"""Stream factory telemetry over a small stdlib-only WebSocket server."""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

try:
    from create_demo_stage import DEFAULT_LAYOUT, load_layout
    from create_layered_stage import DEFAULT_AMR_ROUTES, DEFAULT_SCENARIOS, load_json
except ImportError:
    from scripts.create_demo_stage import DEFAULT_LAYOUT, load_layout
    from scripts.create_layered_stage import DEFAULT_AMR_ROUTES, DEFAULT_SCENARIOS, load_json


GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def scenario_by_id(scenarios: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    for scenario in scenarios["variants"]:
        if scenario["id"] == scenario_id:
            return scenario
    return scenarios["variants"][0]


def sensor_value(sensor: dict[str, Any], scenario: dict[str, Any], tick: int) -> float:
    offset = scenario["sensor_offsets"].get(sensor["id"], 0.0)
    wave = math.sin(tick / 9 + len(sensor["id"])) * sensor["threshold"] * 0.025
    return max(0.0, float(sensor["value"]) + float(offset) + wave)


def interpolate_route(amr_routes: dict[str, Any], tick: int) -> dict[str, Any]:
    robot = amr_routes["robots"][0]
    waypoint_map = {waypoint["id"]: waypoint for waypoint in amr_routes["waypoints"]}
    route = [waypoint_map[waypoint_id] for waypoint_id in robot["route"]]
    segment = (tick // 18) % len(route)
    next_segment = (segment + 1) % len(route)
    progress = (tick % 18) / 18
    start = route[segment]["translation"]
    end = route[next_segment]["translation"]
    position = [round(start[i] + (end[i] - start[i]) * progress, 3) for i in range(3)]
    return {
        "id": robot["id"],
        "position": position,
        "next_waypoint": route[next_segment]["id"],
        "task": route[next_segment]["task"],
        "progress": round(progress, 3),
        "payload_kg": robot["payload_kg"],
    }


def telemetry_payload(
    layout: dict[str, Any],
    scenarios: dict[str, Any],
    amr_routes: dict[str, Any],
    scenario_id: str,
    tick: int,
) -> dict[str, Any]:
    scenario = scenario_by_id(scenarios, scenario_id)
    sensors = []
    for sensor in layout["sensors"]:
        value = sensor_value(sensor, scenario, tick)
        ratio = value / float(sensor["threshold"])
        sensors.append(
            {
                "id": sensor["id"],
                "value": round(value, 3),
                "unit": sensor["unit"],
                "threshold": sensor["threshold"],
                "status": "watch" if ratio >= 0.92 else "nominal",
            }
        )

    base_throughput = layout["equipment"][0]["metrics"]["throughput_per_hour"]
    throughput = base_throughput * scenario["throughput_multiplier"] + math.sin(tick / 7) * 18
    base_oee = sum(item["metrics"].get("oee", 0.88) for item in layout["equipment"]) / len(layout["equipment"])
    oee = min(0.99, max(0.0, base_oee + scenario["oee_delta"] + math.sin(tick / 14) * 0.01))
    equipment = [
        {
            "id": item["id"],
            "status": scenario["equipment_status"].get(item["id"], item.get("status", "nominal")),
        }
        for item in layout["equipment"]
    ]
    alert_load = sum(1 for sensor in sensors if sensor["status"] == "watch") + sum(
        1 for item in equipment if item["status"] in {"watch", "maintenance"}
    )

    return {
        "type": "telemetry",
        "sequence": tick,
        "timestamp": time.time(),
        "scenario": scenario["id"],
        "scenario_label": scenario["label"],
        "kpis": {
            "throughput_per_hour": round(throughput),
            "oee": round(oee, 3),
            "alert_load": alert_load,
        },
        "sensors": sensors,
        "equipment": equipment,
        "amr": interpolate_route(amr_routes, tick),
    }


def encode_frame(payload: str) -> bytes:
    data = payload.encode("utf-8")
    length = len(data)
    if length < 126:
        header = bytes([0x81, length])
    elif length < 65536:
        header = bytes([0x81, 126]) + length.to_bytes(2, "big")
    else:
        header = bytes([0x81, 127]) + length.to_bytes(8, "big")
    return header + data


async def read_http_headers(reader: asyncio.StreamReader) -> dict[str, str]:
    raw = await reader.readuntil(b"\r\n\r\n")
    lines = raw.decode("utf-8", errors="replace").split("\r\n")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.lower()] = value.strip()
    return headers


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    layout: dict[str, Any],
    scenarios: dict[str, Any],
    amr_routes: dict[str, Any],
    scenario_id: str,
    interval: float,
) -> None:
    try:
        headers = await read_http_headers(reader)
        key = headers.get("sec-websocket-key")
        if not key:
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionError, BrokenPipeError):
                pass
            return

        accept = base64.b64encode(hashlib.sha1(f"{key}{GUID}".encode("ascii")).digest()).decode("ascii")
        writer.write(
            (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
            ).encode("ascii")
        )
        await writer.drain()

        tick = 0
        while not writer.is_closing():
            payload = telemetry_payload(layout, scenarios, amr_routes, scenario_id, tick)
            writer.write(encode_frame(json.dumps(payload, separators=(",", ":"))))
            await writer.drain()
            tick += 1
            await asyncio.sleep(interval)
    except (asyncio.IncompleteReadError, ConnectionError, BrokenPipeError):
        pass
    finally:
        if not writer.is_closing():
            writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, BrokenPipeError):
            pass


async def serve(args: argparse.Namespace) -> None:
    layout = load_layout(args.layout)
    scenarios = load_json(args.scenarios)
    amr_routes = load_json(args.amr_routes)
    server = await asyncio.start_server(
        lambda reader, writer: handle_client(
            reader,
            writer,
            layout,
            scenarios,
            amr_routes,
            args.scenario,
            args.interval,
        ),
        args.host,
        args.port,
    )
    print(f"Telemetry WebSocket listening on ws://{args.host}:{args.port}/ws")
    print(f"Scenario: {args.scenario}")
    async with server:
        await server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream factory telemetry over WebSocket.")
    parser.add_argument("--layout", type=Path, default=DEFAULT_LAYOUT, help="Factory layout JSON.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS, help="Scenario variants JSON.")
    parser.add_argument("--amr-routes", type=Path, default=DEFAULT_AMR_ROUTES, help="AMR route JSON.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind.")
    parser.add_argument("--scenario", default="peak_hour", help="Scenario id to stream.")
    parser.add_argument("--interval", type=float, default=0.75, help="Seconds between telemetry frames.")
    return parser.parse_args()


def main() -> None:
    try:
        asyncio.run(serve(parse_args()))
    except KeyboardInterrupt:
        print("\nTelemetry server stopped.")


if __name__ == "__main__":
    main()
