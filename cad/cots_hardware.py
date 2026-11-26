"""
KRON-01V (Vision Edition) Real Off-The-Shelf (COTS) Hardware CAD Library + CSI FFC & Wiring
===========================================================================================
Datasheet-accurate multi-body B-Rep CAD library for:
  - Raspberry Pi Zero 2W (65x30mm green PCB, RP3A0 SiP + finned black aluminum heatsink,
    40-pin 2x20 gold GPIO header, 22-pin CSI-2 camera socket, Micro-SD slot, Mini-HDMI,
    dual Micro-USB ports, Wi-Fi ceramic antenna, 4x official M2.5 mounting holes)
  - OV5647 / IMX219 5MP 160-deg Wide-Angle CSI Camera (25x24mm PCB, 4x M2 holes, M12
    threaded lens barrel with multi-coated blue-tint dark optical glass + 15-pin CSI socket)
  - 15cm Pi Zero MIPI CSI-2 FFC Flat Ribbon Cable (swept smoothly from Pi Zero 2W front
    edge up through widened 18mm neck slot directly into the forehead camera!)
  - 2.0-inch ST7789V IPS TFT LCD with glowing cyber-cyan eyes
  - IP5328P / SW6106 5V 3A Type-C Bidirectional Power Board + 3000mAh 18650 High-Drain Cell
  - 2x GA12-N20 Motors, MG90S Servo, DRV8833, MAX98357A, 28mm Speaker, INMP441 Mic,
    CY-12A Caster, 44mm Rubber Tires, DIN 912 M3 Screws, Brass Inserts & 3D Wire Harnesses
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
    Sphere,
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
    """Build a realistic flat MIPI CSI-2 FFC ribbon cable swept along a 3D curve."""
    with BuildPart() as rib:
        with BuildLine() as path:
            Spline(points)
        with BuildSketch(Plane(origin=path.line @ 0, z_dir=path.line % 0)):
            Rectangle(width, thickness)
        sweep()
    return _tag(rib.part, label, color_key)


# ---------------------------------------------------------------------------
# Fasteners (DIN 912 Socket Head Cap Screws & Brass Heat-Set Inserts)
# ---------------------------------------------------------------------------
def build_din912_screw(dia: float = 3.0, length: float = 8.0, label: str = "M3x8_DIN912") -> Compound:
    head_d = 5.5 if dia >= 2.8 else 3.8
    head_h = 3.0 if dia >= 2.8 else 2.0
    hex_r = (2.5 / math.sqrt(3.0)) if dia >= 2.8 else (1.5 / math.sqrt(3.0))
    with BuildPart() as head:
        Cylinder(radius=head_d / 2.0, height=head_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildSketch(Plane.XY.offset(head_h)):
            RegularPolygon(radius=hex_r, side_count=6)
        extrude(amount=-head_h * 0.65, mode=Mode.SUBTRACT)
    shank = Cylinder(radius=dia / 2.0, height=length, align=(Align.CENTER, Align.CENTER, Align.MAX))
    body = head.part + shank
    _tag(body, label, "black_oxide")
    return Compound(label=label, children=[body])


def build_brass_insert(od: float = 4.5, length: float = 4.0, bore: float = 2.5, label: str = "M3_Brass_Insert") -> Compound:
    with BuildPart() as ins:
        Cylinder(radius=od / 2.0, height=length, align=(Align.CENTER, Align.CENTER, Align.MAX))
        Cylinder(radius=bore / 2.0, height=length + 0.2, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
    _tag(ins.part, label, "brass")
    return Compound(label=label, children=[ins.part])


# ---------------------------------------------------------------------------
# 1. Raspberry Pi Zero 2W (Official 30.0 x 65.0 mm Mechanical Drawing!)
# ---------------------------------------------------------------------------
def build_rpi_zero_2w() -> Compound:
    """
    Raspberry Pi Zero 2W:
      - 30.0(X) x 65.0(Y) x 1.6mm Official Raspberry Green PCB w/ 4x Ø2.75mm corner holes (23x58mm)
      - RP3A0 Quad-Core Cortex-A53 SiP + 14x14x5mm finned black aluminum heatsink
      - 40-pin (2x20) 2.54mm GPIO header along -X edge (upward pins!)
      - 22-pin 0.5mm-pitch MIPI CSI-2 camera socket on +Y front short edge!
      - Micro-SD card slot on -Y rear short edge (accessible through Rear Hatch!)
      - Mini-HDMI + Dual Micro-USB (OTG & PWR) along +X edge + Wi-Fi RF shield & green ACT LED
    """
    parts = []
    # Official Green PCB with 4x M2.5 mounting holes (23.0 x 58.0mm centers)
    with BuildPart() as pcb:
        Box(C.RPI_W, C.RPI_L, C.RPI_PCB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        for sx in (-1, 1):
            for sy in (-1, 1):
                with Locations((sx * C.RPI_HOLE_X / 2.0, sy * C.RPI_HOLE_Y / 2.0, -0.5)):
                    Cylinder(radius=1.375, height=3.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    parts.append(_tag(pcb.part, "RPi_Zero2W_PCB", "pcb_green"))

    # RP3A0 SiP + Black Finned Aluminum Heatsink (14 x 14 x 5.0mm)
    with BuildPart() as hs:
        with Locations((1.5, 2.0, C.RPI_PCB_T)):
            Box(14.0, 14.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        for fy in (-4.5, -1.5, 1.5, 4.5):
            with Locations((1.5, 2.0 + fy, C.RPI_PCB_T + 2.0)):
                Box(15.0, 1.2, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    parts.append(_tag(hs.part, "RPi_RP3A0_Heatsink", "black_oxide"))

    # Wi-Fi / BT Metallic RF Shield (SYN43436)
    rf = Location((2.5, -16.0, C.RPI_PCB_T)) * Box(8.0, 10.0, 1.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(rf, "RPi_WiFi_Shield", "metal_silver"))

    # 22-Pin MIPI CSI-2 Camera Connector at Front Short Edge (+Y = +30.0)
    csi_body = Location((0.0, C.RPI_L / 2.0 - 2.2, C.RPI_PCB_T)) * Box(
        15.0, 4.4, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    csi_latch = Location((0.0, C.RPI_L / 2.0 - 0.3, C.RPI_PCB_T + 0.3)) * Box(
        15.6, 1.2, 1.7, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    parts.append(_tag(csi_body, "RPi_CSI2_Socket", "white"))
    parts.append(_tag(csi_latch, "RPi_CSI2_Latch", "black_oxide"))

    # Micro-SD Card Slot at Rear Short Edge (-Y = -30.5)
    sd = Location((1.0, -C.RPI_L / 2.0 + 6.5, C.RPI_PCB_T)) * Box(
        12.0, 13.5, 1.9, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    parts.append(_tag(sd, "RPi_MicroSD_Slot", "metal_silver"))

    # Mini-HDMI + Dual Micro-USB ports along +X edge
    hdmi = Location((C.RPI_W / 2.0 - 3.8, -19.5, C.RPI_PCB_T)) * Box(7.6, 11.2, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    usb_otg = Location((C.RPI_W / 2.0 - 3.0, 8.5, C.RPI_PCB_T)) * Box(6.0, 7.6, 2.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    usb_pwr = Location((C.RPI_W / 2.0 - 3.0, 21.0, C.RPI_PCB_T)) * Box(6.0, 7.6, 2.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(hdmi, "RPi_MiniHDMI", "metal_silver"))
    parts.append(_tag(usb_otg, "RPi_MicroUSB_OTG", "metal_silver"))
    parts.append(_tag(usb_pwr, "RPi_MicroUSB_PWR", "metal_silver"))

    # 40-Pin (2x20) 2.54mm GPIO Header along -X edge (X = -11.5, upward pins!)
    hdr_base = Location((-C.RPI_W / 2.0 + 3.5, 0.0, C.RPI_PCB_T)) * Box(
        5.08, 50.8, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    parts.append(_tag(hdr_base, "RPi_40Pin_Base", "black_oxide"))
    with BuildPart() as pins40:
        for row_x in (-C.RPI_W / 2.0 + 2.23, -C.RPI_W / 2.0 + 4.77):
            for i in range(20):
                py = -24.13 + i * 2.54
                with Locations((row_x, py, C.RPI_PCB_T + 2.5)):
                    Box(0.64, 0.64, 5.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(pins40.part, "RPi_40Pin_GoldPins", "gold"))

    # Green ACT Status LED
    led = Location((-5.0, -28.0, C.RPI_PCB_T)) * Box(2.0, 1.2, 0.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    parts.append(_tag(led, "RPi_ACT_LED", "rgb_green"))

    comp = Compound(label="COTS_RaspberryPi_Zero2W", children=parts)
    return comp.move(Location((C.RPI_X_CTR, C.RPI_Y_CTR, C.RPI_Z_PCB)))


# ---------------------------------------------------------------------------
# 2. OV5647 / IMX219 5MP 160° Wide-Angle Forehead CSI Camera Module
# ---------------------------------------------------------------------------
def build_csi_camera_ov5647() -> Compound:
    """
    Standard Raspberry Pi Camera V1/V2 Footprint (25.0 x 24.0 mm PCB):
      - 4x Ø2.2mm M2 mounting holes at 21.0 x 12.5mm
      - 15-pin 1.0mm CSI FFC connector on bottom back edge
      - M12 Wide-Angle 160-deg optical lens barrel (Ø14mm x 10.5mm) + multi-coated dark blue optical glass!
    """
    parts = []
    with BuildPart() as pcb:
        Box(C.CAM_PCB_W, C.CAM_PCB_T, C.CAM_PCB_H, align=(Align.CENTER, Align.MIN, Align.CENTER))
        for sx in (-1, 1):
            for sz in (-1, 1):
                with Locations((sx * C.CAM_HOLE_X / 2.0, 0, sz * C.CAM_HOLE_Z / 2.0)):
                    Cylinder(radius=1.1, height=C.CAM_PCB_T + 1.5, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
    parts.append(_tag(pcb.part, "CSI_Cam_PCB", "pcb_dark"))

    # Lens mount base square (14x14x4mm)
    mount = Location((0, C.CAM_PCB_T, 0)) * Box(14.5, 4.0, 14.5, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(mount, "CSI_Cam_M12_Base", "black_oxide"))

    # Stepped wide-angle M12 lens barrel protruding forward (+Y)
    barrel1 = Location((0, C.CAM_PCB_T + 4.0, 0)) * Cylinder(
        radius=C.CAM_LENS_DIA / 2.0, height=5.5, rotation=(90, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    barrel2 = Location((0, C.CAM_PCB_T + 9.0, 0)) * Cylinder(
        radius=C.CAM_LENS_DIA / 2.0 - 0.8, height=2.0, rotation=(90, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    parts.append(_tag(barrel1, "CSI_Cam_LensBarrel", "black_oxide"))
    parts.append(_tag(barrel2, "CSI_Cam_LensRim", "metal_silver"))

    # Multi-coated convex blue/dark optical lens glass element!
    glass = Location((0, C.CAM_PCB_T + 9.8, 0)) * Cylinder(
        radius=4.6, height=1.2, rotation=(90, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MAX)
    )
    parts.append(_tag(glass, "CSI_Cam_OpticsGlass", "lens_glass"))

    # Rear 15-pin CSI FFC connector socket
    sock = Location((0, -1.8, -8.5)) * Box(19.0, 2.5, 4.5, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(sock, "CSI_Cam_15Pin_Socket", "white"))

    comp = Compound(label="COTS_CSI_Camera_OV5647", children=parts)
    return comp.move(Location((0, C.CAM_Y_PCB, C.CAM_Z_CTR)))


# ---------------------------------------------------------------------------
# 3. 2.0-inch ST7789V IPS TFT Display Module (320x240 Landscape)
# ---------------------------------------------------------------------------
def build_st7789_2inch_lcd() -> Compound:
    parts = []
    with BuildPart() as pcb:
        Box(C.LCD_PCB_W, C.LCD_PCB_T, C.LCD_PCB_H, align=(Align.CENTER, Align.MIN, Align.CENTER))
        for sx in (-1, 1):
            for sz in (-1, 1):
                with Locations((sx * (C.LCD_PCB_W / 2.0 - 3.0), 0, sz * (C.LCD_PCB_H / 2.0 - 3.0))):
                    Cylinder(radius=1.35, height=C.LCD_PCB_T + 1.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
    parts.append(_tag(pcb.part, "LCD_ST7789_PCB", "pcb_red"))

    fpc = Location((C.LCD_GLASS_W / 2.0 + 1.0, C.LCD_PCB_T + 0.5, 0)) * Box(
        4.5, 1.0, 14.0, align=(Align.CENTER, Align.MIN, Align.CENTER)
    )
    parts.append(_tag(fpc, "LCD_FPC_Ribbon", "fpc_copper"))

    glass = Location((0, C.LCD_PCB_T, 0)) * Box(
        C.LCD_GLASS_W, C.LCD_GLASS_T, C.LCD_GLASS_H, align=(Align.CENTER, Align.MIN, Align.CENTER)
    )
    parts.append(_tag(glass, "LCD_IPS_Glass", "screen_glass"))

    # Glowing Cyber-Cyan Eyes on Active Area
    y_eye = C.LCD_PCB_T + C.LCD_GLASS_T
    for sgn, ename in ((-1.0, "L"), (1.0, "R")):
        with BuildPart() as eye:
            with Locations((sgn * 10.5, y_eye, 1.0)):
                Box(13.5, 0.5, 11.0, align=(Align.CENTER, Align.MIN, Align.CENTER))
            with Locations((sgn * 10.2, y_eye - 0.1, 0.4)):
                Box(6.2, 2.0, 5.2, align=(Align.CENTER, Align.MIN, Align.CENTER), mode=Mode.SUBTRACT)
        parts.append(_tag(eye.part, f"Display_CyberEye_{ename}", "cyan_glow"))
        pupil = Location((sgn * 10.2, y_eye, 0.4)) * Box(2.4, 0.55, 2.4, align=(Align.CENTER, Align.MIN, Align.CENTER))
        parts.append(_tag(pupil, f"Display_Pupil_{ename}", "cyan_glow"))

    hdr_base = Location((C.LCD_PCB_W / 2.0 - 4.0, -2.5, 0)) * Box(2.54, 2.5, 20.5, align=(Align.CENTER, Align.MIN, Align.CENTER))
    hdr_pins = Location((C.LCD_PCB_W / 2.0 - 4.0, -6.5, 0)) * Box(0.7, 4.0, 19.5, align=(Align.CENTER, Align.MIN, Align.CENTER))
    parts.append(_tag(hdr_base, "LCD_SPI_Header_Base", "black_oxide"))
    parts.append(_tag(hdr_pins, "LCD_SPI_Header_Pins", "gold"))

    comp = Compound(label="COTS_ST7789_2in_LCD", children=parts)
    return comp.move(Location((0, C.LCD_Y_PCB, C.LCD_Z_CTR)))


# ---------------------------------------------------------------------------
# 4. N20 Motors, MG90S Servo, 18650 Battery, DRV8833, MAX98357A, IP5328P, Switch
# ---------------------------------------------------------------------------
def build_n20_motor(side: str = "L", axle: str = "F") -> Compound:
    """GA12-N20 Metal Gear Motor mounted at Front (+26) or Rear (-26) axle, Left or Right."""
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


def build_mg90s_servo() -> Compound:
    parts = []
    y_body_off = -(C.MG90S_L / 2.0 - C.MG90S_SHAFT_OFFSET)
    parts.append(_tag(Location((-11.5, y_body_off, 0)) * Box(C.MG90S_H, C.MG90S_L, C.MG90S_W), "MG90S_Body", "servo_blue"))
    parts.append(_tag(Location((-19.0, y_body_off, 0)) * Box(2.5, C.MG90S_FLANGE_L, C.MG90S_W), "MG90S_Flange", "servo_blue"))
    parts.append(_tag(Location((-24.5, 0, 0)) * Cylinder(radius=5.8, height=4.0, rotation=(0, 90, 0)), "MG90S_GearDome", "servo_blue"))
    parts.append(_tag(Location((-28.0, 0, 0)) * Cylinder(radius=2.4, height=4.5, rotation=(0, 90, 0)), "MG90S_Spline", "metal_silver"))
    parts.append(_tag(Location((-30.0, 5.0, 0)) * Box(2.0, 16.0, 5.5), "MG90S_Horn", "white"))
    return Compound(label="COTS_MG90S_Servo", children=parts).move(Location((0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)))


def build_18650_battery() -> Compound:
    parts = []
    with BuildPart() as holder:
        Box(C.BAT_HOLDER_L, C.BAT_HOLDER_W, C.BAT_HOLDER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, 2.0)):
            Box(C.BAT_HOLDER_L - 4.0, C.BAT_HOLDER_W - 3.0, C.BAT_HOLDER_H, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    parts.append(_tag(holder.part, "Battery_Holder_18650", "black_oxide"))
    parts.append(_tag(Location((0, 0, 11.2)) * Cylinder(radius=9.2, height=65.2, rotation=(0, 90, 0)), "Cell_18650_3000mAh", "battery_pink"))
    parts.append(_tag(Location((33.1, 0, 11.2)) * Cylinder(radius=4.0, height=1.5, rotation=(0, 90, 0)), "Battery_PosCap", "metal_silver"))
    parts.append(_tag(Location((-34.0, 0, 11.2)) * Cylinder(radius=5.0, height=3.0, rotation=(0, 90, 0)), "Battery_NegSpring", "metal_silver"))
    return Compound(label="COTS_18650_Battery", children=parts).move(Location((0, C.BAT_Y, C.BAT_Z_BOT)))


def build_drv8833() -> Compound:
    parts = [
        _tag(Box(C.DRV_W, C.DRV_L, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)), "DRV8833_PCB", "pcb_green"),
        _tag(Location((0, 0, 1.6)) * Box(5.0, 6.4, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)), "DRV8833_IC", "black_oxide"),
    ]
    return Compound(label="COTS_DRV8833_Driver", children=parts).move(Location((C.DRV_X, C.DRV_Y, C.DRV_Z)))


def build_max98357a() -> Compound:
    parts = [
        _tag(Box(C.AMP_W, C.AMP_L, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)), "MAX98357A_PCB", "pcb_purple"),
        _tag(Location((0, 0, 1.6)) * Box(3.5, 3.5, 0.9, align=(Align.CENTER, Align.CENTER, Align.MIN)), "MAX98357A_IC", "black_oxide"),
        _tag(Location((0, 5.5, 1.6)) * Box(8.0, 5.5, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN)), "MAX98357A_Terminal", "pcb_green"),
    ]
    return Compound(label="COTS_MAX98357A_Amp", children=parts).move(Location((C.AMP_X, C.AMP_Y, C.AMP_Z)))


def build_ip5328p_power_3a() -> Compound:
    parts = [
        _tag(Box(C.PWR_W, C.PWR_L, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)), "IP5328P_PCB", "pcb_dark"),
        _tag(Location((0, -C.PWR_L / 2.0 + 3.5, 1.6)) * Box(9.0, 7.5, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN)), "IP5328P_USBC_3A", "metal_silver"),
        _tag(Location((0, 5.0, 1.6)) * Box(8.0, 8.0, 4.2, align=(Align.CENTER, Align.CENTER, Align.MIN)), "IP5328P_PowerInductor", "black_oxide"),
    ]
    return Compound(label="COTS_IP5328P_5V3A_Power", children=parts).move(Location((C.PWR_X, C.PWR_Y, C.PWR_Z)))


def build_power_switch() -> Compound:
    parts = [
        _tag(Box(8.6, 4.4, 4.5), "SS12D00G3_Body", "metal_silver"),
        _tag(Location((-1.5, -3.5, 0)) * Box(2.5, 3.5, 2.5), "SS12D00G3_Knob", "black_oxide"),
    ]
    return Compound(label="COTS_Power_Switch", children=parts).move(Location((C.SW_X, C.SW_Y, C.SW_Z)))


def build_speaker_28mm() -> Compound:
    parts = [
        _tag(Cylinder(radius=C.SPK_DIA / 2.0, height=2.5, align=(Align.CENTER, Align.CENTER, Align.MAX)), "Speaker_Frame", "black_oxide"),
        _tag(Location((0, 0, -2.5)) * Cylinder(radius=8.5, height=2.5, align=(Align.CENTER, Align.CENTER, Align.MAX)), "Speaker_Magnet", "metal_silver"),
    ]
    return Compound(label="COTS_Speaker_28mm", children=parts).move(Location((0, C.SPK_Y, C.SPK_Z_TOP)))


def build_inmp441_mic() -> Compound:
    parts = [
        _tag(Cylinder(radius=7.0, height=1.6), "INMP441_PCB", "pcb_dark"),
        _tag(Location((0, 0, 1.3)) * Box(4.7, 3.8, 1.0), "INMP441_MEMS", "gold"),
    ]
    return Compound(label="COTS_INMP441_Mic", children=parts).move(Location((0, C.MIC_Y, C.MIC_Z)))


def build_rubber_tire(side: str = "L", axle: str = "F") -> Compound:
    """42mm OD x 29.8mm ID x 17mm wide chunky rugged off-road rubber tire for Terra-Rover 4WD."""
    sgn = -1.0 if side == "L" else 1.0
    y_pos = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    with BuildPart() as tire:
        Cylinder(radius=C.WHEEL_R - 1.4, height=C.WHEEL_W, rotation=(0, 90, 0))
        # Chunky staggered off-road tread lugs (exact Ø42.0mm outer envelope -> Z_min = 0.00mm!)
        for i in range(18):
            ang = i * (360.0 / 18.0)
            rad = math.radians(ang)
            with Locations(Location((0, (C.WHEEL_R - 1.35) * math.cos(rad), (C.WHEEL_R - 1.35) * math.sin(rad)), (ang, 0, 0))):
                Box(C.WHEEL_W - 1.4, 2.5, 3.8)
        Cylinder(radius=C.WHEEL_HUB_OD / 2.0 - 0.2, height=C.WHEEL_W + 2.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        Cylinder(radius=C.WHEEL_R + 1.0, height=2.2, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        Cylinder(radius=C.WHEEL_R - 2.0, height=2.4, rotation=(0, 90, 0))
        Cylinder(radius=C.WHEEL_HUB_OD / 2.0 - 0.2, height=C.WHEEL_W + 2.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    _tag(tire.part, f"Rubber_Tire_42mm_{tag}", "rubber")
    return Compound(label=f"COTS_Rubber_Tire_{tag}", children=[tire.part]).move(
        Location((sgn * C.X_WHEEL, y_pos, C.Z_AXLE))
    )


# ---------------------------------------------------------------------------
# 5. Real 3D MIPI CSI-2 Flat Ribbon Cable + 4WD Color-Coded Harnesses
# ---------------------------------------------------------------------------
def build_wiring_harness() -> Compound:
    cables = []

    # 1. REAL MIPI CSI-2 FFC FLAT RIBBON CABLE (Pi Zero 2W Front -> Neck -> Visor OV5647)
    csi_pts = [
        (C.RPI_X_CTR, C.RPI_Y_CTR + C.RPI_L / 2.0 - 1.0, C.RPI_Z_PCB + 2.5),
        (2.0, 12.0, 50.0),
        (4.0, 2.0, 64.0),
        (3.0, 5.0, 82.0),
        (0.0, 14.0, 96.0),
        (0.0, C.CAM_Y_PCB - 2.0, C.CAM_Z_CTR - 8.5),
    ]
    cables.append(_make_flat_ribbon(csi_pts, 12.0, 0.55, "Cable_MIPI_CSI2_FFC_Ribbon", "ffc_white"))

    # 2. SPI0 LCD Ribbon
    for cname, ckey, dx in (("SPI0_SCLK", "wire_yellow", -1.5), ("SPI0_MOSI", "wire_blue", -0.5), ("SPI0_RST", "wire_green", 0.5), ("SPI0_DC", "wire_orange", 1.5)):
        pts = [(-14.5, 0.0 + dx * 1.2, 46.5), (-6.0 + dx, 4.0, 52.0), (10.0 + dx * 0.6, 0.0, 64.0), (12.0 + dx * 0.6, 3.0, 74.0), (26.5, 14.5, C.LCD_Z_CTR + dx * 1.8)]
        cables.append(_make_cable(pts, 0.52, f"Cable_{cname}", ckey))

    # 3. I2S Mic Bundle -> Chin INMP441
    for cname, ckey, dx in (("I2S_WS", "wire_purple", -0.7), ("I2S_SD", "wire_white", 0.7)):
        pts = [(-14.5, -18.0 + dx, 46.5), (-8.0 + dx, 2.0, 52.0), (0.0 + dx, 4.0, 59.0), (dx, C.MIC_Y - 3.0, C.MIC_Z + 1.0)]
        cables.append(_make_cable(pts, 0.48, f"Cable_{cname}", ckey))

    # 4. Speaker Twisted Pair: Rear MAX98357A -> Neck -> Rear Crown Speaker
    for cname, ckey, dx in (("SPK_POS", "wire_red", -0.8), ("SPK_NEG", "wire_black", 0.8)):
        pts = [(dx * 2.0, C.AMP_Y + 5.5, 25.0), (10.0 + dx, -16.0, 38.0), (11.0 + dx, -5.0, 55.0), (8.0 + dx, -8.0, 80.0), (4.0 + dx, -12.0, 102.0), (dx * 2.5, C.SPK_Y, C.SPK_Z_TOP - 4.5)]
        cables.append(_make_cable(pts, 0.56, f"Cable_{cname}", ckey))

    # 5. MG90S Servo 3-Pin Ribbon
    for cname, ckey, dy in (("SERVO_PWM1", "wire_orange", -1.0), ("SERVO_5V", "wire_red", 0.0), ("SERVO_GND", "wire_brown", 1.0)):
        cables.append(_make_cable([(-2.0, -16.0 + dy, 65.5), (-10.0, -12.0 + dy, 55.0), (-14.5, -10.0 + dy * 1.4, 46.5)], 0.46, f"Cable_{cname}", ckey))

    # 6. 4WD Parallel Left & Right N20 Motor Power Pairs -> Front-Center DRV8833
    cables.append(_make_cable([(-15.5, C.Y_AXLE_F, 22.0), (-11.0, C.Y_AXLE_F, 22.0), (-6.0, C.DRV_Y, 22.0)], 0.60, "Cable_MOT_FL", "wire_yellow"))
    cables.append(_make_cable([( 15.5, C.Y_AXLE_F, 22.0), ( 11.0, C.Y_AXLE_F, 22.0), ( 6.0, C.DRV_Y, 22.0)], 0.60, "Cable_MOT_FR", "wire_blue"))
    cables.append(_make_cable([(-15.5, C.Y_AXLE_R, 22.0), (-14.0, 0.0, 38.5), (-6.0, C.DRV_Y - 5.0, 22.5)], 0.60, "Cable_MOT_RL", "wire_yellow"))
    cables.append(_make_cable([( 15.5, C.Y_AXLE_R, 22.0), ( 14.0, 0.0, 38.5), ( 6.0, C.DRV_Y - 5.0, 22.5)], 0.60, "Cable_MOT_RR", "wire_blue"))

    # 7. 5V/3A Main Power Bus: Center 18650 (Y=0) -> Switch -> IP5328P -> Pi Zero 2W
    cables.append(_make_cable([(34.0, C.BAT_Y - 4.0, 29.5), (35.0, -16.0, 39.0), (C.PWR_X + 3.0, -24.0, C.PWR_Z + 2.0)], 0.90, "Cable_BAT_POS_20AWG", "wire_red"))
    cables.append(_make_cable([(-34.0, C.BAT_Y - 4.0, 29.5), (-34.0, -24.0, 39.5), (C.SW_X, C.SW_Y + 3.0, C.SW_Z)], 0.90, "Cable_BAT_SW_20AWG", "wire_black"))
    cables.append(_make_cable([(C.PWR_X - 5.0, -22.0, C.PWR_Z + 2.0), (14.0, -22.0, 46.5), (-14.5, -26.0, 46.5)], 0.82, "Cable_5V3A_BUS_RED", "wire_red"))
    cables.append(_make_cable([(C.PWR_X - 5.0, -26.0, C.PWR_Z + 2.0), (14.0, -26.0, 45.5), (-14.5, -29.0, 46.5)], 0.82, "Cable_GND_BUS_BLK", "wire_black"))

    return Compound(label="COTS_Wiring_and_CSI_FFC", children=cables)


# ---------------------------------------------------------------------------
# 6. Fasteners & Heat-Set Inserts (Clean Hidden Clamshell Bolts + Ear Pivots)
# ---------------------------------------------------------------------------
def build_fastener_kit() -> Compound:
    items = []
    # Clamshell Top Hood 4x M3x8 flush recessed bolts (2 rear deck + 2 mid-flank under white shoulder wings!)
    for i, (x, y) in enumerate(((-33.5, -39.0), (33.5, -39.0), (-33.5, 16.0), (33.5, 16.0))):
        items.append(build_din912_screw(3.0, 8.0, f"M3x8_TopHood_{i+1}").move(Location((x, y, C.CHASSIS_Z_TOP - 2.0))))
        items.append(build_brass_insert(4.5, 4.0, 2.5, f"Insert_TopHood_{i+1}").move(Location((x, y, C.CHASSIS_SPLIT_Z))))
    # Head Shell Lock 2x M3x10 bolts + Brass Inserts (A09 Ear Hub -> B04 Shell -> A06 Core!)
    for side, sgn in (("L", -1.0), ("R", 1.0)):
        items.append(build_din912_screw(3.0, 10.0, f"M3x10_EarLock_{side}").move(Location((sgn * 45.8, C.HEAD_Y_CTR - 2.0, C.HEAD_Z_CTR - 1.0), (0, -90 if sgn < 0 else 90, 0))))
        items.append(build_brass_insert(4.5, 4.0, 2.5, f"Insert_EarLock_{side}").move(Location((sgn * 34.0, C.HEAD_Y_CTR - 2.0, C.HEAD_Z_CTR - 1.0), (0, 90 if sgn < 0 else -90, 0))))
    # Coaxial Right Neck Pivot M3x10 bolt + Brass Insert inside A02_Top_Hood neck!
    items.append(build_din912_screw(3.0, 10.0, "M3x10_NeckPivot_R").move(Location((31.5, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z), (0, 90, 0))))
    items.append(build_brass_insert(4.5, 4.0, 2.5, "Insert_NeckPivot_R").move(Location((21.0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z), (0, -90, 0))))
    return Compound(label="COTS_Fasteners_M3_Kit", children=items)


def build_all_cots() -> dict:
    return {
        "cots_rpi_zero2w": load_or_build("rpi_zero_2w", build_rpi_zero_2w),
        "cots_csi_camera": load_or_build("csi_camera_ov5647", build_csi_camera_ov5647),
        "cots_st7789_lcd": load_or_build("st7789_2inch_lcd", build_st7789_2inch_lcd),
        "cots_n20_FL": load_or_build("n20_motor_FL", lambda: build_n20_motor("L", "F")),
        "cots_n20_FR": load_or_build("n20_motor_FR", lambda: build_n20_motor("R", "F")),
        "cots_n20_RL": load_or_build("n20_motor_RL", lambda: build_n20_motor("L", "R")),
        "cots_n20_RR": load_or_build("n20_motor_RR", lambda: build_n20_motor("R", "R")),
        "cots_mg90s_servo": load_or_build("mg90s_servo", build_mg90s_servo),
        "cots_18650_battery": load_or_build("battery_18650", build_18650_battery),
        "cots_drv8833": load_or_build("drv8833_driver", build_drv8833),
        "cots_max98357a": load_or_build("max98357a_amp", build_max98357a),
        "cots_ip5328p_power": load_or_build("ip5328p_power_3a", build_ip5328p_power_3a),
        "cots_power_switch": load_or_build("power_switch", build_power_switch),
        "cots_speaker_28mm": load_or_build("speaker_28mm", build_speaker_28mm),
        "cots_inmp441_mic": load_or_build("inmp441_mic", build_inmp441_mic),
        "cots_tire_FL": load_or_build("rubber_tire_FL", lambda: build_rubber_tire("L", "F")),
        "cots_tire_FR": load_or_build("rubber_tire_FR", lambda: build_rubber_tire("R", "F")),
        "cots_tire_RL": load_or_build("rubber_tire_RL", lambda: build_rubber_tire("L", "R")),
        "cots_tire_RR": load_or_build("rubber_tire_RR", lambda: build_rubber_tire("R", "R")),
        "cots_wiring": build_wiring_harness(),
        "cots_fasteners": build_fastener_kit(),
    }
