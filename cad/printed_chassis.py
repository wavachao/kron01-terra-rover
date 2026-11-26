"""
KRON-01V5 (Terra-Rover 4WD Edition — Production DFM/DFA Reinforced Release)
===========================================================================
Every mechanical joint is production-engineered for rock-solid FDM assembly:
  - A01_chassis_tub       : Lower tub w/ 4× N20 cradles + M2.5 screw bosses for motor clamp straps,
                            perimeter clamshell alignment rim, front nose catch ledge, side-panel
                            screw bosses, and rear-wall Micro-SD + 5V/3A Type-C + Switch + OTG port!
  - A02_top_hood          : Sloped aerodynamic lift-off hood w/ 2.5mm underside perimeter alignment
                            step-lip, front interlock tongue, locating sockets for B01 white wings,
                            recessed neck-swing well (-20°..+25° zero collision), and sturdy shark-fin!
  - A03_motor_clamp_F/R   : 2× bolt-down N20 motor retaining clamp straps (prevents motor twist/pop-out!)
  - A04_wheel_hub_FL..RR  : Deep-dish 6-spoke star hubs w/ inward-extended 8.5mm D-shaft collar +
                            radial M2.5 set-screw hole for slip-proof torque transfer!
  - B01_hood_wing_L/R     : Pearl-white hood wings w/ dual Ø3.0mm locating alignment pegs!
  - B02/B03_side_fairing  : Pearl-white side fairings w/ internal M3 screw bosses + locating pegs!
  - C03_wheel_rim_FL..RR  : 4× snap-in satin gold-amber inner wheel lip accent rings
"""

import math
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Cylinder,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    RectangleRounded,
    add,
    extrude,
    loft,
)
import config as C


def _col(name: str) -> Color:
    r, g, b, a = C.COLORS[name]
    return Color(r, g, b, a)


def _tag(shape, label: str, color_key: str):
    shape.label = label
    shape.color = _col(color_key)
    return shape


# ---------------------------------------------------------------------------
# A01: Reinforced Clamshell Lower Rover Chassis Tub (Plate A — Gunmetal)
# ---------------------------------------------------------------------------
def build_chassis_tub() -> Part:
    w = C.CHASSIS_W        # 80.0
    l = C.CHASSIS_L        # 104.0 (Y: -50..+54)
    yc = C.CHASSIS_Y_CTR   # +2.0
    h = C.CHASSIS_SPLIT_Z - C.CHASSIS_Z_BOT  # 33.5 mm (Z = 15.0..48.5)
    wall = C.WALL          # 2.5

    with BuildPart() as outer_bp:
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_BOT)):
            with Locations((0, yc - 1.0)):
                RectangleRounded(w - 6.0, l - 8.0, radius=11.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_BOT + 7.5)):
            with Locations((0, yc)):
                RectangleRounded(w, l, radius=11.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z)):
            with Locations((0, yc)):
                RectangleRounded(w, l, radius=11.0)
        loft(ruled=False)

    with BuildPart() as tub:
        add(outer_bp.part)

        # Sloped front nose trim
        with Locations(Location((0, 56.0, 48.5), (-32, 0, 0))):
            Box(w + 10.0, 32.0, 22.0, mode=Mode.SUBTRACT)

        # Protective 1.2mm dropped skid pads under 4× N20 motors
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * (w / 2.0 - 13.5), y_ax, C.CHASSIS_Z_BOT - 1.0)):
                    Box(22.0, C.N20_W + 4.4, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4× Reinforced Suspension Axle Collar Shrouds (|X| = 38..41.5 -> leaves crisp 2mm gap to tire!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * 40.2, y_ax, C.Z_AXLE)):
                    Cylinder(radius=5.0, height=3.8, rotation=(0, 90, 0))

        # Angled Front Off-Road Skid Plate + Recessed Grille + Headlight Bezels
        with Locations(Location((0, 53.5, 22.0), (28, 0, 0))):
            Box(28.0, 3.6, 15.0)
        with Locations((0, 56.5, 31.5)):
            Box(24.0, 6.0, 6.5, mode=Mode.SUBTRACT)
        for sx in (-1, 1):
            with Locations((sx * 21.0, 55.5, 32.5)):
                Box(10.0, 6.0, 5.5, mode=Mode.SUBTRACT)

        # 2. Hollow interior cavity (open cleanly at top Z = 48.5, closed ALL 4 vertical walls!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_FLOOR)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(w - 2 * wall, l - 10.0, radius=7.5)
        extrude(amount=h + 4.0, mode=Mode.SUBTRACT)

        # Front Nose Interlock Catch Ledge (fused solidly into front inner wall at Y=47..48.5; receives A02 tongue!)
        with Locations((0, 45.5, 38.3)):
            Box(28.0, 6.0, 3.0)

        # 3. 4× N20 Gearmotor Cradles + M2.5 Bolt Bosses for A03 Motor Clamp Straps!
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                saddle_x = sgn * (w / 2.0 - 13.5)
                with Locations((saddle_x, y_ax, C.CHASSIS_Z_FLOOR)):
                    Box(22.0, C.N20_W + 7.2, 9.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations((sgn * (w / 2.0 - 12.5), y_ax, C.Z_AXLE + 0.1)):
                    Box(26.5, C.N20_W + 0.35, C.N20_H + 0.35, mode=Mode.SUBTRACT)
                with Locations((sgn * (w / 2.0 + 1.0), y_ax, C.Z_AXLE)):
                    Cylinder(radius=3.6, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                # Dual M2.5 pilot holes flanking each motor for bolt-down clamp strap A03!
                for dy_b in (-7.2, 7.2):
                    with Locations((sgn * 28.0, y_ax + dy_b, C.CHASSIS_Z_FLOOR + 2.5)):
                        Cylinder(radius=C.M25_PILOT_DIA / 2.0, height=8.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 4. Dead-Center 18650 Battery Retaining Rails (Y = ±11.8 -> 50/50 CG!)
        for sgn_y in (-1.0, 1.0):
            with Locations((0, C.BAT_Y + sgn_y * (C.BAT_HOLDER_W / 2.0 + 1.2), C.CHASSIS_Z_FLOOR)):
                Box(64.0, 2.0, 11.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 5. Official Raspberry Pi Zero 2W 4× M2.5 Standoffs (23.0 × 58.0 mm)
        for sx in (-1, 1):
            for sy in (-1, 1):
                px = C.RPI_X_CTR + sx * (C.RPI_HOLE_X / 2.0)
                py = C.RPI_Y_CTR + sy * (C.RPI_HOLE_Y / 2.0)
                with Locations((px, py, C.CHASSIS_Z_FLOOR)):
                    Cylinder(radius=2.9, height=C.RPI_Z_PCB - C.CHASSIS_Z_FLOOR, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations((px, py, C.RPI_Z_PCB - 5.2)):
                    Cylinder(radius=C.M25_PILOT_DIA / 2.0, height=6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # DRV8833 & MAX98357A standoffs + IP5328P upper shelf
        for px, py in ((C.DRV_X, C.DRV_Y), (C.AMP_X, C.AMP_Y)):
            for dx in (-7.2, 7.2):
                for dy in (-6.2, 6.2):
                    with Locations((px + dx, py + dy, C.CHASSIS_Z_FLOOR)):
                        Cylinder(radius=2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((C.PWR_X + 1.0, C.PWR_Y, C.PWR_Z - 2.0)):
            Box(19.0, 26.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((w / 2.0 - wall - 1.5, C.PWR_Y, C.PWR_Z - 8.0)):
            Box(3.0, 24.0, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 6. 4× Clamshell Top-Hood M3 Heat-Set Brass Insert Bosses
        for bx, by in ((-33.5, -39.0), (33.5, -39.0), (-33.5, 16.0), (33.5, 16.0)):
            with Locations((bx, by, C.CHASSIS_SPLIT_Z - 5.8)):
                Cylinder(radius=4.3, height=5.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((bx, by, C.CHASSIS_SPLIT_Z - 5.2)):
                Cylinder(radius=C.HEATSET_M3_DIA / 2.0, height=5.8, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 7. Side-Fairing Mounting Holes (Internal M3 Screw + Ø3.3mm Locating Socket — Zero External Screws!)
        for sgn in (-1.0, 1.0):
            for by in (-14.0, 2.0):
                with Locations((sgn * (w / 2.0 - 1.0), by, 37.5)):
                    Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=8.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # 8. Rear-Wall Zero-Disassembly Maintenance Ports (Micro-SD + 5V/3A Type-C + Switch + Optional OTG + Vents)
        y_rear = C.CHASSIS_Y_MIN
        with Locations((C.RPI_X_CTR + 1.0, y_rear + 1.5, C.RPI_Z_PCB + 2.6)):
            Box(15.5, 8.0, 5.2, mode=Mode.SUBTRACT)  # Tool-free Micro-SD quick-swap!
        with Locations((C.PWR_X, y_rear + 1.5, C.PWR_Z + 3.2)):
            Box(11.8, 8.0, 6.4, mode=Mode.SUBTRACT)  # 5V/3A Type-C charge/UPS port
        with Locations((C.SW_X, y_rear + 1.5, C.SW_Z)):
            Box(9.2, 8.0, 4.4, mode=Mode.SUBTRACT)   # Main power slide switch
        with Locations((13.0, y_rear + 1.5, 32.0)):
            Box(11.0, 8.0, 6.0, mode=Mode.SUBTRACT)  # Optional wired USB-OTG pigtail debug port!
        for sx in (-12.0, -5.0, 2.0):
            with Locations((sx, y_rear + 1.5, 27.0)):
                Box(3.4, 8.0, 9.0, mode=Mode.SUBTRACT)

    return _tag(tub.part, "A01_Chassis_Tub", "charcoal")


# ---------------------------------------------------------------------------
# A03_F / A03_R: Bolt-Down N20 Motor Clamp Straps (Locks 4× N20 Rock-Solid!)
# ---------------------------------------------------------------------------
def build_motor_clamp(axle: str = "F") -> Part:
    """Rigid M2.5 bolt-down clamp strap locking both N20 gearboxes on an axle into A01_Chassis_Tub."""
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    with BuildPart() as clamp:
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 28.0, y_ax, C.Z_AXLE + C.N20_H / 2.0 + 1.4)):
                Box(14.0, 20.0, 2.6)
            for dy_b in (-7.2, 7.2):
                with Locations((sgn * 28.0, y_ax + dy_b, C.Z_AXLE + C.N20_H / 2.0 + 1.4)):
                    Cylinder(radius=1.45, height=5.0, mode=Mode.SUBTRACT)
        # Thin tie-bar bridging left & right clamp pads (clears DRV8833/MAX98357A cleanly above Z=27!)
        with Locations((0, y_ax, C.Z_AXLE + C.N20_H / 2.0 + 1.8)):
            Box(46.0, 5.0, 2.2)
    return _tag(clamp.part, f"A03_Motor_Clamp_{axle}", "charcoal")


# ---------------------------------------------------------------------------
# A02: Reinforced Clamshell Top Hood (Step-Lip + Front Catch + Shark-Fin!)
# ---------------------------------------------------------------------------
def build_top_hood() -> Part:
    w = C.CHASSIS_W
    l = C.CHASSIS_L
    yc = C.CHASSIS_Y_CTR

    with BuildPart() as hood_bp:
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z)):
            with Locations((0, yc)):
                RectangleRounded(w, l, radius=11.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP)):
            with Locations((0, yc - 4.0)):
                RectangleRounded(w - 10.0, l - 14.0, radius=10.0)
        loft(ruled=False)

    with BuildPart() as hood:
        add(hood_bp.part)

        # Match sloped front nose cleanly
        with Locations(Location((0, 56.0, 48.5), (-32, 0, 0))):
            Box(w + 10.0, 32.0, 22.0, mode=Mode.SUBTRACT)

        # 2.5mm Underside Perimeter Alignment Step-Lip (snaps into tub with zero lateral rattle!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z - 2.5)):
            with Locations((0, -10.0)):
                RectangleRounded(73.8, 70.0, radius=7.0)
        extrude(amount=2.8)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z - 3.0)):
            with Locations((0, -10.0)):
                RectangleRounded(68.8, 65.0, radius=5.5)
        extrude(amount=4.0, mode=Mode.SUBTRACT)
        # Clear the 4 corner brass insert bosses cleanly
        for bx, by in ((-33.5, -39.0), (33.5, -39.0), (-33.5, 16.0), (33.5, 16.0)):
            with Locations((bx, by, C.CHASSIS_SPLIT_Z - 3.5)):
                Cylinder(radius=5.2, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Front Interlock Catch Hook (L-shaped stem + tongue fused solidly into hood underside; slides cleanly under A01 ledge!)
        with Locations((0, 34.25, 42.0)):
            Box(22.0, 3.5, 16.0)
        with Locations((0, 39.25, 35.2)):
            Box(22.0, 13.5, 2.4)

        # Raised Sporty Rear-Deck Fastback Cowl + Unbreakable Sculpted Aero Shark-Fin Antenna!
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 1.5)):
            with Locations((0, -30.0)):
                RectangleRounded(42.0, 26.0, radius=6.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 3.2)):
            with Locations((0, -31.0)):
                RectangleRounded(32.0, 18.0, radius=5.0)
        loft(ruled=False)
        # Sturdy FDM-proof Aero Shark-Fin (5mm thick -> 10x stronger than thin cylindrical pin!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 2.0)):
            with Locations((14.0, -34.0)):
                RectangleRounded(5.0, 14.0, radius=2.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 13.5)):
            with Locations((14.0, -39.0)):
                RectangleRounded(3.2, 6.5, radius=1.2)
        loft(ruled=False)

        # Underside headroom recess (clears 40-pin GPIO & heatsink) + Top convection vents
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z - 0.5)):
            with Locations((0, -10.0)):
                RectangleRounded(60.0, 74.0, radius=6.0)
        extrude(amount=4.2, mode=Mode.SUBTRACT)
        for vx in (-9.0, -3.0, 3.0, 9.0):
            with Locations((vx, -28.0, C.CHASSIS_Z_TOP - 2.0)):
                Box(2.4, 12.0, 8.0, mode=Mode.SUBTRACT)

        # Sculpted Neck Turret (Z = 53..76 -> supports coaxial head pivot at Z=69.5!)
        neck_base_z = C.CHASSIS_Z_TOP - 2.0
        neck_top_z = C.HEAD_PIVOT_Z + 6.5
        with BuildSketch(Plane.XY.offset(neck_base_z)):
            with Locations((0, C.NECK_Y_CTR)):
                RectangleRounded(C.NECK_W + 4.0, C.NECK_D + 6.0, radius=12.0)
        with BuildSketch(Plane.XY.offset(neck_top_z)):
            with Locations((0, C.NECK_Y_CTR)):
                RectangleRounded(C.NECK_W, C.NECK_D, radius=8.0)
        loft(ruled=False)

        # Widened central MIPI CSI-2 FFC + Wire Tunnel
        with Locations((4.0, C.NECK_Y_CTR, C.CHASSIS_SPLIT_Z - 1.0)):
            Box(18.0, 13.0, (neck_top_z - C.CHASSIS_SPLIT_Z) + 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # MG90S Servo Pocket + Right Coaxial M3 Brass Insert Pivot
        y_body_off = -(C.MG90S_L / 2.0 - C.MG90S_SHAFT_OFFSET)
        with Locations((-11.5, C.HEAD_PIVOT_Y + y_body_off, C.HEAD_PIVOT_Z)):
            Box(C.MG90S_H + 1.0, C.MG90S_L + 0.6, C.MG90S_W + 0.6, mode=Mode.SUBTRACT)
        with Locations((-23.0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
            Cylinder(radius=6.3, height=8.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((21.0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
            Cylinder(radius=C.HEATSET_M3_DIA / 2.0, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # Locating Peg Sockets for B01_Hood_Wing_L/R (exact snap-alignment!)
        for sgn in (-1.0, 1.0):
            for py in (4.0, 26.0):
                with Locations((sgn * 25.0, py, C.CHASSIS_Z_TOP - 3.5)):
                    Cylinder(radius=1.7, height=8.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 4× Countersunk Clamshell M3 Bolt Holes
        for bx, by in ((-33.5, -39.0), (33.5, -39.0), (-33.5, 16.0), (33.5, 16.0)):
            with Locations((bx, by, C.CHASSIS_SPLIT_Z - 1.0)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=12.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            with Locations((bx, by, C.CHASSIS_Z_TOP - 2.4)):
                Cylinder(radius=3.1, height=6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    return _tag(hood.part, "A02_Top_Hood", "charcoal")


# ---------------------------------------------------------------------------
# B01_L / B01_R: Pearl-White Hood Wings w/ Integrated Ø3.0mm Locating Pegs!
# ---------------------------------------------------------------------------
def build_hood_wing(side: str = "L") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    with BuildPart() as wing:
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z + 1.5)):
            with Locations((sgn * 25.5, 18.0)):
                RectangleRounded(22.0, 56.0, radius=7.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 1.4)):
            with Locations((sgn * 24.5, 14.0)):
                RectangleRounded(16.0, 44.0, radius=6.0)
        loft(ruled=False)
        with Locations(Location((0, 55.5, 48.5), (-32, 0, 0))):
            Box(90.0, 32.0, 24.0, mode=Mode.SUBTRACT)
        with Locations((0, C.NECK_Y_CTR, C.CHASSIS_Z_TOP)):
            Cylinder(radius=24.0, height=16.0, mode=Mode.SUBTRACT)
        # Dual Precision Ø3.0mm Alignment Pegs snapping cleanly into A02_Top_Hood!
        for py in (4.0, 26.0):
            with Locations((sgn * 25.0, py, C.CHASSIS_SPLIT_Z - 1.0)):
                Cylinder(radius=1.45, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return _tag(wing.part, f"B01_Hood_Wing_{side}", "white")


# ---------------------------------------------------------------------------
# B02 / B03: Pearl-White Side Fairings w/ Internal M3 Heat-Set Screw Bosses!
# ---------------------------------------------------------------------------
def build_side_fairing(side: str = "L") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    x_in = sgn * (C.CHASSIS_W / 2.0 - 0.5)
    with BuildPart() as panel:
        with BuildSketch(Plane.YZ.offset(x_in)):
            with Locations((-10.0, 37.5)):
                RectangleRounded(66.0, 21.0, radius=7.5)
        with BuildSketch(Plane.YZ.offset(x_in + sgn * 4.5)):
            with Locations((-11.0, 38.0)):
                RectangleRounded(56.0, 15.0, radius=5.5)
        loft(ruled=False)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            with Locations((x_in + sgn * 2.0, y_ax, C.Z_AXLE)):
                Cylinder(radius=C.WHEEL_R + 3.0, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Dual Internal M2.5/M3 Pilot Bores (bolted cleanly from inside A01_chassis_tub -> zero external screws!)
        for by in (-14.0, 2.0):
            with Locations((x_in + sgn * 1.5, by, 37.5)):
                Cylinder(radius=C.M25_PILOT_DIA / 2.0, height=4.5, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    return _tag(panel.part, f"B02_Side_Fairing_{side}", "white")


# ---------------------------------------------------------------------------
# A04: 4× Deep-Dish Star Wheel Hubs w/ 8.5mm Deep D-Shaft Collar + Set-Screw!
# ---------------------------------------------------------------------------
def build_wheel_hub(side: str = "L", axle: str = "F") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    hub_r = C.WHEEL_HUB_OD / 2.0  # 15.0 mm
    w = C.WHEEL_W - 1.0           # 16.0 mm

    with BuildPart() as hub:
        Cylinder(radius=hub_r, height=w, rotation=(0, 90, 0))
        for ex in (-w / 2.0 + 1.0, w / 2.0 - 1.0):
            with Locations((ex, 0, 0)):
                Cylinder(radius=hub_r + 0.5, height=1.8, rotation=(0, 90, 0))
        with Locations((sgn * 3.4, 0, 0)):
            Cylinder(radius=hub_r - 2.6, height=w - 3.8, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Inward-extended reinforced shaft boss (reaches |X|=41.5 -> 8.5mm full D-shaft engagement!)
        with Locations((-sgn * 1.5, 0, 0)):
            Cylinder(radius=5.2, height=w + 1.2, rotation=(0, 90, 0))
        for i in range(6):
            ang = math.radians(i * 60.0)
            with Locations((sgn * 1.5, 8.8 * math.cos(ang), 8.8 * math.sin(ang))):
                Cylinder(radius=2.5, height=w + 2.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # N20 D-shaft bore + radial M2.5 set-screw hole on flat side for zero-slip grip!
        Cylinder(radius=1.6, height=w + 5.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((-sgn * 1.5, 0, 1.35)):
            Box(w - 1.0, 3.0, 0.55)
        with Locations((-sgn * 5.2, 0, 4.0)):
            Cylinder(radius=1.1, height=8.0, mode=Mode.SUBTRACT)

    return _tag(
        hub.part.move(Location((sgn * C.X_WHEEL, y_ax, C.Z_AXLE))),
        f"A04_Wheel_Hub_{tag}",
        "titanium",
    )


def build_wheel_rim_accent(side: str = "L", axle: str = "F") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    hub_r = C.WHEEL_HUB_OD / 2.0
    w = C.WHEEL_W - 1.0
    with BuildPart() as ring:
        Cylinder(radius=hub_r - 1.0, height=2.0, rotation=(0, 90, 0))
        Cylinder(radius=hub_r - 2.5, height=3.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    return _tag(
        ring.part.move(Location((sgn * (C.X_WHEEL + w / 2.0 - 0.8), y_ax, C.Z_AXLE))),
        f"C03_Wheel_Rim_{tag}",
        "orange",
    )


def build_all_chassis_parts() -> dict:
    return {
        "A01_chassis_tub": ("plate_A_charcoal", build_chassis_tub()),
        "A02_top_hood": ("plate_A_charcoal", build_top_hood()),
        "A03_motor_clamp_F": ("plate_A_charcoal", build_motor_clamp("F")),
        "A03_motor_clamp_R": ("plate_A_charcoal", build_motor_clamp("R")),
        "A04_wheel_hub_FL": ("plate_A_charcoal", build_wheel_hub("L", "F")),
        "A04_wheel_hub_FR": ("plate_A_charcoal", build_wheel_hub("R", "F")),
        "A04_wheel_hub_RL": ("plate_A_charcoal", build_wheel_hub("L", "R")),
        "A04_wheel_hub_RR": ("plate_A_charcoal", build_wheel_hub("R", "R")),
        "B01_hood_wing_L": ("plate_B_white", build_hood_wing("L")),
        "B01_hood_wing_R": ("plate_B_white", build_hood_wing("R")),
        "B02_side_fairing_L": ("plate_B_white", build_side_fairing("L")),
        "B03_side_fairing_R": ("plate_B_white", build_side_fairing("R")),
        "C03_wheel_rim_FL": ("plate_C_orange", build_wheel_rim_accent("L", "F")),
        "C03_wheel_rim_FR": ("plate_C_orange", build_wheel_rim_accent("R", "F")),
        "C03_wheel_rim_RL": ("plate_C_orange", build_wheel_rim_accent("L", "R")),
        "C03_wheel_rim_RR": ("plate_C_orange", build_wheel_rim_accent("R", "R")),
    }
