const FALLBACK_LAYOUT = {
  project: "omniverse-ops-starter",
  title: "Omniverse Ops Starter Factory Twin",
  description: "A compact factory digital twin scene for NVIDIA Omniverse and OpenUSD workflows.",
  units: { meters_per_unit: 1, up_axis: "Z" },
  equipment: [
    {
      id: "Conveyor_A",
      kind: "cube",
      role: "inbound conveyor",
      status: "running",
      translation: [-2.7, 0.0, 0.38],
      scale: [1.9, 0.32, 0.28],
      color: [0.1, 0.35, 0.85],
      metrics: { throughput_per_hour: 920, oee: 0.87 },
    },
    {
      id: "Robot_Cell_B",
      kind: "cube",
      role: "pick and place cell",
      status: "ready",
      translation: [1.35, 0.55, 0.72],
      scale: [0.72, 0.72, 0.72],
      color: [0.85, 0.35, 0.1],
      metrics: { cycle_time_seconds: 8.4, oee: 0.91 },
    },
    {
      id: "Inspection_C",
      kind: "cube",
      role: "vision quality gate",
      status: "watch",
      translation: [3.2, -0.1, 0.52],
      scale: [0.62, 0.48, 0.52],
      color: [0.22, 0.62, 0.44],
      metrics: { pass_rate: 0.982, alerts: 1 },
    },
  ],
  sensors: [
    {
      id: "Temperature_01",
      kind: "sphere",
      role: "temperature",
      unit: "C",
      value: 37.4,
      threshold: 45,
      translation: [-3.15, -0.78, 1.16],
      scale: [0.15, 0.15, 0.15],
      color: [0.95, 0.15, 0.2],
    },
    {
      id: "Pressure_01",
      kind: "sphere",
      role: "air pressure",
      unit: "bar",
      value: 5.8,
      threshold: 6.2,
      translation: [0.0, 1.05, 1.08],
      scale: [0.15, 0.15, 0.15],
      color: [0.15, 0.8, 0.35],
    },
    {
      id: "Vibration_01",
      kind: "sphere",
      role: "vibration",
      unit: "mm/s",
      value: 2.1,
      threshold: 4.5,
      translation: [2.45, -0.78, 1.25],
      scale: [0.15, 0.15, 0.15],
      color: [0.95, 0.78, 0.12],
    },
  ],
  safety_zones: [
    {
      id: "Robot_Cell_Safety",
      translation: [1.35, 0.55, 0.04],
      scale: [1.25, 1.05, 0.035],
      color: [0.95, 0.78, 0.12],
      opacity: 0.32,
    },
    {
      id: "Forklift_Lane",
      translation: [0.0, -1.55, 0.035],
      scale: [4.6, 0.22, 0.025],
      color: [0.15, 0.62, 0.95],
      opacity: 0.28,
    },
  ],
  flow_markers: [
    { id: "Inbound", translation: [-3.9, 0.0, 0.18], scale: [0.16, 0.16, 0.16], color: [0.1, 0.35, 0.85] },
    { id: "Robot_Handoff", translation: [-0.55, 0.0, 0.18], scale: [0.16, 0.16, 0.16], color: [0.85, 0.35, 0.1] },
    { id: "Inspection", translation: [2.4, -0.08, 0.18], scale: [0.16, 0.16, 0.16], color: [0.22, 0.62, 0.44] },
    { id: "Outbound", translation: [4.05, -0.08, 0.18], scale: [0.16, 0.16, 0.16], color: [0.95, 0.78, 0.12] },
  ],
};

const FALLBACK_SCENARIOS = {
  default: "baseline",
  variants: [
    {
      id: "baseline",
      label: "Baseline",
      description: "Normal factory operations.",
      throughput_multiplier: 1,
      oee_delta: 0,
      sensor_offsets: { Temperature_01: 0, Pressure_01: 0, Vibration_01: 0 },
      equipment_status: { Conveyor_A: "running", Robot_Cell_B: "ready", Inspection_C: "watch" },
    },
    {
      id: "peak_hour",
      label: "Peak Hour",
      description: "Higher inbound volume pushes pressure close to the threshold.",
      throughput_multiplier: 1.18,
      oee_delta: -0.03,
      sensor_offsets: { Temperature_01: 2.6, Pressure_01: 0.38, Vibration_01: 0.24 },
      equipment_status: { Conveyor_A: "running", Robot_Cell_B: "busy", Inspection_C: "watch" },
    },
    {
      id: "maintenance",
      label: "Maintenance",
      description: "Robot cell is isolated while AMR uses a bypass path.",
      throughput_multiplier: 0.62,
      oee_delta: -0.16,
      sensor_offsets: { Temperature_01: -1.2, Pressure_01: -0.5, Vibration_01: 0.12 },
      equipment_status: { Conveyor_A: "running", Robot_Cell_B: "maintenance", Inspection_C: "ready" },
    },
  ],
};

const FALLBACK_AMR_ROUTES = {
  robots: [
    {
      id: "AMR_01",
      role: "line-side material runner",
      base_pose: [-3.8, -1.42, 0.16],
      scale: [0.36, 0.24, 0.12],
      color: [0.18, 0.2, 0.24],
      payload_kg: 35,
      max_speed_mps: 1.1,
      route: ["Dock_Inbound", "Conveyor_Drop", "Inspection_Pickup", "Dock_Outbound"],
    },
  ],
  waypoints: [
    { id: "Dock_Inbound", translation: [-3.8, -1.42, 0.12], task: "load empty bin" },
    { id: "Conveyor_Drop", translation: [-1.35, -1.42, 0.12], task: "drop bin near inbound conveyor" },
    { id: "Inspection_Pickup", translation: [2.55, -1.42, 0.12], task: "pick inspected output" },
    { id: "Dock_Outbound", translation: [4.05, -1.42, 0.12], task: "stage outbound bin" },
  ],
  safety: { avoid_zones: ["Robot_Cell_Safety"], preferred_lane: "Forklift_Lane", min_clearance_m: 0.45 },
};

const state = {
  layout: FALLBACK_LAYOUT,
  scenarios: FALLBACK_SCENARIOS,
  amrRoutes: FALLBACK_AMR_ROUTES,
  telemetry: null,
  telemetryConnected: false,
  selected: null,
  running: true,
  tick: 0,
  speed: 2,
  scenario: "baseline",
  layers: {
    equipment: true,
    sensors: true,
    zones: true,
    flow: true,
    robots: true,
  },
  hitTargets: [],
  throughputHistory: Array.from({ length: 24 }, (_, index) => 860 + Math.round(Math.sin(index / 2) * 48)),
};

const canvas = document.querySelector("#factory-canvas");
const ctx = canvas.getContext("2d");
const kpiGrid = document.querySelector("#kpi-grid");
const sensorList = document.querySelector("#sensor-list");
const assetName = document.querySelector("#asset-name");
const assetRole = document.querySelector("#asset-role");
const assetStatus = document.querySelector("#asset-status");
const assetMetrics = document.querySelector("#asset-metrics");
const sparkline = document.querySelector("#sparkline");
const throughputValue = document.querySelector("#throughput-value");
const alertLoad = document.querySelector("#alert-load");
const primCount = document.querySelector("#prim-count");
const toggleSim = document.querySelector("#toggle-sim");
const toggleIcon = document.querySelector("#toggle-icon");
const speedRange = document.querySelector("#speed-range");
const liveStatus = document.querySelector("#live-status");
const scenarioGrid = document.querySelector("#scenario-grid");
const amrName = document.querySelector("#amr-name");
const amrTask = document.querySelector("#amr-task");
const amrProgress = document.querySelector("#amr-progress");
const amrPosition = document.querySelector("#amr-position");

function usdColor(rgb, alpha = 1) {
  const [r, g, b] = rgb.map((value) => Math.round(value * 255));
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function mapPoint([x, y]) {
  const bounds = { left: -4.8, right: 4.8, top: 2.25, bottom: -2.15 };
  const padding = Math.min(canvas.width, canvas.height) * 0.09;
  const usableWidth = canvas.width - padding * 2;
  const usableHeight = canvas.height - padding * 2;
  return {
    x: padding + ((x - bounds.left) / (bounds.right - bounds.left)) * usableWidth,
    y: padding + ((bounds.top - y) / (bounds.top - bounds.bottom)) * usableHeight,
  };
}

function assetKind(asset) {
  if (state.layout.equipment.includes(asset)) return "equipment";
  if (state.layout.sensors.includes(asset)) return "sensor";
  if (state.layout.safety_zones.includes(asset)) return "zone";
  if (state.amrRoutes.robots.includes(asset)) return "robot";
  if (state.amrRoutes.waypoints.includes(asset)) return "waypoint";
  return "flow";
}

function activeScenario() {
  return (
    state.scenarios.variants.find((scenario) => scenario.id === state.scenario) ||
    state.scenarios.variants.find((scenario) => scenario.id === state.scenarios.default) ||
    state.scenarios.variants[0]
  );
}

function telemetrySensor(sensorId) {
  return state.telemetry?.sensors?.find((sensor) => sensor.id === sensorId);
}

function telemetryEquipment(equipmentId) {
  return state.telemetry?.equipment?.find((item) => item.id === equipmentId);
}

function scenarioSensorValue(sensor) {
  const liveSensor = telemetrySensor(sensor.id);
  if (liveSensor) return liveSensor.value;
  const scenario = activeScenario();
  const scenarioOffset = scenario?.sensor_offsets?.[sensor.id] || 0;
  const wave = Math.sin(state.tick / 18 + sensor.id.length) * 0.08;
  return sensor.value * (1 + wave) + scenarioOffset;
}

function statusFor(asset) {
  const liveSensor = telemetrySensor(asset.id);
  if (liveSensor) return liveSensor.status;
  const liveEquipment = telemetryEquipment(asset.id);
  if (liveEquipment) return liveEquipment.status;
  if (assetKind(asset) === "equipment") {
    return activeScenario()?.equipment_status?.[asset.id] || asset.status || "nominal";
  }
  if (assetKind(asset) === "sensor") {
    return scenarioSensorValue(asset) / asset.threshold >= 0.92 ? "watch" : "nominal";
  }
  return asset.status || "nominal";
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const pixelRatio = window.devicePixelRatio || 1;
  canvas.width = Math.max(640, Math.floor(rect.width * pixelRatio));
  canvas.height = Math.max(420, Math.floor(rect.height * pixelRatio));
  ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  draw();
}

function drawFloor() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const origin = mapPoint([-4.4, 1.7]);
  const end = mapPoint([4.4, -1.8]);
  ctx.fillStyle = "#fbfaf6";
  ctx.strokeStyle = "#cfc8bd";
  ctx.lineWidth = 1.5;
  roundedRect(origin.x, origin.y, end.x - origin.x, end.y - origin.y, 8);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = "rgba(32, 35, 38, 0.48)";
  ctx.font = "700 12px Inter, sans-serif";
  ctx.fillText("Factory Floor /World", 22, height - 22);
  ctx.fillText("OpenUSD meters, Z-up", width - 154, height - 22);
}

function roundedRect(x, y, width, height, radius) {
  const r = Math.min(radius, Math.abs(width) / 2, Math.abs(height) / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + width, y, x + width, y + height, r);
  ctx.arcTo(x + width, y + height, x, y + height, r);
  ctx.arcTo(x, y + height, x, y, r);
  ctx.arcTo(x, y, x + width, y, r);
  ctx.closePath();
}

function drawZone(zone) {
  const center = mapPoint(zone.translation);
  const scale = zone.scale;
  const width = scale[0] * 92;
  const height = scale[1] * 92;
  ctx.fillStyle = usdColor(zone.color, zone.opacity || 0.3);
  ctx.strokeStyle = usdColor(zone.color, 0.65);
  ctx.lineWidth = 2;
  roundedRect(center.x - width / 2, center.y - height / 2, width, height, 8);
  ctx.fill();
  ctx.stroke();
}

function drawEquipment(asset) {
  const center = mapPoint(asset.translation);
  const scale = asset.scale;
  const width = Math.max(88, scale[0] * 90);
  const height = Math.max(46, scale[1] * 150);
  const selected = state.selected?.id === asset.id;
  ctx.save();
  ctx.translate(center.x, center.y);
  ctx.fillStyle = usdColor(asset.color, 0.92);
  ctx.strokeStyle = selected ? "#202326" : "rgba(32, 35, 38, 0.28)";
  ctx.lineWidth = selected ? 4 : 1.5;
  roundedRect(-width / 2, -height / 2, width, height, 8);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#fffdf9";
  ctx.font = "800 11px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(asset.id.replaceAll("_", " "), 0, 4);
  ctx.restore();
  state.hitTargets.push({ asset, x: center.x - width / 2, y: center.y - height / 2, width, height });
}

function drawSensor(sensor) {
  const center = mapPoint(sensor.translation);
  const value = scenarioSensorValue(sensor);
  const ratio = Math.min(value / sensor.threshold, 1.28);
  const radius = 11 + Math.sin(state.tick / 6) * 1.5;
  const warn = ratio >= 0.92;
  ctx.beginPath();
  ctx.fillStyle = usdColor(sensor.color, warn ? 0.95 : 0.82);
  ctx.strokeStyle = warn ? "#d89412" : "rgba(32, 35, 38, 0.35)";
  ctx.lineWidth = warn ? 4 : 2;
  ctx.arc(center.x, center.y, radius, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.strokeStyle = warn ? "rgba(216, 148, 18, 0.3)" : usdColor(sensor.color, 0.2);
  ctx.lineWidth = 2;
  ctx.arc(center.x, center.y, radius + 10 + ratio * 8, 0, Math.PI * 2);
  ctx.stroke();
  state.hitTargets.push({ asset: sensor, x: center.x - 24, y: center.y - 24, width: 48, height: 48 });
}

function drawFlowMarkers() {
  const markers = state.layout.flow_markers;
  ctx.strokeStyle = "rgba(32, 35, 38, 0.35)";
  ctx.lineWidth = 2;
  ctx.setLineDash([8, 8]);
  ctx.beginPath();
  markers.forEach((marker, index) => {
    const point = mapPoint(marker.translation);
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.stroke();
  ctx.setLineDash([]);

  markers.forEach((marker, index) => {
    const point = mapPoint(marker.translation);
    const pulse = index === Math.floor((state.tick / 16) % markers.length);
    ctx.beginPath();
    ctx.fillStyle = usdColor(marker.color, 0.94);
    ctx.arc(point.x, point.y, pulse ? 13 : 9, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#202326";
    ctx.font = "800 11px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(String(index + 1), point.x, point.y + 4);
    state.hitTargets.push({ asset: marker, x: point.x - 18, y: point.y - 18, width: 36, height: 36 });
  });
}

function currentAmrState() {
  if (state.telemetry?.amr) return state.telemetry.amr;
  const robot = state.amrRoutes.robots[0];
  if (!robot) return null;
  const waypointMap = Object.fromEntries(state.amrRoutes.waypoints.map((waypoint) => [waypoint.id, waypoint]));
  const route = robot.route.map((waypointId) => waypointMap[waypointId]).filter(Boolean);
  if (!route.length) return null;
  const segment = Math.floor(state.tick / 32) % route.length;
  const nextSegment = (segment + 1) % route.length;
  const progress = (state.tick % 32) / 32;
  const start = route[segment].translation;
  const end = route[nextSegment].translation;
  const position = start.map((value, index) => value + (end[index] - value) * progress);
  return {
    id: robot.id,
    position,
    next_waypoint: route[nextSegment].id,
    task: route[nextSegment].task,
    progress,
    payload_kg: robot.payload_kg,
  };
}

function drawRobots() {
  const route = state.amrRoutes.waypoints || [];
  ctx.strokeStyle = "rgba(32, 35, 38, 0.55)";
  ctx.lineWidth = 3;
  ctx.setLineDash([12, 8]);
  ctx.beginPath();
  route.forEach((waypoint, index) => {
    const point = mapPoint(waypoint.translation);
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.stroke();
  ctx.setLineDash([]);

  route.forEach((waypoint) => {
    const point = mapPoint(waypoint.translation);
    ctx.beginPath();
    ctx.fillStyle = "#202326";
    ctx.strokeStyle = "rgba(255, 253, 249, 0.9)";
    ctx.lineWidth = 3;
    ctx.arc(point.x, point.y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    state.hitTargets.push({ asset: waypoint, x: point.x - 16, y: point.y - 16, width: 32, height: 32 });
  });

  const amr = currentAmrState();
  const robot = state.amrRoutes.robots[0];
  if (!amr || !robot) return;
  const point = mapPoint(amr.position);
  ctx.save();
  ctx.translate(point.x, point.y);
  ctx.fillStyle = usdColor(robot.color, 0.95);
  ctx.strokeStyle = "#fffdf9";
  ctx.lineWidth = 3;
  roundedRect(-24, -15, 48, 30, 8);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#fffdf9";
  ctx.font = "900 10px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("AMR", 0, 4);
  ctx.restore();
  state.hitTargets.push({ asset: robot, x: point.x - 28, y: point.y - 20, width: 56, height: 40 });
}

function draw() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);
  state.hitTargets = [];
  drawFloor();
  if (state.layers.zones) state.layout.safety_zones.forEach(drawZone);
  if (state.layers.flow) drawFlowMarkers();
  if (state.layers.equipment) state.layout.equipment.forEach(drawEquipment);
  if (state.layers.sensors) state.layout.sensors.forEach(drawSensor);
  if (state.layers.robots) drawRobots();
}

function metricPairs(asset) {
  if (assetKind(asset) === "sensor") {
    const value = scenarioSensorValue(asset);
    return [
      ["Value", `${value.toFixed(value < 10 ? 2 : 1)} ${asset.unit}`],
      ["Threshold", `${asset.threshold} ${asset.unit}`],
      ["USD path", `/World/Sensors/${asset.id}`],
    ];
  }
  if (assetKind(asset) === "zone") {
    return [
      ["Opacity", `${Math.round((asset.opacity || 0) * 100)}%`],
      ["Footprint", `${asset.scale[0]}m x ${asset.scale[1]}m`],
      ["USD path", `/World/SafetyZones/${asset.id}`],
    ];
  }
  if (assetKind(asset) === "flow") {
    return [
      ["Station", asset.id.replaceAll("_", " ")],
      ["Position", `${asset.translation[0]}m, ${asset.translation[1]}m`],
      ["USD path", `/World/FlowMarkers/${asset.id}`],
    ];
  }
  if (assetKind(asset) === "waypoint") {
    return [
      ["Task", asset.task],
      ["Position", `${asset.translation[0]}m, ${asset.translation[1]}m`],
      ["USD path", `/World/AMRRoute/${asset.id}`],
    ];
  }
  if (assetKind(asset) === "robot") {
    const amr = currentAmrState();
    return [
      ["Payload", `${asset.payload_kg} kg`],
      ["Max speed", `${asset.max_speed_mps} m/s`],
      ["Next waypoint", amr?.next_waypoint || asset.route[0]],
      ["USD path", `/World/Robots/${asset.id}`],
    ];
  }
  const metrics = Object.entries(asset.metrics || {}).map(([key, value]) => [
    key.replaceAll("_", " "),
    typeof value === "number" && value < 1 ? `${Math.round(value * 100)}%` : String(value),
  ]);
  return [...metrics, ["USD path", `/World/Equipment/${asset.id}`]];
}

function selectAsset(asset) {
  state.selected = asset;
  assetName.textContent = asset.id || "Factory Floor";
  assetRole.textContent = asset.role || assetKind(asset);
  const status = statusFor(asset);
  assetStatus.textContent = status;
  assetStatus.classList.toggle("warn", status === "watch");
  assetMetrics.innerHTML = "";
  metricPairs(asset).forEach(([label, value]) => {
    const row = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = value;
    row.append(dt, dd);
    assetMetrics.append(row);
  });
  draw();
}

function renderKpis() {
  const sensors = state.layout.sensors;
  const warningCount = sensors.filter((sensor) => scenarioSensorValue(sensor) / sensor.threshold >= 0.92).length;
  const baseOee =
    state.layout.equipment.reduce((sum, item) => sum + (item.metrics?.oee || 0.88), 0) / state.layout.equipment.length;
  const scenarioOee = Math.min(0.99, Math.max(0, baseOee + (activeScenario()?.oee_delta || 0)));
  const oee = state.telemetry?.kpis?.oee || scenarioOee;
  const throughput = currentThroughput();
  const kpis = [
    ["OEE", `${Math.round(oee * 100)}%`, state.telemetryConnected ? "live feed" : "scenario"],
    ["Throughput", `${throughput}/hr`, "live takt"],
    ["Sensors", String(sensors.length), `${warningCount} watch`],
    ["AMR", state.amrRoutes.robots[0]?.id || "1", currentAmrState()?.next_waypoint || "route"],
  ];
  kpiGrid.innerHTML = "";
  kpis.forEach(([label, value, sub]) => {
    const node = document.createElement("div");
    node.className = "kpi";
    node.innerHTML = `<span>${label}</span><strong>${value}</strong><em>${sub}</em>`;
    kpiGrid.append(node);
  });
  alertLoad.textContent = String(
    state.telemetry?.kpis?.alert_load ??
      warningCount + state.layout.equipment.filter((item) => statusFor(item) === "watch").length,
  );
  throughputValue.textContent = `${throughput}/hr`;
}

function renderSensors() {
  sensorList.innerHTML = "";
  state.layout.sensors.forEach((sensor) => {
    const value = scenarioSensorValue(sensor);
    const row = document.createElement("div");
    row.className = "sensor-row";
    const warn = value / sensor.threshold >= 0.92;
    row.innerHTML = `
      <button type="button" aria-label="Inspect ${sensor.id}">
        <span>${sensor.id.replaceAll("_", " ")}</span>
        <strong class="${warn ? "sensor-warn" : ""}">${value.toFixed(value < 10 ? 2 : 1)} ${sensor.unit}</strong>
      </button>
    `;
    row.querySelector("button").addEventListener("click", () => selectAsset(sensor));
    sensorList.append(row);
  });
}

function renderSparkline() {
  sparkline.innerHTML = "";
  const max = Math.max(...state.throughputHistory);
  const min = Math.min(...state.throughputHistory);
  state.throughputHistory.forEach((value) => {
    const bar = document.createElement("i");
    const height = 18 + ((value - min) / Math.max(1, max - min)) * 30;
    bar.style.height = `${height}px`;
    sparkline.append(bar);
  });
}

function renderAmrMission() {
  const robot = state.amrRoutes.robots[0];
  const amr = currentAmrState();
  if (!robot || !amr) return;
  amrName.textContent = robot.id;
  amrTask.textContent = `${amr.task} -> ${amr.next_waypoint}`;
  amrProgress.style.width = `${Math.round((amr.progress || 0) * 100)}%`;
  amrPosition.textContent = `x ${amr.position[0].toFixed(2)} / y ${amr.position[1].toFixed(2)} / payload ${amr.payload_kg} kg`;
}

function renderScenarios() {
  scenarioGrid.innerHTML = "";
  state.scenarios.variants.forEach((scenario) => {
    const button = document.createElement("button");
    button.className = `scenario${scenario.id === state.scenario ? " active" : ""}`;
    button.dataset.scenario = scenario.id;
    button.type = "button";
    const effect =
      scenario.throughput_multiplier === 1
        ? `${Math.round((1 + scenario.oee_delta) * 87)}%`
        : `${Math.round((scenario.throughput_multiplier - 1) * 100)}%`;
    button.innerHTML = `<span>${scenario.label}</span><strong>${effect}</strong>`;
    button.addEventListener("click", () => {
      document.querySelectorAll(".scenario").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      state.scenario = scenario.id;
      state.telemetry = null;
      renderAll();
    });
    scenarioGrid.append(button);
  });
}

function currentThroughput() {
  if (state.telemetry?.kpis?.throughput_per_hour) return state.telemetry.kpis.throughput_per_hour;
  const base = state.layout.equipment[0]?.metrics?.throughput_per_hour || 900;
  const multiplier = activeScenario()?.throughput_multiplier || 1;
  return Math.round((base + Math.sin(state.tick / 20) * 35) * multiplier);
}

function renderAll() {
  primCount.textContent = String(
    7 +
      4 +
      state.layout.equipment.length +
      state.layout.sensors.length +
      state.layout.safety_zones.length +
      state.layout.flow_markers.length +
      2 +
      state.amrRoutes.robots.length +
      state.amrRoutes.waypoints.length +
      1,
  );
  renderKpis();
  renderSensors();
  renderSparkline();
  renderAmrMission();
  selectAsset(state.selected || state.layout.equipment[0]);
}

function updateLoop() {
  if (state.running) {
    state.tick += state.speed;
    if (state.tick % 12 < state.speed) {
      state.throughputHistory.push(currentThroughput());
      state.throughputHistory = state.throughputHistory.slice(-24);
      renderKpis();
      renderSensors();
      renderSparkline();
      renderAmrMission();
      if (state.selected) selectAsset(state.selected);
    }
    draw();
  }
  requestAnimationFrame(updateLoop);
}

function bindControls() {
  toggleSim.addEventListener("click", () => {
    state.running = !state.running;
    toggleIcon.textContent = state.running ? "||" : ">";
    toggleSim.setAttribute("aria-label", state.running ? "Pause simulation" : "Resume simulation");
  });

  document.querySelector("#focus-alerts").addEventListener("click", () => {
    const alertSensor = state.layout.sensors.find((sensor) => scenarioSensorValue(sensor) / sensor.threshold >= 0.92);
    selectAsset(alertSensor || state.layout.equipment.find((item) => item.status === "watch") || state.layout.sensors[0]);
  });

  speedRange.addEventListener("input", (event) => {
    state.speed = Number(event.target.value);
  });

  document.querySelectorAll(".toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const layer = button.dataset.layer;
      state.layers[layer] = !state.layers[layer];
      button.classList.toggle("active", state.layers[layer]);
      draw();
    });
  });

  canvas.addEventListener("click", (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const target = [...state.hitTargets]
      .reverse()
      .find((item) => x >= item.x && x <= item.x + item.width && y >= item.y && y <= item.y + item.height);
    if (target) selectAsset(target.asset);
  });

  window.addEventListener("resize", resizeCanvas);
}

async function loadJson(path, fallback) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    if (response.ok) {
      return await response.json();
    }
  } catch {
  }
  return fallback;
}

function setTelemetryStatus(connected) {
  state.telemetryConnected = connected;
  liveStatus.classList.toggle("connected", connected);
  liveStatus.querySelector("strong").textContent = connected ? "Live WS" : "Local sim";
}

function telemetryUrl() {
  if (location.protocol === "http:" || location.protocol === "https:") {
    return `ws://${location.hostname || "127.0.0.1"}:8766/ws`;
  }
  return "ws://127.0.0.1:8766/ws";
}

function connectTelemetry() {
  let socket;
  try {
    socket = new WebSocket(telemetryUrl());
  } catch {
    setTelemetryStatus(false);
    return;
  }

  socket.addEventListener("open", () => setTelemetryStatus(true));
  socket.addEventListener("message", (event) => {
    const payload = JSON.parse(event.data);
    if (payload.type !== "telemetry") return;
    state.telemetry = payload;
    state.scenario = payload.scenario || state.scenario;
    state.tick = payload.sequence || state.tick;
    state.throughputHistory.push(payload.kpis.throughput_per_hour);
    state.throughputHistory = state.throughputHistory.slice(-24);
    renderScenarios();
    renderKpis();
    renderSensors();
    renderSparkline();
    renderAmrMission();
    if (state.selected) selectAsset(state.selected);
    draw();
  });
  socket.addEventListener("close", () => {
    setTelemetryStatus(false);
    state.telemetry = null;
    setTimeout(connectTelemetry, 2400);
  });
  socket.addEventListener("error", () => {
    setTelemetryStatus(false);
  });
}

async function init() {
  state.layout = await loadJson("../data/factory_layout.json", FALLBACK_LAYOUT);
  state.scenarios = await loadJson("../data/ops_scenarios.json", FALLBACK_SCENARIOS);
  state.amrRoutes = await loadJson("../data/amr_routes.json", FALLBACK_AMR_ROUTES);
  state.scenario = state.scenarios.default || state.scenario;
  bindControls();
  resizeCanvas();
  renderScenarios();
  renderAll();
  connectTelemetry();
  updateLoop();
}

init();
