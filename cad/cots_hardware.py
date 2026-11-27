"""
KRON-01V6 (ESP32-S3-CAM N16R8 Edition, v2.0.0) — Real COTS Hardware CAD Library
===============================================================================
Datasheet-accurate multi-body B-Rep CAD library matching the user's exact purchased kit:
  - ESP32-S3-CAM N16R8 (58.0×27.94mm PCB + 6.04mm Wi-Fi antenna = 64.04mm, dual Type-C,
    ESP32-S3-WROOM-1 RF shield, 24-pin FPC camera socket, downward 2×22P gold headers)
  - OV3660 Short-Ribbon Camera Module (8.5×8.5×6.0mm lens head + ~20mm FPC ribbon)
  - GMT020-02 2.0" IPS SPI TFT LCD (62.0×37.5×3.4mm, 8-pin header, glowing cyan eyes)
  - Dual-18650 Parallel Type-C Power Board (85.0×44.0×23.0mm, 2× EVE 18650-2500mAh cells,
    3× 2×6P header banks, right-edge Type-C VIN + ON/OFF slide switch + 4× battery LEDs)
  - PCA9685A 16-Channel I2C PWM Driver (62.0×25.0mm blue PCB, 16×3P headers + 6P I2C)
  - 2× DRV8833 Red Motor Drivers (21.0×18.0mm each, pre-soldered straight headers)
  - 4× GA12-N20 Pre-Wired Motors + 4× Complete Ø43×18mm D-Shaft Rubber Wheels
  - 3020 Cavity Speaker (30.0×20.0×7.0mm), MAX98357A Purple I2S Amp, INMP441 MEMS Mic
  - MG90S 180° Metal-Gear Servo, 7-Wire Neck DuPont Ribbon & Unified M3 Captive Nut Kit
"""

from pathlib import Path
import math
from build123d import (
    Align,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Circle,
    Color,
    Compound,
    Cylinder,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    RegularPolygon,
    Spline,
    extrude,
    import_step,
    sweep,
)
import config as C

EXTERNAL_STEP_DIR = Path(__file__).parent / "external_step"

WIRE_COLORS = {
    "wire_red":    (0.92, 0.16, 0.16, 1.0),
    "wire_black":  (0.12, 0.13, 0.15, 1.0),
    "wire_yellow": (0.96, 0.80, 0.12, 1.0),
    "wire_blue":   (0.16, 0.52, 0.96, 1.0),
    "wire_green":  (0.16, 0.78, 0.34, 1.0),
    "wire_orange": (0.98, 0.52, 0.10, 1.0),
    "wire_purple": (0.68, 0.30, 0.92, 1.0),
    "wire_white":  (0.90, 0.92, 0.95, 1.0),
    "wire_brown":  (0.48, 0.28, 0.14, 1.0),
    "fpc_copper":  (0.84, 0.44, 0.12, 1.0),
    "rgb_green":   (0.10, 0.95, 0.45, 1.0),
}


def _col(name: str) -> Color:
    rgba = C.COLORS.get(name) or WIRE_COLORS[name]
    return Color(rgba[0], rgba[1], rgba[2], rgba[3])


def _tag(shape, label: str, color_key: str):
    shape.label = label
    shape.color = _col(color_key)
    return shape


def load_or_build(part_key: str, builder_fn):
    ext_path = EXTERNAL_STEP_DIR / f"{part_key}.step"
    if ext_path.exists():
        imported = import_step(str(ext_path))
        imported.label = f"{part_key}_imported"
        return imported
    return builder_fn()


def _make_cable(points: list, radius: float, label: str, color_key: str):
    with BuildPart() as cable:
        with BuildLine() as path:
            Spline(points)
        with BuildSketch(Plane(origin=path.line @ 0, z_dir=path.line % 0)):
            Circle(radius=radius)
        sweep()
    return _tag(cable.part, label, color_key)


def _make_flat_ribbon(points: list, width: float, thickness: float, label: str, color_key: str):
    with BuildPart() as rib:
        with BuildLine() as path:
            Spline(points)
        with BuildSketch(Plane(origin=path.line @ 0, z_dir=path.line % 0)):
            Rectangle(width, thickness)
        sweep()
    return _tag(rib.part, label, color_key)


# ---------------------------------------------------------------------------
# Fasteners (Unified DIN 912 M3 Socket Cap Screws & DIN 934 M3 Captive Nuts)
# ---------------------------------------------------------------------------
def build_din912_screw(dia: float = 3.0, length: float = 10.0, label: str = "M3x10_DIN912") -> Compound:
    head_d = 5.5
    head_h = 3.0
    hex_r = 2.5 / math.sqrt(3.0)
    with BuildPart() as head:
        Cylinder(radius=head_d / 2.0, height=head_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildSketch(Plane.XY.offset(head_h)):
            RegularPolygon(radius=hex_r, side_count=6)
        extrude(amount=-head_h * 0.65, mode=Mode.SUBTRACT)
    shank = Cylinder(radius=dia / 2.0, height=length, align=(Align.CENTER, Align.CENTER, Align.MAX))
    body = head.part + shank
    _tag(body, label, "black_oxide")
    return Compound(label=label, children=[body])


def build_hex_nut(across_flats: float = 5.5, thickness: float = 2.4, bore_dia: float = 3.0, label: str = "Nut_M3"):
    with BuildPart() as nut:
        with BuildSketch(Plane.XY):
            RegularPolygon(radius=across_flats / math.sqrt(3.0), side_count=6)
        extrude(amount=thickness)
        Cylinder(radius=bore_dia / 2.0, height=thickness + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    return _tag(nut.part, label, "metal_silver")


# ---------------------------------------------------------------------------
# 1. SF-ESP32-S3-CAM WROOM V1.0.0 (58×27.94mm PCB + 6.04mm Ant + 1.8mm Type-C = 65.84mm)
# ---------------------------------------------------------------------------
def build_esp32_s3_cam() -> Compound:
    """
    Exact SF-ESP32-S3-CAM WROOM V1.0.0 mounted VERTICALLY facing +Y (from user photo):
      - Main PCB: 58.0(X) × 1.6(Y) × 27.94(Z) mm
      - Protruding PCB Wi-Fi Antenna on +X end (+6.04mm)
      - Dual protruding Type-C ports (COM & USB) on -X end (+1.80mm overhang past PCB!)
      - ESP32-S3-WROOM-1 RF shield & center 24-pin OV3660 FPC socket on front (+Y) face!
      - TF card slot + pre-soldered 2×22P headers pointing BACKWARD (-Y) for easy plug-in!
    """
    parts = []
    # Total X span = 65.84mm (-32.92..+32.92): Type-C overhang -32.92..-31.12, PCB -31.12..+26.88, Ant +26.88..+32.92
    x_pcb_ctr = (C.S3_USBC_PROTRUDE - C.S3_ANT_L) / 2.0  # -2.12 mm
    pcb = Location((x_pcb_ctr, 0, 0)) * Box(C.S3_PCB_L, C.S3_PCB_T, C.S3_PCB_W, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(pcb, "S3CAM_PCB", "pcb_dark"))

    ant = Location((C.S3_TOTAL_L / 2.0 - C.S3_ANT_L / 2.0, 0.2, 0)) * Box(
        C.S3_ANT_L, 1.2, 18.0, align=(Align.CENTER, Align.MIN, Align.CENTER)
    )
    parts.append(_tag(ant, "S3CAM_WiFi_Antenna", "pcb_dark"))

    # ESP32-S3-WROOM-1 RF Metal Shield on +X/+Y front face (18 × 3.2 × 18 mm)
    shield = Location((17.0, C.S3_PCB_T, 0)) * Box(18.0, 3.2, 18.0, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(shield, "S3CAM_WROOM_Shield", "metal_silver"))

    # Dual protruding Type-C ports on -X end (overhang 1.8mm past PCB edge!)
    for sz, pname in ((-5.3, "USB"), (5.3, "COM")):
        usbc = Location((-C.S3_TOTAL_L / 2.0 + 3.6, C.S3_PCB_T, sz)) * Box(
            7.2, 3.2, 8.9, align=(Align.CENTER, Align.MIN, Align.CENTER)
        )
        parts.append(_tag(usbc, f"S3CAM_TypeC_{pname}", "metal_silver"))

    # Center 24-Pin OV3660 FPC Socket on front (+Y) face — directly faces OV3660 lens just 13.9mm away!
    fpc_sock = Location((0.5, C.S3_PCB_T, 0.0)) * Box(
        5.2, 2.2, 17.5, align=(Align.CENTER, Align.MIN, Align.CENTER)
    )
    parts.append(_tag(fpc_sock, "S3CAM_FPC24_Socket", "white"))

    # Rear TF Card Slot on -Y back face (behind WROOM shield)
    tf = Location((17.0, -2.0, 0.0)) * Box(14.5, 2.0, 15.0, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(tf, "S3CAM_TF_Slot", "metal_silver"))

    # Pre-soldered 2×22P headers pointing BACKWARD (-Y) at Z = ±12.7mm (25.4mm pitch!)
    for sz in (-12.7, 12.7):
        base = Location((x_pcb_ctr, -2.5, sz)) * Box(55.88, 2.5, 2.54, align=(Align.CENTER, Align.MIN, Align.CENTER))
        pins = Location((x_pcb_ctr, -8.5, sz)) * Box(54.5, 6.0, 0.7, align=(Align.CENTER, Align.MIN, Align.CENTER))
        parts.append(_tag(base, "S3CAM_Hdr_Base", "black_oxide"))
        parts.append(_tag(pins, "S3CAM_Hdr_Pins", "gold"))

    comp = Compound(label="COTS_ESP32_S3_CAM_N16R8", children=parts)
    return comp.move(Location((C.S3_X_CTR, C.S3_Y_PCB, C.S3_Z_CTR)))


# ---------------------------------------------------------------------------
# 2. OV3660 Short-Ribbon Camera Sensor Head (8.5 × 8.5 × 6.0 mm)
# ---------------------------------------------------------------------------
def build_ov3660_camera() -> Compound:
    parts = []
    # Square sensor housing (8.5 × 8.5 × 4.0 mm)
    body = Box(C.CAM_BODY_W, 4.0, C.CAM_BODY_H, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(body, "OV3660_SensorBody", "black_oxide"))
    # Round lens barrel protruding forward (+Y)
    barrel = Location((0, 4.0, 0)) * Cylinder(
        radius=C.CAM_LENS_DIA / 2.0, height=2.2, rotation=(90, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    parts.append(_tag(barrel, "OV3660_LensBarrel", "black_oxide"))
    # Optical glass element
    glass = Location((0, 5.6, 0)) * Cylinder(
        radius=2.6, height=0.8, rotation=(90, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    parts.append(_tag(glass, "OV3660_OpticsGlass", "lens_glass"))

    comp = Compound(label="COTS_OV3660_Camera", children=parts)
    return comp.move(Location((0, C.CAM_Y_PCB, C.CAM_Z_CTR)))


# ---------------------------------------------------------------------------
# 3. GMT020-02 2.0" IPS SPI TFT Display (62.0 × 37.5 × 3.4 mm)
# ---------------------------------------------------------------------------
def build_gmt020_lcd() -> Compound:
    parts = []
    with BuildPart() as pcb:
        Box(C.LCD_PCB_W, C.LCD_PCB_T, C.LCD_PCB_H, align=(Align.CENTER, Align.MIN, Align.CENTER))
        for sx in (-1, 1):
            for sz in (-1, 1):
                with Locations((sx * (C.LCD_PCB_W / 2.0 - 3.0), 0, sz * (C.LCD_PCB_H / 2.0 - 3.0))):
                    Cylinder(radius=1.25, height=C.LCD_PCB_T + 1.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
    parts.append(_tag(pcb.part, "GMT020_LCD_PCB", "pcb_green"))

    fpc = Location((C.LCD_GLASS_W / 2.0 + 1.2, C.LCD_PCB_T + 0.4, 0)) * Box(
        4.2, 0.9, 14.0, align=(Align.CENTER, Align.MIN, Align.CENTER)
    )
    parts.append(_tag(fpc, "GMT020_FPC", "fpc_copper"))

    glass = Location((0, C.LCD_PCB_T, 0)) * Box(
        C.LCD_GLASS_W, C.LCD_GLASS_T, C.LCD_GLASS_H, align=(Align.CENTER, Align.MIN, Align.CENTER)
    )
    parts.append(_tag(glass, "GMT020_IPS_Glass", "screen_glass"))

    # Glowing Cyber-Cyan Eyes on 40.8 × 30.6 mm Active Area
    y_eye = C.LCD_PCB_T + C.LCD_GLASS_T
    for sgn, ename in ((-1.0, "L"), (1.0, "R")):
        with BuildPart() as eye:
            with Locations((sgn * 10.5, y_eye, 1.0)):
                Box(13.5, 0.45, 11.0, align=(Align.CENTER, Align.MIN, Align.CENTER))
            with Locations((sgn * 10.2, y_eye - 0.1, 0.4)):
                Box(6.2, 2.0, 5.2, align=(Align.CENTER, Align.MIN, Align.CENTER), mode=Mode.SUBTRACT)
        parts.append(_tag(eye.part, f"Display_CyberEye_{ename}", "cyan_glow"))
        pupil = Location((sgn * 10.2, y_eye, 0.4)) * Box(2.4, 0.5, 2.4, align=(Align.CENTER, Align.MIN, Align.CENTER))
        parts.append(_tag(pupil, f"Display_Pupil_{ename}", "cyan_glow"))

    # 8-Pin pre-soldered straight header on +X short edge pointing backward (-Y)
    hdr_base = Location((C.LCD_PCB_W / 2.0 - 3.5, -2.5, 0)) * Box(2.54, 2.5, 20.5, align=(Align.CENTER, Align.MIN, Align.CENTER))
    hdr_pins = Location((C.LCD_PCB_W / 2.0 - 3.5, -6.5, 0)) * Box(0.7, 4.0, 19.5, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(hdr_base, "GMT020_SPI_HdrBase", "black_oxide"))
    parts.append(_tag(hdr_pins, "GMT020_SPI_HdrPins", "gold"))

    comp = Compound(label="COTS_GMT020_2in_LCD", children=parts)
    return comp.move(Location((0, C.LCD_Y_PCB, C.LCD_Z_CTR)))


# ---------------------------------------------------------------------------
# 4. Dual-18650 Parallel Type-C Power Board (85.0 × 44.0 × 23.0 mm)
# ---------------------------------------------------------------------------
def build_dual_18650_power_board() -> Compound:
    """
    Exact geometry from user's uploaded photos (85.0 × 44.0 × 23.0 mm):
      - Lower dual-18650 parallel holder (77 × 41 × 21.4 mm) + 2× EVE 18650-2500mAh green cells
      - Top green/dark power distribution PCB (85.0 × 44.0 × 1.6 mm) at Z = +21.4..+23.0
      - 3× double-row 2×6P vertical male pin header banks (5V/GND, 3V3/GND, 1V8/GND) on top
      - Right (+X) short edge: Type-C VIN charging port, OFF/ON slide switch, 4× battery LEDs
    """
    parts = []
    # Dual 18650 holder housing beneath PCB
    holder = Location((-2.0, 0, 0)) * Box(77.5, 41.0, 21.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(holder, "Dual18650_Holder", "black_oxide"))

    # 2× EVE 18650-2500mAh 12C flat-top power cells inside holder
    for sy, tag in ((-10.2, "A"), (10.2, "B")):
        cell = Location((-2.0, sy, 10.5)) * Cylinder(radius=9.1, height=65.0, rotation=(0, 90, 0))
        parts.append(_tag(cell, f"Cell_EVE_18650_{tag}", "battery_green"))

    # Top PCB (85.0 × 44.0 × 1.6 mm)
    pcb = Location((0, 0, 21.4)) * Box(C.PWR_L, C.PWR_W, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(pcb, "Dual18650_PCB", "pcb_green"))

    # 3× double-row 2×6P vertical pin header banks (5V/GND, 3V3/GND, 1V8/GND)
    for bx, bname in ((-24.0, "5V"), (-6.0, "3V3"), (12.0, "1V8")):
        hbase = Location((bx, 0, 23.0)) * Box(15.2, 5.1, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        hpins = Location((bx, 0, 25.5)) * Box(14.5, 3.2, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        parts.append(_tag(hbase, f"PwrBank_{bname}_Base", "black_oxide"))
        parts.append(_tag(hpins, f"PwrBank_{bname}_Pins", "gold"))

    # Right (+X) short edge interface: Type-C VIN (Y=+10), ON/OFF Switch (Y=0), 4× LEDs (Y=-11)
    usbc = Location((C.PWR_L / 2.0 - 3.6, 10.0, 23.0)) * Box(7.4, 9.0, 3.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    sw = Location((C.PWR_L / 2.0 - 2.2, 0.0, 23.0)) * Box(5.0, 8.5, 4.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(usbc, "Dual18650_TypeC_VIN", "metal_silver"))
    parts.append(_tag(sw, "Dual18650_ONOFF_Switch", "black_oxide"))
    for i in range(4):
        led = Location((C.PWR_L / 2.0 - 3.0, -7.5 - i * 3.0, 23.0)) * Box(2.0, 1.2, 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        parts.append(_tag(led, f"Dual18650_LED_{25*(i+1)}pct", "rgb_green"))

    comp = Compound(label="COTS_Dual18650_PowerBoard", children=parts)
    return comp.move(Location((C.PWR_X, C.PWR_Y, C.PWR_Z)))


# ---------------------------------------------------------------------------
# 5. PCA9685A 16-Channel I2C PWM Driver (Blue Board, 62.0 × 25.0 mm)
# ---------------------------------------------------------------------------
def build_pca9685a() -> Compound:
    parts = []
    pcb = Box(C.PCA_L, C.PCA_W, C.PCA_PCB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(pcb, "PCA9685_PCB", "pcb_blue"))

    # 16×3P vertical PWM headers along front (+Y) half
    hdr_base = Location((0, 4.5, C.PCA_PCB_T)) * Box(46.0, 7.6, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hdr_pins = Location((0, 4.5, C.PCA_PCB_T + 2.5)) * Box(45.0, 6.2, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(hdr_base, "PCA9685_PWM_Base", "black_oxide"))
    parts.append(_tag(hdr_pins, "PCA9685_PWM_Pins", "gold"))

    # Green V+ power screw terminal & 1000uF electrolytic capacitor
    term = Location((-18.0, -7.5, C.PCA_PCB_T)) * Box(10.0, 7.5, 9.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = Location((14.0, -6.5, C.PCA_PCB_T)) * Cylinder(radius=4.0, height=10.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(term, "PCA9685_PowerTerm", "pcb_green"))
    parts.append(_tag(cap, "PCA9685_FilterCap", "black_oxide"))

    # 6-Pin right-angle I2C header protruding from +X edge (X = +31.0 .. +36.5)
    i2c_hdr = Location((C.PCA_L / 2.0 + 2.5, 0.0, C.PCA_PCB_T + 1.5)) * Box(5.5, 15.2, 2.5)
    parts.append(_tag(i2c_hdr, "PCA9685_I2C_6P", "gold"))

    comp = Compound(label="COTS_PCA9685A_PWM", children=parts)
    return comp.move(Location((C.PCA_X, C.PCA_Y, C.PCA_Z)))


# ---------------------------------------------------------------------------
# 6. 2× DRV8833 Red Dual H-Bridge Motor Drivers (21.0 × 18.0 mm each)
# ---------------------------------------------------------------------------
def build_drv8833(axle: str = "F") -> Compound:
    y_pos = C.DRV_F_Y if axle == "F" else C.DRV_R_Y
    x_pos = C.DRV_F_X if axle == "F" else C.DRV_R_X
    parts = [
        _tag(Box(C.DRV_W, C.DRV_L, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)), f"DRV8833_{axle}_PCB", "pcb_red"),
        _tag(Location((0, 0, 1.6)) * Box(5.0, 6.4, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)), f"DRV8833_{axle}_IC", "black_oxide"),
        _tag(Location((-8.5, 0, 1.6)) * Box(2.5, 15.2, 8.2, align=(Align.CENTER, Align.CENTER, Align.MIN)), f"DRV8833_{axle}_HdrL", "gold"),
        _tag(Location(( 8.5, 0, 1.6)) * Box(2.5, 15.2, 8.2, align=(Align.CENTER, Align.CENTER, Align.MIN)), f"DRV8833_{axle}_HdrR", "gold"),
    ]
    return Compound(label=f"COTS_DRV8833_{axle}", children=parts).move(Location((x_pos, y_pos, C.DRV_Z)))


# ---------------------------------------------------------------------------
# 7. 4× GA12-N20 Pre-Wired Motors & 4× Complete Ø43×18mm D-Shaft Wheels
# ---------------------------------------------------------------------------
def build_n20_motor(side: str = "L", axle: str = "F") -> Compound:
    sgn = -1.0 if side == "L" else 1.0
    y_pos = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    parts = []
    gear_x_ctr = sgn * (C.N20_OUTER_X - C.N20_GEAR_L / 2.0)
    parts.append(_tag(Location((gear_x_ctr, 0, 0)) * Box(C.N20_GEAR_L, C.N20_W, C.N20_H), f"N20_Gearbox_{tag}", "brass"))
    can_l = C.N20_BODY_L - C.N20_GEAR_L
    can_x_ctr = sgn * (C.N20_OUTER_X - C.N20_GEAR_L - can_l / 2.0)
    parts.append(_tag(Location((can_x_ctr, 0, 0)) * Box(can_l, C.N20_W, C.N20_H), f"N20_Can_{tag}", "metal_silver"))
    cap_x = sgn * (C.N20_OUTER_X - C.N20_BODY_L - 1.0)
    parts.append(_tag(Location((cap_x, 0, 0)) * Box(2.0, 9.0, 10.5), f"N20_Endcap_{tag}", "black_oxide"))
    shaft_x_ctr = sgn * (C.N20_OUTER_X + C.N20_SHAFT_L / 2.0)
    with BuildPart() as shaft:
        Cylinder(radius=C.N20_SHAFT_D / 2.0, height=C.N20_SHAFT_L, rotation=(0, 90, 0))
        with Locations((0, 0, C.N20_SHAFT_D / 2.0 - 0.25)):
            Box(C.N20_SHAFT_L + 1.0, C.N20_SHAFT_D + 1.0, 0.5, mode=Mode.SUBTRACT)
    parts.append(_tag(shaft.part.move(Location((shaft_x_ctr, 0, 0))), f"N20_DShaft_{tag}", "metal_silver"))
    return Compound(label=f"COTS_N20_Motor_{tag}", children=parts).move(Location((0, y_pos, C.Z_AXLE)))


def build_complete_43mm_wheel(side: str = "L", axle: str = "F") -> Compound:
    """Complete off-the-shelf Ø43×18mm N20 D-shaft rubber tire + bright rim (replaces printed hubs!)."""
    sgn = -1.0 if side == "L" else 1.0
    y_pos = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    with BuildPart() as tire:
        Cylinder(radius=C.WHEEL_R - 1.3, height=C.WHEEL_W, rotation=(0, 90, 0))
        for i in range(18):
            ang = i * (360.0 / 18.0)
            rad = math.radians(ang)
            with Locations(Location((0, (C.WHEEL_R - 1.3) * math.cos(rad), (C.WHEEL_R - 1.3) * math.sin(rad)), (ang, 0, 0))):
                Box(C.WHEEL_W - 1.2, 2.6, 3.72)
        Cylinder(radius=14.8, height=C.WHEEL_W + 2.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    with BuildPart() as rim:
        Cylinder(radius=14.8, height=C.WHEEL_W - 1.2, rotation=(0, 90, 0))
        with Locations((sgn * 3.0, 0, 0)):
            Cylinder(radius=11.8, height=C.WHEEL_W - 5.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        Cylinder(radius=4.5, height=C.WHEEL_W - 1.0, rotation=(0, 90, 0))
        Cylinder(radius=1.6, height=C.WHEEL_W + 2.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    parts = [
        _tag(tire.part, f"Wheel43_Tire_{tag}", "rubber"),
        _tag(rim.part, f"Wheel43_Rim_{tag}", "wheel_hub"),
    ]
    return Compound(label=f"COTS_Wheel_43mm_{tag}", children=parts).move(
        Location((sgn * C.X_WHEEL, y_pos, C.Z_AXLE))
    )


# ---------------------------------------------------------------------------
# 8. MG90S Servo, 3020 Cavity Speaker, MAX98357A Amp (in Head), INMP441 Mic
# ---------------------------------------------------------------------------
def build_mg90s_servo() -> Compound:
    parts = []
    y_body_off = -(C.MG90S_L / 2.0 - C.MG90S_SHAFT_OFFSET)
    parts.append(_tag(Location((-11.5, y_body_off, 0)) * Box(C.MG90S_H, C.MG90S_L, C.MG90S_W), "MG90S_Body", "servo_blue"))
    parts.append(_tag(Location((-19.0, y_body_off, 0)) * Box(2.5, C.MG90S_FLANGE_L, C.MG90S_W), "MG90S_Flange", "servo_blue"))
    parts.append(_tag(Location((-24.5, 0, 0)) * Cylinder(radius=5.8, height=4.0, rotation=(0, 90, 0)), "MG90S_GearDome", "servo_blue"))
    parts.append(_tag(Location((-28.0, 0, 0)) * Cylinder(radius=2.4, height=4.5, rotation=(0, 90, 0)), "MG90S_Spline", "metal_silver"))
    parts.append(_tag(Location((-30.0, 5.0, 0)) * Box(2.0, 16.0, 5.5), "MG90S_Horn", "white"))
    return Compound(label="COTS_MG90S_Servo", children=parts).move(Location((0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)))


def build_speaker_3020() -> Compound:
    """30.0 × 20.0 × 7.0 mm 8Ω 2W rectangular sealed cavity speaker."""
    parts = [
        _tag(Box(C.SPK_L, C.SPK_W, C.SPK_H, align=(Align.CENTER, Align.CENTER, Align.MAX)), "Speaker_3020_Box", "black_oxide"),
        _tag(Location((0, 0, 0.05)) * Box(22.0, 12.0, 0.5, align=(Align.CENTER, Align.CENTER, Align.MAX)), "Speaker_3020_Cone", "titanium"),
    ]
    return Compound(label="COTS_Speaker_3020", children=parts).move(Location((0, C.SPK_Y, C.SPK_Z_TOP)))


def build_max98357a() -> Compound:
    """MAX98357A Purple I2S Amp mounted vertically against rear inner head wall (ultra-short speaker wire!)."""
    parts = [
        _tag(Box(C.AMP_W, 1.6, C.AMP_H, align=(Align.CENTER, Align.MIN, Align.CENTER)), "MAX98357A_PCB", "pcb_purple"),
        _tag(Location((0, 1.6, 0)) * Box(3.8, 1.0, 3.8, align=(Align.CENTER, Align.MIN, Align.CENTER)), "MAX98357A_IC", "black_oxide"),
        _tag(Location((0, 1.6, 5.2)) * Box(8.2, 6.5, 5.5, align=(Align.CENTER, Align.MIN, Align.CENTER)), "MAX98357A_Terminal", "pcb_green"),
        _tag(Location((0, 1.6, -7.2)) * Box(17.5, 6.5, 2.5, align=(Align.CENTER, Align.MIN, Align.CENTER)), "MAX98357A_Pins", "gold"),
    ]
    return Compound(label="COTS_MAX98357A_Amp", children=parts).move(Location((C.AMP_X, C.AMP_Y, C.AMP_Z)))


def build_inmp441_mic() -> Compound:
    parts = [
        _tag(Cylinder(radius=C.MIC_DIA / 2.0, height=C.MIC_T), "INMP441_PCB", "pcb_dark"),
        _tag(Location((0, 0, -1.2)) * Box(4.7, 3.8, 1.0), "INMP441_MEMS", "gold"),
    ]
    return Compound(label="COTS_INMP441_Mic", children=parts).move(Location((C.MIC_X, C.MIC_Y, C.MIC_Z)))


# ---------------------------------------------------------------------------
# 9. Clean Zero-Soldering 3D Wiring Harness (Only 7 Thin Wires Cross Neck!)
# ---------------------------------------------------------------------------
def build_wiring_harness() -> Compound:
    cables = []

    # 1. OV3660 Short ~20mm FPC Ribbon -> Vertical SF-ESP32-S3-CAM Center 24P Socket (13.9mm straight shot!)
    ov_pts = [
        (0.5, C.S3_Y_PCB + 3.2, C.S3_Z_CTR + 3.0),
        (0.2, 20.5, 134.5),
        (0.0, C.CAM_Y_PCB + 0.5, C.CAM_Z_CTR - 3.5),
    ]
    cables.append(_make_flat_ribbon(ov_pts, 6.5, 0.35, "Cable_OV3660_Short_FPC", "fpc_copper"))

    # 2. 7-Wire Flexible Neck DuPont Ribbon -> Vertical SF-ESP32-S3-CAM Rear-Facing 2×22P Pins!
    neck_specs = [
        ("Neck_5V_S3",  "wire_red",    -2.4),
        ("Neck_5V_AMP", "wire_orange", -1.6),
        ("Neck_3V3_BL", "wire_yellow", -0.8),
        ("Neck_GND_S3", "wire_black",   0.0),
        ("Neck_GND_LR", "wire_brown",   0.8),
        ("Neck_I2C_SDA","wire_blue",    1.6),
        ("Neck_I2C_SCL","wire_green",   2.4),
    ]
    for cname, ckey, dx in neck_specs:
        pts = [
            (dx * 2.5, -18.0, 50.0),
            (8.5 + dx * 0.7, -5.0, 68.0),
            (8.5 + dx * 0.7, -5.0, 92.0),
            (5.0 + dx * 1.2, -3.0, 108.0),
            (dx * 3.0, C.S3_Y_PCB - 6.0, C.S3_Z_CTR - 12.7),
        ]
        cables.append(_make_cable(pts, 0.45, f"Cable_{cname}", ckey))

    # 3. Internal Head Speaker Twisted Pair (MAX98357A -> 3020 Speaker, ~25mm!)
    for cname, ckey, dx in (("SPK_POS", "wire_red", -1.5), ("SPK_NEG", "wire_black", 1.5)):
        pts = [
            (dx, C.AMP_Y + 5.5, C.AMP_Z + 6.5),
            (dx, -17.0, 133.0),
            (dx * 2.0, C.SPK_Y - 2.0, C.SPK_Z_TOP - C.SPK_H),
        ]
        cables.append(_make_cable(pts, 0.50, f"Cable_{cname}", ckey))

    # 4. Internal Head LCD SPI Ribbon (S3-CAM Rear Pins -> GMT020-02)
    for cname, ckey, dz in (("LCD_SCL", "wire_yellow", -2.5), ("LCD_SDA", "wire_blue", 0.0), ("LCD_DC", "wire_green", 2.5)):
        pts = [
            (18.0, C.S3_Y_PCB - 6.0, C.S3_Z_CTR - 12.7 + dz * 0.4),
            (25.0, 12.0, 114.0 + dz),
            (C.LCD_PCB_W / 2.0 - 3.5, C.LCD_Y_PCB - 4.5, C.LCD_Z_CTR + dz * 1.6),
        ]
        cables.append(_make_cable(pts, 0.42, f"Cable_{cname}", ckey))

    # 5. Chassis 4× N20 Factory 2P DuPont Leads -> DRV8833 #1 (Front) & #2 (Rear)
    cables.append(_make_cable([(-20.0, C.Y_AXLE_F, 22.0), (-14.0, C.Y_AXLE_F, 24.0), (-8.5, C.DRV_F_Y, 26.0)], 0.55, "Cable_MOT_FL", "wire_yellow"))
    cables.append(_make_cable([( 20.0, C.Y_AXLE_F, 22.0), ( 14.0, C.Y_AXLE_F, 24.0), ( 8.5, C.DRV_F_Y, 26.0)], 0.55, "Cable_MOT_FR", "wire_blue"))
    cables.append(_make_cable([(-20.0, C.Y_AXLE_R, 22.0), (-14.0, C.Y_AXLE_R, 24.0), (-8.5, C.DRV_R_Y, 26.0)], 0.55, "Cable_MOT_RL", "wire_yellow"))
    cables.append(_make_cable([( 20.0, C.Y_AXLE_R, 22.0), ( 14.0, C.Y_AXLE_R, 24.0), ( 8.5, C.DRV_R_Y, 26.0)], 0.55, "Cable_MOT_RR", "wire_blue"))

    # 6. PCA9685A -> MG90S Servo 3-Pin Lead
    for cname, ckey, dy in (("SERVO_PWM", "wire_orange", -0.8), ("SERVO_5V", "wire_red", 0.0), ("SERVO_GND", "wire_brown", 0.8)):
        pts = [
            (-18.0, C.PCA_Y + 4.5 + dy, C.PCA_Z + 8.0),
            (-10.0, -18.0 + dy, 58.0),
            (-10.0, -14.0 + dy, 82.0),
        ]
        cables.append(_make_cable(pts, 0.44, f"Cable_{cname}", ckey))

    return Compound(label="COTS_Wiring_Harness", children=cables)


# ---------------------------------------------------------------------------
# 10. Unified M3 Captive Metal Hex Nuts & Bolts (ONLY M3 in Entire Robot!)
# ---------------------------------------------------------------------------
def build_fastener_kit() -> Compound:
    items = []
    # 1. Right Coaxial Neck Pivot: 1× M3×10 bolt + 1× Captive DIN 934 M3 Hex Nut inside A02!
    items.append(build_din912_screw(3.0, 10.0, "M3x10_NeckPivot_R").move(Location((34.5, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z), (0, 90, 0))))
    items.append(build_hex_nut(5.5, 2.4, 3.0, "Nut_M3_NeckPivot_R").move(Location((17.8, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z), (0, 90, 0))))

    # 2. N20 Motor Clamps (A03_F/R): 8× M3×10 bolts + 8× Captive M3 Hex Nuts in A01 saddles!
    bx_clamp = C.CHASSIS_W / 2.0 - 13.0
    idx = 0
    for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
        for sgn in (-1.0, 1.0):
            for dy_b in (-9.5, 9.5):
                idx += 1
                items.append(build_din912_screw(3.0, 10.0, f"M3x10_Clamp_{idx}").move(Location((sgn * bx_clamp, y_ax + dy_b, C.Z_AXLE + C.N20_H / 2.0 + 3.0))))
                items.append(build_hex_nut(5.5, 2.4, 3.0, f"Nut_M3_Clamp_{idx}").move(Location((sgn * bx_clamp, y_ax + dy_b, C.CHASSIS_Z_FLOOR + 2.8))))
    return Compound(label="COTS_Fasteners_M3_Only_Kit", children=items)


def build_all_cots() -> dict:
    return {
        "cots_esp32_s3_cam": load_or_build("esp32_s3_cam", build_esp32_s3_cam),
        "cots_ov3660_cam": load_or_build("ov3660_cam", build_ov3660_camera),
        "cots_gmt020_lcd": load_or_build("gmt020_lcd", build_gmt020_lcd),
        "cots_dual18650_pwr": load_or_build("dual_18650_power", build_dual_18650_power_board),
        "cots_pca9685a": load_or_build("pca9685a_pwm", build_pca9685a),
        "cots_drv8833_F": load_or_build("drv8833_F", lambda: build_drv8833("F")),
        "cots_drv8833_R": load_or_build("drv8833_R", lambda: build_drv8833("R")),
        "cots_n20_FL": load_or_build("n20_motor_FL", lambda: build_n20_motor("L", "F")),
        "cots_n20_FR": load_or_build("n20_motor_FR", lambda: build_n20_motor("R", "F")),
        "cots_n20_RL": load_or_build("n20_motor_RL", lambda: build_n20_motor("L", "R")),
        "cots_n20_RR": load_or_build("n20_motor_RR", lambda: build_n20_motor("R", "R")),
        "cots_mg90s_servo": load_or_build("mg90s_servo", build_mg90s_servo),
        "cots_speaker_3020": load_or_build("speaker_3020", build_speaker_3020),
        "cots_max98357a": load_or_build("max98357a_amp", build_max98357a),
        "cots_inmp441_mic": load_or_build("inmp441_mic", build_inmp441_mic),
        "cots_wheel_FL": load_or_build("wheel_43mm_FL", lambda: build_complete_43mm_wheel("L", "F")),
        "cots_wheel_FR": load_or_build("wheel_43mm_FR", lambda: build_complete_43mm_wheel("R", "F")),
        "cots_wheel_RL": load_or_build("wheel_43mm_RL", lambda: build_complete_43mm_wheel("L", "R")),
        "cots_wheel_RR": load_or_build("wheel_43mm_RR", lambda: build_complete_43mm_wheel("R", "R")),
        "cots_wiring": build_wiring_harness(),
        "cots_fasteners": build_fastener_kit(),
    }
