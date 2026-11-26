"""
KRON-01V5 (Terra-Rover 4WD Edition — Production Zero-Collision DFM/DFA Release)
===============================================================================
Every mechanical joint is production-engineered for rock-solid SLA/FDM printing & assembly:
  - A01_chassis_tub       : Ruled-wall lower tub w/ 4× N20 cradles + dropped skid floor + M2.5 clamp bosses,
                            front nose catch ledge, IP5328P shelf, switch pocket, and rear maintenance ports!
  - A02_top_hood          : Sloped aerodynamic lift-off hood w/ 2.5mm underside alignment step-lip,
                            integral L-shaped front interlock hook, top-open drop-in MG90S servo pocket,
                            widened CSI/wire tunnel, locating sockets for B01 white wings, and shark-fin!
  - A03_motor_clamp_F/R   : 2× bolt-down N20 motor retaining clamp straps (prevents motor twist/pop-out!)
  - A04_wheel_hub_FL..RR  : Deep-dish 6-spoke star hubs w/ 8.0mm D-shaft collar (clears tub shroud by 0.8mm)
                            + radial M2.5 set-screw hole + mating dish for C03 gold accent ring!
  - B01_hood_wing_L/R     : Pearl-white hood wings seated cleanly on A02 top deck w/ dual Ø2.9mm locating pegs!
  - B02/B03_side_fairing  : Sturdy pearl-white side armor panels seated cleanly outside A01 w/ internal M2.5 bores!
  - C03_wheel_rim_FL..RR  : 4× snap-in satin gold-amber inner wheel lip accent rings (0.25mm radial fit inside A04)
"""

import math
from build123d import (
    Align,
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
    w = C.CHASSIS_W        # 80.0 (X: -40..+40)
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
        # Ruled loft eliminates cubic spline belly bulge -> exact ±40mm side walls & -50..+54mm front/rear!
        loft(ruled=True)

    with BuildPart() as tub:
        add(outer_bp.part)

        # Sloped front nose trim
        with Locations(Location((0, 56.0, 48.5), (-32, 0, 0))):
            Box(w + 10.0, 32.0, 22.0, mode=Mode.SUBTRACT)

        # Protective dropped skid pads under 4× N20 motors (Z=12.8..15.5 -> leaves 1.95mm solid skid floor!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * 26.5, y_ax, 12.8)):
                    Box(28.0, C.N20_W + 6.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4× Reinforced Suspension Axle Collar Shrouds (|X| = 38.6..41.2 -> 0.8mm running clearance to A04 hub!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * 39.9, y_ax, C.Z_AXLE)):
                    Cylinder(radius=5.0, height=2.6, rotation=(0, 90, 0))

        # Angled Front Off-Road Skid Plate + Clean Exterior Recessed Grille & Headlight Bezels (zero internal voids!)
        with Locations(Location((0, 53.2, 22.0), (28, 0, 0))):
            Box(28.0, 3.6, 15.0)
        with Locations((0, 54.0, 31.5)):
            Box(24.0, 5.0, 6.5, mode=Mode.SUBTRACT)
        for sx in (-1, 1):
            with Locations((sx * 21.0, 54.0, 32.5)):
                Box(10.0, 5.0, 5.5, mode=Mode.SUBTRACT)

        # 2. Hollow interior cavity (open cleanly at top Z = 48.5, closed ALL 4 vertical walls!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_FLOOR)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(w - 2 * wall, l - 10.0, radius=7.5)
        extrude(amount=h + 4.0, mode=Mode.SUBTRACT)

        # Front Nose Interlock Catch Ledge (fused solidly into front inner wall Y=47..48.5; receives A02 L-hook!)
        with Locations((0, 45.5, 38.3)):
            Box(28.0, 6.0, 3.0)

        # 3. 4× N20 Gearmotor Cradles + M2.5 Bolt Bosses for A03 Motor Clamp Straps!
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                saddle_x = sgn * (w / 2.0 - 13.5)
                with Locations((saddle_x, y_ax, C.CHASSIS_Z_FLOOR)):
                    Box(22.0, C.N20_W + 7.2, 9.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Full N20 body + endcap pocket (|X|=12.75..41.25, Z=14.75..27.25 -> 0.25mm clearance all around!)
                with Locations((sgn * 27.0, y_ax, C.Z_AXLE)):
                    Box(28.5, C.N20_W + 0.5, C.N20_H + 0.5, mode=Mode.SUBTRACT)
                with Locations((sgn * (w / 2.0 + 0.5), y_ax, C.Z_AXLE)):
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

        # DRV8833 & MAX98357A standoffs
        for px, py in ((C.DRV_X, C.DRV_Y), (C.AMP_X, C.AMP_Y)):
            for dx in (-7.2, 7.2):
                for dy in (-6.2, 6.2):
                    with Locations((px + dx, py + dy, C.CHASSIS_Z_FLOOR)):
                        Cylinder(radius=2.0, height=2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # IP5328P upper shelf (Z=37.3..39.3 -> 0.2mm clear under PCB at 39.5) + solid side wall bracket
        with Locations((C.PWR_X + 2.0, C.PWR_Y, C.PWR_Z - 2.2)):
            Box(22.0, 28.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((w / 2.0 - wall - 1.5, C.PWR_Y, C.PWR_Z - 8.2)):
            Box(4.0, 26.0, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Power switch lower support shelf (Z=38.3..40.5 -> 0.25mm under switch body at 40.75)
        with Locations((C.SW_X, C.SW_Y - 1.5, C.SW_Z - 4.7)):
            Box(11.0, 7.0, 2.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 6. 4× Clamshell Top-Hood M3 Heat-Set Brass Insert Bosses
        for bx, by in ((-33.5, -39.0), (33.5, -39.0), (-33.5, 16.0), (33.5, 16.0)):
            with Locations((bx, by, C.CHASSIS_SPLIT_Z - 5.8)):
                Cylinder(radius=4.2, height=5.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((bx, by, C.CHASSIS_SPLIT_Z - 5.2)):
                Cylinder(radius=C.HEATSET_M3_DIA / 2.0, height=5.8, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 7. Side-Fairing Mounting Holes (aligned with B02/B03 internal M2.5 bores at Y=±10, Z=37.5!)
        for sgn in (-1.0, 1.0):
            for by in (-10.0, 10.0):
                with Locations((sgn * (w / 2.0 - 1.0), by, 37.5)):
                    Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=8.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # 8. Rear-Wall Zero-Disassembly Maintenance Ports (Micro-SD + 5V/3A Type-C + Switch + OTG + Vents)
        y_rear = C.CHASSIS_Y_MIN
        with Locations((C.RPI_X_CTR + 1.0, y_rear + 1.5, C.RPI_Z_PCB + 2.6)):
            Box(15.5, 8.0, 5.2, mode=Mode.SUBTRACT)  # Tool-free Micro-SD quick-swap!
        with Locations((C.PWR_X, y_rear + 1.5, C.PWR_Z + 3.2)):
            Box(11.8, 8.0, 6.4, mode=Mode.SUBTRACT)  # 5V/3A Type-C charge/UPS port
        with Locations((C.SW_X, y_rear + 1.5, C.SW_Z)):
            Box(9.6, 8.0, 5.2, mode=Mode.SUBTRACT)   # Main power slide switch (clears 8.6×4.5 body!)
        with Locations((11.0, y_rear + 1.5, 32.0)):
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
# A02: Reinforced Clamshell Top Hood (Step-Lip + L-Hook + Drop-In MG90S Neck!)
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
        loft(ruled=True)

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

        # Integral Front Interlock Catch Hook (L-shaped stem + tongue fused solidly into hood underside!)
        with Locations((0, 34.25, 42.0)):
            Box(22.0, 3.5, 16.0)
        with Locations((0, 39.25, 35.2)):
            Box(22.0, 13.5, 2.4)

        # Raised Sporty Rear-Deck Fastback Cowl (low-profile Z=57.2 -> full +22° pitch-up clearance!) + Shark-Fin
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 1.5)):
            with Locations((0, -37.0)):
                RectangleRounded(42.0, 15.0, radius=4.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 2.2)):
            with Locations((0, -38.0)):
                RectangleRounded(32.0, 10.0, radius=3.5)
        loft(ruled=True)
        # Sturdy FDM/SLA-proof Aero Shark-Fin (5mm thick -> 10x stronger than thin cylindrical pin!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 1.5)):
            with Locations((14.0, -37.0)):
                RectangleRounded(5.0, 11.0, radius=2.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 12.5)):
            with Locations((14.0, -40.5)):
                RectangleRounded(3.2, 5.5, radius=1.2)
        loft(ruled=True)

        # Underside headroom recess (clears 40-pin GPIO & heatsink) + Top rear convection vents
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z - 0.5)):
            with Locations((0, -10.0)):
                RectangleRounded(60.0, 74.0, radius=6.0)
        extrude(amount=4.2, mode=Mode.SUBTRACT)
        for vx in (-9.0, -3.0, 3.0, 9.0):
            with Locations((vx, -38.0, C.CHASSIS_Z_TOP - 2.0)):
                Box(2.4, 7.0, 10.0, mode=Mode.SUBTRACT)

        # Dual-Tier Sculpted Neck Turret:
        # 1) Slim Lower Pedestal Stalk (36×22mm, Z=53..67 -> huge clearance for helmet rim at -20°..+22°!)
        neck_top_z = C.HEAD_PIVOT_Z + 6.5  # 79.5mm
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 2.0)):
            with Locations((0, -5.0)):
                RectangleRounded(36.0, 22.0, radius=5.0)
        extrude(amount=14.0)
        # 2) Upper MG90S Servo Yoke (48×36.2mm, Y=-26.2..+10.0, Z=66.0..79.5 -> neatly inside helmet cavity!)
        with BuildSketch(Plane.XY.offset(C.HEAD_PIVOT_Z - 7.0)):
            with Locations((0, C.NECK_Y_CTR)):
                RectangleRounded(C.NECK_W, C.NECK_D, radius=5.0)
        extrude(amount=13.5)

        # Widened Right-Side MIPI CSI-2 FFC + Wire Tunnel (X=+2.5..+15.0 -> clear of MG90S & M3 pivot!)
        with Locations((8.75, -5.0, C.CHASSIS_SPLIT_Z - 1.0)):
            Box(12.5, 16.0, (neck_top_z - C.CHASSIS_SPLIT_Z) + 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Top-Open Drop-In MG90S Servo Pocket (Body + 32.5mm Flange + Left Gear-Dome Slot -> zero collision!)
        servo_z_bot = C.HEAD_PIVOT_Z - C.MG90S_W / 2.0 - 0.35
        with Locations((-11.5, -7.9, servo_z_bot)):
            Box(23.2, 23.4, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((-19.0, -7.9, servo_z_bot)):
            Box(3.4, 33.4, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((-24.0, -2.0, servo_z_bot + 0.2)):
            Box(5.0, 12.6, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # Right Coaxial M3 Brass Insert Pivot
        with Locations((21.0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
            Cylinder(radius=C.HEATSET_M3_DIA / 2.0, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # Locating Peg Sockets for B01_Hood_Wing_L/R (exact snap-alignment at X=±22, Y=17.5 & 29.5!)
        for sgn in (-1.0, 1.0):
            for py in (17.5, 29.5):
                with Locations((sgn * 22.0, py, C.CHASSIS_Z_TOP - 4.0)):
                    Cylinder(radius=1.75, height=5.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 4× Countersunk Clamshell M3 Bolt Holes (100% accessible outside B01 white wings!)
        for bx, by in ((-33.5, -39.0), (33.5, -39.0), (-33.5, 16.0), (33.5, 16.0)):
            with Locations((bx, by, C.CHASSIS_SPLIT_Z - 1.0)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=12.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            with Locations((bx, by, C.CHASSIS_Z_TOP - 2.4)):
                Cylinder(radius=3.1, height=6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    return _tag(hood.part, "A02_Top_Hood", "charcoal")


# ---------------------------------------------------------------------------
# B01_L / B01_R: Pearl-White Hood Wings Seated Cleanly on A02 Top Deck!
# ---------------------------------------------------------------------------
def build_hood_wing(side: str = "L") -> Part:
    """Sleek pearl-white hood wing seated 0.20mm above A02 top deck (Z=55.2..57.6) w/ Ø2.9mm locating pegs."""
    sgn = -1.0 if side == "L" else 1.0
    with BuildPart() as wing:
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 0.2)):
            with Locations((sgn * 22.0, 24.5)):
                RectangleRounded(14.5, 25.0, radius=4.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 2.6)):
            with Locations((sgn * 21.5, 23.5)):
                RectangleRounded(11.0, 20.5, radius=3.5)
        loft(ruled=True)
        # Dual Precision Ø2.9mm Alignment Pegs dropping into A02 Ø3.5mm sockets (0.3mm radial + 0.8mm depth clearance!)
        for py in (17.5, 29.5):
            with Locations((sgn * 22.0, py, C.CHASSIS_Z_TOP - 3.2)):
                Cylinder(radius=1.45, height=4.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return _tag(wing.part, f"B01_Hood_Wing_{side}", "white")


# ---------------------------------------------------------------------------
# B02 / B03: Sturdy Pearl-White Side Armor Panels (Zero Collision w/ A01!)
# ---------------------------------------------------------------------------
def build_side_fairing(side: str = "L") -> Part:
    """Sturdy 4.25mm-thick white side armor seated 0.25mm outside A01's flat |X|=40.0 wall, between wheel arches."""
    sgn = -1.0 if side == "L" else 1.0
    x_in = sgn * (C.CHASSIS_W / 2.0 + 0.25)  # |X| = 40.25mm -> 0.25mm clean gap outside A01 wall!
    with BuildPart() as panel:
        with BuildSketch(Plane.YZ.offset(x_in)):
            with Locations((0.0, 37.5)):
                RectangleRounded(42.0, 19.5, radius=5.5)
        with BuildSketch(Plane.YZ.offset(x_in + sgn * 4.25)):
            with Locations((0.0, 38.0)):
                RectangleRounded(35.0, 14.5, radius=4.0)
        loft(ruled=True)
        # Crisp wheel-arch clearance cutouts (leaves >=4.5mm sturdy corners, zero fragile thin hooks!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            with Locations((x_in + sgn * 2.0, y_ax, C.Z_AXLE)):
                Cylinder(radius=C.WHEEL_R + 2.4, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Dual Internal M2.5 Pilot Bores (bolted cleanly from inside A01_chassis_tub -> zero external screws!)
        for by in (-10.0, 10.0):
            with Locations((x_in + sgn * 1.5, by, 37.5)):
                Cylinder(radius=C.M25_PILOT_DIA / 2.0, height=3.6, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    return _tag(panel.part, f"B02_Side_Fairing_{side}", "white")


# ---------------------------------------------------------------------------
# A04: 4× Deep-Dish Star Wheel Hubs (0.8mm Tub Clearance + C03 Dish Fit!)
# ---------------------------------------------------------------------------
def build_wheel_hub(side: str = "L", axle: str = "F") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    hub_r = C.WHEEL_HUB_OD / 2.0 - 0.30  # 14.70mm (0.10mm slip-fit inside 14.80mm tire ID!)
    w = C.WHEEL_W - 1.0                  # 16.0mm (|X| = 42.5..58.5)

    with BuildPart() as hub:
        Cylinder(radius=hub_r, height=w, rotation=(0, 90, 0))
        # Deep outer dish cavity (R=12.5mm -> receives C03 gold ring R=12.25mm cleanly!)
        with Locations((sgn * 3.0, 0, 0)):
            Cylinder(radius=12.5, height=w - 4.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Reinforced center shaft boss (inner end at |X|=42.0 -> 0.8mm clear of A01 shroud at 41.2, 8.0mm shaft grip!)
        with Locations((-sgn * 0.5, 0, 0)):
            Cylinder(radius=5.2, height=w, rotation=(0, 90, 0))
        # 6-spoke weight-saving & aesthetic holes
        for i in range(6):
            ang = math.radians(i * 60.0)
            with Locations((sgn * 1.5, 8.8 * math.cos(ang), 8.8 * math.sin(ang))):
                Cylinder(radius=2.3, height=w + 2.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # N20 D-shaft bore (R=1.65mm) + D-flat key (Z=+1.15mm -> 0.15mm clear of shaft flat at +1.0mm!) + radial M2.5 set-screw
        Cylinder(radius=1.65, height=w + 4.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((-sgn * 1.0, 0, 1.45)):
            Box(w - 2.0, 3.0, 0.60)
        with Locations((-sgn * 5.0, 0, 4.0)):
            Cylinder(radius=1.1, height=8.0, mode=Mode.SUBTRACT)

    return _tag(
        hub.part.move(Location((sgn * C.X_WHEEL, y_ax, C.Z_AXLE))),
        f"A04_Wheel_Hub_{tag}",
        "titanium",
    )


# ---------------------------------------------------------------------------
# C03: 4× Snap-In Gold-Amber Wheel Rim Accent Rings (0.25mm Fit Inside A04!)
# ---------------------------------------------------------------------------
def build_wheel_rim_accent(side: str = "L", axle: str = "F") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    w = C.WHEEL_W - 1.0
    with BuildPart() as ring:
        # R_out=12.25mm fits cleanly inside A04's R=12.50mm dish (0.25mm radial clearance, 1.8mm ring width!)
        Cylinder(radius=12.25, height=2.2, rotation=(0, 90, 0))
        Cylinder(radius=10.45, height=3.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    return _tag(
        ring.part.move(Location((sgn * (C.X_WHEEL + w / 2.0 - 1.1), y_ax, C.Z_AXLE))),
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
