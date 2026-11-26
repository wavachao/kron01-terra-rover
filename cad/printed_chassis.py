"""
KRON-01V5 (Terra-Rover 4WD Edition — Mortise-and-Tenon Quick-Release + Captive Hex Nut Release)
================================================================================================
Zero-soldering, zero-heat-set-insert, SLA-resin & FDM production chassis parts:
  - A01_chassis_tub       : Ruled-wall lower tub w/ 4× reinforced side slide-lock catch blocks (ZERO fragile
                            cantilevered bosses!), front nose catch ledge, rear tapered dovetail mortise block,
                            external vertical dovetail rails for B02/B03 side armor, and captive M2.5 hex nut
                            slots for RPi Zero 2WH standoffs & N20 motor clamps!
  - A02_top_hood          : Sloped aerodynamic lift-off hood w/ 5-point rigid L-hook slide-lock (4 side +
                            1 front nose, ΔY=+5mm forward to lock), rear dovetail keyway, side fender eaves
                            trapping B02/B03 vertically, blind-front dovetail slots for B01 wings, 21.4mm
                            vertical DuPont headroom, and top-drop captive M3 hex nut slot for right head pivot!
  - A10_hood_lock_key     : Tapered rear dovetail wedge lock pin (slides straight down into rear fastback
                            cowl to lock A02↔A01 in solid shear — 3-second tool-free open/close!)
  - A03_motor_clamp_F/R   : 2× bolt-down N20 motor retaining clamp straps (bolts into captive M2.5 metal nuts!)
  - A04_wheel_hub_FL..RR  : Deep-dish 6-spoke star hubs w/ 8.0mm D-shaft collar + captive M2 hex nut radial lock!
  - B01_hood_wing_L/R     : Pearl-white hood wings w/ blind-front sliding dovetail tenons (zero glue/screws!)
  - B02/B03_side_fairing  : Sturdy pearl-white side armor panels w/ vertical sliding dovetail mortise (zero screws!)
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
    Polygon,
    Rectangle,
    RectangleRounded,
    add,
    extrude,
    loft,
)
import config as C

# Shared mortise-and-tenon coordinates for A01 <-> A02 <-> A10
SIDE_RAIL_YS = (-25.0, 15.0)


def _col(name: str) -> Color:
    r, g, b, a = C.COLORS[name]
    return Color(r, g, b, a)


def _tag(shape, label: str, color_key: str):
    shape.label = label
    shape.color = _col(color_key)
    return shape


def _build_rear_dovetail_prism(z_bot: float, z_top: float, clearance: float = 0.0) -> Part:
    """
    Build the tapered trapezoidal dovetail prism for the A10 rear hood lock key / mortise slot.
    - Wider at rear (-Y) than front (+Y) -> dovetail interlocking against both ±X and ±Y.
    - Gently tapered (~1.5 deg) narrower toward bottom (-Z) -> snug, rattle-free thumb-press fit!
    - clearance > 0 expands the prism outward to cut the matching mortise slot in A01/A02.
    """
    c = clearance
    # Nominal shaft dimensions at z_ref_bot=54.3 and z_ref_top=68.7
    z0, z1 = 54.3, 68.7

    def _lerp(v0: float, v1: float, z: float) -> float:
        t = (z - z0) / (z1 - z0)
        return v0 + t * (v1 - v0)

    def _trap_pts(z: float):
        y_rear = _lerp(-45.2, -45.5, z) - c
        y_front = _lerp(-41.4, -41.1, z) + c
        hw_rear = _lerp(5.0, 5.4, z) + c
        hw_front = _lerp(3.8, 4.2, z) + c
        return [
            (-hw_rear, y_rear),
            (hw_rear, y_rear),
            (hw_front, y_front),
            (-hw_front, y_front),
        ]

    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(z_bot)):
            Polygon(*_trap_pts(z_bot))
        with BuildSketch(Plane.XY.offset(z_top)):
            Polygon(*_trap_pts(z_top))
        loft(ruled=True)
    return bp.part


# ---------------------------------------------------------------------------
# A01: Mortise-and-Tenon Clamshell Lower Chassis Tub (Zero Cantilever Bosses!)
# ---------------------------------------------------------------------------
def build_chassis_tub() -> Part:
    w = C.CHASSIS_W        # 84.0 (X: -42..+42)
    l = C.CHASSIS_L        # 104.0 (Y: -50..+54)
    yc = C.CHASSIS_Y_CTR   # +2.0
    h = C.CHASSIS_SPLIT_Z - C.CHASSIS_Z_BOT  # 45.0 mm (Z = 15.0..60.0)
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
        loft(ruled=True)

    with BuildPart() as tub:
        add(outer_bp.part)

        # Sloped front nose trim (stays outside Y=+49.5mm -> solid closed >=2.5mm front wall up to split line!)
        with Locations(Location((0, 67.0, C.CHASSIS_SPLIT_Z + 2.0), (-32, 0, 0))):
            Box(w + 10.0, 32.0, 22.0, mode=Mode.SUBTRACT)

        # Protective dropped skid pads under 4× N20 motors (Z=12.8..15.5 -> leaves 1.95mm solid skid floor!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * (w / 2.0 - 13.5), y_ax, 12.8)):
                    Box(28.0, C.N20_W + 6.0, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4× Reinforced Suspension Axle Collar Shrouds (|X| = w/2-1.4..w/2+1.2 -> 0.8mm clearance to A04 hub!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * (w / 2.0 - 0.1), y_ax, C.Z_AXLE)):
                    Cylinder(radius=5.0, height=2.6, rotation=(0, 90, 0))

        # External Vertical Sliding Dovetail Rails for B02/B03 Side White Armor (ZERO screws!)
        for sgn in (-1.0, 1.0):
            with BuildSketch(Plane.YZ.offset(sgn * (w / 2.0 - 0.2))):
                with Locations((0.0, 46.0)):
                    Rectangle(12.0, 23.0)  # Z = 34.5..57.5, Y = -6.0..+6.0
            with BuildSketch(Plane.YZ.offset(sgn * (w / 2.0 + 2.0))):
                with Locations((0.0, 46.0)):
                    Rectangle(15.2, 23.0)  # 38.6° dovetail tenon!
            loft(ruled=True)

        # Angled Front Off-Road Skid Plate + Clean Exterior Recessed Grille & Headlight Bezels
        with Locations(Location((0, 53.2, 22.0), (28, 0, 0))):
            Box(28.0, 3.6, 15.0)
        with Locations((0, 54.0, 34.5)):
            Box(26.0, 5.0, 7.5, mode=Mode.SUBTRACT)
        for sx in (-1, 1):
            with Locations((sx * 22.5, 54.0, 35.5)):
                Box(10.5, 5.0, 6.0, mode=Mode.SUBTRACT)

        # 2. Hollow interior cavity (inner width 79.0mm -> fits ANY 74.5~77.5mm Taobao 18650 holder!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_FLOOR)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(w - 2 * wall, l - 10.0, radius=7.5)
        extrude(amount=h + 4.0, mode=Mode.SUBTRACT)

        # Front Nose Interlock Catch Ledge (fused solidly into front inner wall Y=43..48.5; receives A02 front L-hook!)
        with Locations((0, 45.75, C.CHASSIS_SPLIT_Z - 10.1)):
            Box(28.0, 5.5, 3.2)

        # 3. 4× Reinforced Side-Wall Slide-Lock Catch Blocks + Vertical End-Stop Ribs (ZERO cantilevered bosses!)
        #    A02's 4 L-hooks drop behind these blocks at ΔY=-5mm, then slide +5mm forward to lock rigidly under Z=53.5!
        x_in = w / 2.0 - wall  # 39.5 mm
        for sgn in (-1.0, 1.0):
            for y_rail in SIDE_RAIL_YS:
                # 6.0mm-thick horizontal catch block fused solidly into side wall (|X|=34.5..40.5, Z=53.5..59.5)
                with Locations((sgn * (x_in - 2.0), y_rail, C.CHASSIS_SPLIT_Z - 6.5)):
                    Box(6.0, 8.0, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Solid vertical end-stop & structural rib at front of rail (Z=48.0..59.5 -> clears IP5328P & 18650!)
                with Locations((sgn * (x_in - 2.0), y_rail + 5.8, C.CHASSIS_SPLIT_Z - 12.0)):
                    Box(6.0, 3.8, 11.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4. Rear Reinforced Dovetail Lock Mortise Block (X=-10..+10, Y=-48.0..-39.8, Z=53.0..60.0 -> clears RPi!)
        with Locations((0.0, -43.9, C.CHASSIS_SPLIT_Z - 7.0)):
            Box(20.0, 8.2, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Tapered dovetail keyway receiving A10_Hood_Lock_Key (+0.22mm sliding clearance per side!)
        add(_build_rear_dovetail_prism(C.CHASSIS_SPLIT_Z - 6.0, C.CHASSIS_SPLIT_Z + 1.0, clearance=0.22), mode=Mode.SUBTRACT)

        # 5. 4× N20 Gearmotor Cradles + Captive M2.5 Hex Nut Slots for A03 Motor Clamp Straps!
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                saddle_x = sgn * (w / 2.0 - 13.5)
                with Locations((saddle_x, y_ax, C.CHASSIS_Z_FLOOR)):
                    Box(22.0, C.N20_W + 9.6, 9.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Full N20 body + endcap pocket (0.25mm clearance all around!)
                with Locations((sgn * (w / 2.0 - 13.0), y_ax, C.Z_AXLE)):
                    Box(28.5, C.N20_W + 0.5, C.N20_H + 0.5, mode=Mode.SUBTRACT)
                with Locations((sgn * (w / 2.0 + 0.5), y_ax, C.Z_AXLE)):
                    Cylinder(radius=3.6, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                # Dual M2.5 clearance bores + side-entry Captive M2.5 Hex Nut Slots (zero self-tapping in resin!)
                bx_clamp = sgn * (w / 2.0 - 12.0)
                for dy_b in (-7.2, 7.2):
                    with Locations((bx_clamp, y_ax + dy_b, C.CHASSIS_Z_FLOOR + 1.5)):
                        Cylinder(radius=C.M25_CLEAR_DIA / 2.0, height=9.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                    # Side-entry hex nut slot opening cleanly toward outer Y face of saddle (Z=20.5..22.8)
                    slot_y = y_ax + dy_b + (1.2 if dy_b > 0 else -1.2)
                    with Locations((bx_clamp, slot_y, C.CHASSIS_Z_FLOOR + 3.0)):
                        Box(C.NUT_M25_AF, 7.2, C.NUT_M25_T, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 6. Dead-Center 18650 Battery Retaining Rails (Y = ±11.8 -> 50/50 CG, fits up to 78mm holder!)
        for sgn_y in (-1.0, 1.0):
            with Locations((0, C.BAT_Y + sgn_y * (C.BAT_HOLDER_W / 2.0 + 1.2), C.CHASSIS_Z_FLOOR)):
                Box(68.0, 2.0, 11.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 7. Official Raspberry Pi Zero 2WH 4× Reinforced M2.5 Standoffs w/ Captive Hex Nut Slots!
        for sx in (-1, 1):
            for sy in (-1, 1):
                px = C.RPI_X_CTR + sx * (C.RPI_HOLE_X / 2.0)
                py = C.RPI_Y_CTR + sy * (C.RPI_HOLE_Y / 2.0)
                # Base pillar + reinforced upper nut-holder collar (R=4.2mm at Z=33.5..41.0 -> zero clash!)
                with Locations((px, py, C.CHASSIS_Z_FLOOR)):
                    Cylinder(radius=3.0, height=C.RPI_Z_PCB - C.CHASSIS_Z_FLOOR, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations((px, py, C.RPI_Z_PCB - 7.5)):
                    Cylinder(radius=4.2, height=7.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations((px, py, C.RPI_Z_PCB - 6.8)):
                    Cylinder(radius=C.M25_CLEAR_DIA / 2.0, height=7.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                # Side-entry captive M2.5 hex nut pocket (slides in from ±X side -> easy drop-in with fingers!)
                with Locations((px + sx * 1.6, py, C.RPI_Z_PCB - 4.8)):
                    Box(7.0, C.NUT_M25_AF, C.NUT_M25_T, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

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

        # 8. Rear-Wall Zero-Disassembly Maintenance Ports (Micro-SD + 5V/3A Type-C + Switch + OTG + Vents)
        y_rear = C.CHASSIS_Y_MIN
        with Locations((C.RPI_X_CTR + 1.0, y_rear + 1.5, C.RPI_Z_PCB + 2.6)):
            Box(15.5, 8.0, 5.2, mode=Mode.SUBTRACT)  # Tool-free Micro-SD quick-swap!
        with Locations((C.PWR_X, y_rear + 1.5, C.PWR_Z + 3.2)):
            Box(11.8, 8.0, 6.4, mode=Mode.SUBTRACT)  # 5V/3A Type-C charge/UPS port
        with Locations((C.SW_X, y_rear + 1.5, C.SW_Z)):
            Box(9.6, 8.0, 5.2, mode=Mode.SUBTRACT)   # Main power slide switch
        with Locations((11.0, y_rear + 1.5, 32.0)):
            Box(11.0, 8.0, 6.0, mode=Mode.SUBTRACT)  # Optional wired USB-OTG pigtail debug port
        for sx in (-12.0, -5.0, 2.0):
            with Locations((sx, y_rear + 1.5, 27.0)):
                Box(3.4, 8.0, 9.0, mode=Mode.SUBTRACT)

    return _tag(tub.part, "A01_Chassis_Tub", "charcoal")


# ---------------------------------------------------------------------------
# A03_F / A03_R: Bolt-Down N20 Motor Clamp Straps (Locks into Captive M2.5 Nuts!)
# ---------------------------------------------------------------------------
def build_motor_clamp(axle: str = "F") -> Part:
    """Rigid M2.5 bolt-down clamp strap locking both N20 gearboxes on an axle into A01 captive nuts."""
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    pad_x = C.CHASSIS_W / 2.0 - 12.0  # 30.0 mm
    with BuildPart() as clamp:
        for sgn in (-1.0, 1.0):
            with Locations((sgn * pad_x, y_ax, C.Z_AXLE + C.N20_H / 2.0 + 1.4)):
                Box(14.0, 20.0, 2.6)
            for dy_b in (-7.2, 7.2):
                with Locations((sgn * pad_x, y_ax + dy_b, C.Z_AXLE + C.N20_H / 2.0 + 1.4)):
                    Cylinder(radius=C.M25_CLEAR_DIA / 2.0, height=5.0, mode=Mode.SUBTRACT)
        # Thin tie-bar bridging left & right clamp pads (clears DRV8833/MAX98357A cleanly above Z=27!)
        with Locations((0, y_ax, C.Z_AXLE + C.N20_H / 2.0 + 1.8)):
            Box(2.0 * pad_x - 10.0, 5.0, 2.2)
    return _tag(clamp.part, f"A03_Motor_Clamp_{axle}", "charcoal")


# ---------------------------------------------------------------------------
# A02: Tool-Free 5-Point Slide-Lock Top Hood (Zero Exterior Screws!)
# ---------------------------------------------------------------------------
def build_top_hood() -> Part:
    w = C.CHASSIS_W
    l = C.CHASSIS_L
    yc = C.CHASSIS_Y_CTR
    x_in = w / 2.0 - C.WALL  # 39.5 mm

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

        # Match sloped front nose cleanly (100% sealed seam with A01 front wall!)
        with Locations(Location((0, 67.0, C.CHASSIS_SPLIT_Z + 2.0), (-32, 0, 0))):
            Box(w + 10.0, 32.0, 22.0, mode=Mode.SUBTRACT)

        # Sleek Side Fender-Flare Eaves (|X|=41.5..44.6, Z=60.0..62.8) trapping B02/B03 vertical dovetails!
        for sgn in (-1.0, 1.0):
            with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z)):
                with Locations((sgn * (w / 2.0 + 1.0), 0.0)):
                    RectangleRounded(5.2, 22.0, radius=2.2)
            with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z + 2.8)):
                with Locations((sgn * (w / 2.0 - 0.5), 0.0)):
                    RectangleRounded(3.0, 18.0, radius=1.2)
            loft(ruled=True)

        # Mid-Side Alignment Ribs (|X|=36.6..39.1, Y=-11.5..+5.0 -> 0.8mm clear of A01 rear stop at ΔY=-5mm!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * (x_in - 1.65), -3.25, C.CHASSIS_SPLIT_Z - 2.5)):
                Box(2.5, 16.5, 2.8, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4× Rigid Side Slide-Lock L-Hooks (drop behind A01 catch blocks at ΔY=-5mm, slide +5mm forward to lock!)
        for sgn in (-1.0, 1.0):
            hx = sgn * (x_in - 2.45)  # |X| = 34.95..39.15 (0.35mm clear inside A01 wall 39.5!)
            for y_rail in SIDE_RAIL_YS:
                # Vertical stem (Y = y_rail-7.8 .. y_rail-4.3 -> 0.30mm clear behind catch block at y_rail-4.0!)
                with Locations((hx, y_rail - 6.05, C.CHASSIS_SPLIT_Z - 10.8)):
                    Box(4.2, 3.5, 11.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Forward-pointing horizontal foot (Y = y_rail-7.8 .. y_rail+0.5, Z = 49.2..53.2 -> 0.30mm under 53.5!)
                with Locations((hx, y_rail - 3.65, C.CHASSIS_SPLIT_Z - 10.8)):
                    Box(4.2, 8.3, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 5th Point: Integral Front Nose Interlock L-Hook (drops at ΔY=-5mm clear of Y=43 ledge, locks 4mm deep!)
        with Locations((0, 36.25, C.CHASSIS_SPLIT_Z - 15.2)):
            Box(22.0, 3.5, 15.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 40.75, C.CHASSIS_SPLIT_Z - 15.2)):
            Box(22.0, 12.5, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Raised Sporty Rear-Deck Fastback Cowl (houses A10 Dovetail Lock Key!) + Aero Shark-Fin
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 1.5)):
            with Locations((0, -39.5)):
                RectangleRounded(42.0, 18.0, radius=4.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 2.2)):
            with Locations((0, -40.5)):
                RectangleRounded(32.0, 13.0, radius=3.5)
        loft(ruled=True)
        # Sturdy Aero Shark-Fin (offset at X=+14 -> clear of center A10 lock key!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 1.5)):
            with Locations((14.0, -37.0)):
                RectangleRounded(5.0, 11.0, radius=2.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 12.5)):
            with Locations((14.0, -40.5)):
                RectangleRounded(3.2, 5.5, radius=1.2)
        loft(ruled=True)

        # Spacious Underside Headroom Recess (Y=-39.5..+27mm, ceiling Z=64.0mm -> 21.4mm above RPi Zero 2WH PCB!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z - 0.5)):
            with Locations((0, -6.25)):
                RectangleRounded(w - 16.0, 66.5, radius=6.0)
        extrude(amount=4.5, mode=Mode.SUBTRACT)

        # Rear Tapered Dovetail Keyway through A02 rear cowl (coaxial with A01 mortise -> locks ΔY=0!)
        add(_build_rear_dovetail_prism(C.CHASSIS_SPLIT_Z - 1.0, C.CHASSIS_Z_TOP + 3.5, clearance=0.22), mode=Mode.SUBTRACT)

        # Twin Rear Convection Vents (flanking A10 lock key at X=±10.5)
        for vx in (-11.0, 11.0):
            with Locations((vx, -36.5, C.CHASSIS_Z_TOP - 2.0)):
                Box(2.8, 7.0, 10.0, mode=Mode.SUBTRACT)

        # Dual-Tier Sculpted Neck Turret:
        # 1) Slim Lower Pedestal Stalk (36×22mm -> huge clearance for helmet rim at -20°..+22°!)
        neck_top_z = C.HEAD_PIVOT_Z + 6.5
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 2.0)):
            with Locations((0, -5.0)):
                RectangleRounded(36.0, 22.0, radius=5.0)
        extrude(amount=14.0)
        # 2) Upper MG90S Servo Yoke (48×36.2mm -> neatly inside helmet cavity!)
        with BuildSketch(Plane.XY.offset(C.HEAD_PIVOT_Z - 7.0)):
            with Locations((0, C.NECK_Y_CTR)):
                RectangleRounded(C.NECK_W, C.NECK_D, radius=5.0)
        extrude(amount=13.5)

        # Widened Right-Side MIPI CSI-2 FFC + Wire Tunnel (X=+2.5..+14.5 -> clear of MG90S & M3 pivot nut!)
        with Locations((8.5, -5.0, C.CHASSIS_SPLIT_Z - 1.0)):
            Box(12.0, 16.0, (neck_top_z - C.CHASSIS_SPLIT_Z) + 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Top-Open Drop-In MG90S Servo Pocket (Body + 32.5mm Flange + Left Gear-Dome Slot -> zero collision!)
        servo_z_bot = C.HEAD_PIVOT_Z - C.MG90S_W / 2.0 - 0.35
        with Locations((-11.5, -7.9, servo_z_bot)):
            Box(23.2, 23.4, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((-19.0, -7.9, servo_z_bot)):
            Box(3.4, 33.4, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((-24.0, -2.0, servo_z_bot + 0.2)):
            Box(5.0, 12.6, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Right Coaxial Head Pivot: M3 Clear Through-Bore + Top-Drop Captive M3 Hex Nut Slot (ZERO heat-set insert!)
        with Locations((20.5, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
            Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=11.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((19.0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z - C.NUT_M3_AF / 2.0)):
            Box(C.NUT_M3_T, C.NUT_M3_AF, 12.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Keyhole Drop-In + Forward Slide Dovetail Mortise Slots for B01_Hood_Wing_L/R (100% hidden under wing!)
        for sgn in (-1.0, 1.0):
            # Front locked dovetail section (Y=24.8..32.4 -> traps B01 tenon in Z & ±X!)
            with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 2.15)):
                with Locations((sgn * 22.0, 28.6)):
                    Rectangle(6.5, 7.6)
            with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 0.2)):
                with Locations((sgn * 22.0, 28.6)):
                    Rectangle(4.9, 7.6)
            loft(ruled=True, mode=Mode.SUBTRACT)
            # Rear straight drop-in keyhole entry pocket (Y=17.4..25.0 -> drop B01 at ΔY=-7.2mm, slide +7.2mm forward!)
            with Locations((sgn * 22.0, 21.2, C.CHASSIS_Z_TOP - 2.15)):
                Box(6.5, 7.6, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    return _tag(hood.part, "A02_Top_Hood", "charcoal")


# ---------------------------------------------------------------------------
# A10: Tapered Rear Dovetail Hood Lock Key (Tool-Free 3-Second Clamshell Lock!)
# ---------------------------------------------------------------------------
def build_hood_lock_key() -> Part:
    """
    Tapered trapezoidal dovetail wedge pin dropping straight down into the rear fastback cowl
    of A02 + A01. Bridges both shells in solid shear to lock the 5-point slide-lock hood!
    """
    z_top = C.CHASSIS_Z_TOP + 2.2  # 68.7 mm (flush with rear fastback cowl deck!)
    with BuildPart() as key:
        # Precision tapered dovetail shaft (Z = 54.3..68.7 -> 0.22mm sliding clearance, snug bottom taper!)
        add(_build_rear_dovetail_prism(C.CHASSIS_SPLIT_Z - 5.7, z_top + 0.3, clearance=0.0))
        # Ergonomic low-profile cyber-spoiler pull cap (Z = 68.7..71.5 -> flush aero styling + easy thumb grip!)
        with BuildSketch(Plane.XY.offset(z_top + 0.25)):
            with Locations((0.0, -43.3)):
                RectangleRounded(16.0, 7.6, radius=2.2)
        with BuildSketch(Plane.XY.offset(z_top + 2.8)):
            with Locations((0.0, -43.3)):
                RectangleRounded(14.0, 6.0, radius=1.8)
        loft(ruled=True)
        # Tactile finger-grip notch on rear overhang for effortless 1-finger pull-up release
        with Locations((0.0, -46.8, z_top + 0.8)):
            Box(12.0, 2.2, 1.4, mode=Mode.SUBTRACT)
    return _tag(key.part, "A10_Hood_Lock_Key", "charcoal")


# ---------------------------------------------------------------------------
# B01_L / B01_R: Pearl-White Hood Wings w/ Keyhole Sliding Dovetail!
# ---------------------------------------------------------------------------
def build_hood_wing(side: str = "L") -> Part:
    """Sleek pearl-white hood wing seated 0.20mm above A02 top deck w/ keyhole sliding dovetail tenon (zero glue!)."""
    sgn = -1.0 if side == "L" else 1.0
    with BuildPart() as wing:
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 0.2)):
            with Locations((sgn * 22.0, 24.5)):
                RectangleRounded(14.5, 25.0, radius=4.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 2.6)):
            with Locations((sgn * 21.5, 23.5)):
                RectangleRounded(11.0, 20.5, radius=3.5)
        loft(ruled=True)
        # Keyhole sliding dovetail tenon (drop straight down at ΔY=-7.2mm, slide +7.2mm forward into Y=25..32!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 1.9)):
            with Locations((sgn * 22.0, 28.5)):
                Rectangle(6.0, 7.0)  # Y = 25.0..32.0 (0.25mm clearance per side inside 6.5/4.9 slot!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 0.4)):
            with Locations((sgn * 22.0, 28.5)):
                Rectangle(4.4, 7.0)
        loft(ruled=True)
    return _tag(wing.part, f"B01_Hood_Wing_{side}", "white")


# ---------------------------------------------------------------------------
# B02 / B03: Zero-Screw Pearl-White Side Armor w/ Vertical Sliding Dovetail!
# ---------------------------------------------------------------------------
def build_side_fairing(side: str = "L") -> Part:
    """
    Sturdy 4.25mm-thick white side armor seated 0.25mm outside A01's flat |X|=42.0 wall.
    Slides straight down (-Z) onto A01's vertical dovetail rail and is locked from above by A02's fender eave!
    """
    sgn = -1.0 if side == "L" else 1.0
    x_in = sgn * (C.CHASSIS_W / 2.0 + 0.25)  # |X| = 42.25mm -> 0.25mm clean gap outside A01 wall!
    with BuildPart() as panel:
        with BuildSketch(Plane.YZ.offset(x_in)):
            with Locations((0.0, 46.5)):
                RectangleRounded(42.0, 26.0, radius=5.0)  # Z = 33.5..59.5 (0.5mm clear under A02 eave at 60.0!)
        with BuildSketch(Plane.YZ.offset(x_in + sgn * 4.25)):
            with Locations((0.0, 46.8)):
                RectangleRounded(35.0, 20.5, radius=4.0)
        loft(ruled=True)
        # Crisp wheel-arch clearance cutouts
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            with Locations((x_in + sgn * 2.0, y_ax, C.Z_AXLE)):
                Cylinder(radius=C.WHEEL_R + 2.4, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Bottom-open / top-blind vertical dovetail mortise groove (0.25mm clearance on all mating faces!)
        with BuildSketch(Plane.YZ.offset(x_in - sgn * 0.45)):
            with Locations((0.0, 45.45)):
                Rectangle(12.5, 24.9)  # Z = 33.0..57.9 (bottom-open -> slides straight down onto Z=34.5..57.5 rail!)
        with BuildSketch(Plane.YZ.offset(x_in + sgn * 2.05)):
            with Locations((0.0, 45.45)):
                Rectangle(15.7, 24.9)
        loft(ruled=True, mode=Mode.SUBTRACT)
    return _tag(panel.part, f"B02_Side_Fairing_{side}", "white")


# ---------------------------------------------------------------------------
# A04: 4× Deep-Dish Star Wheel Hubs (Captive M2 Hex Nut Radial Set-Screw!)
# ---------------------------------------------------------------------------
def build_wheel_hub(side: str = "L", axle: str = "F") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    tag = f"{axle}{side}"
    hub_r = C.WHEEL_HUB_OD / 2.0 - 0.30  # 14.70mm
    w = C.WHEEL_W - 1.0                  # 16.0mm

    with BuildPart() as hub:
        Cylinder(radius=hub_r, height=w, rotation=(0, 90, 0))
        # Deep outer dish cavity (R=12.5mm -> receives C03 gold ring R=12.25mm cleanly!)
        with Locations((sgn * 3.0, 0, 0)):
            Cylinder(radius=12.5, height=w - 4.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Reinforced center shaft boss (inner end clears A01 shroud by 0.8mm, 8.0mm shaft grip!)
        with Locations((-sgn * 0.5, 0, 0)):
            Cylinder(radius=5.4, height=w, rotation=(0, 90, 0))
        # 6-spoke weight-saving & aesthetic holes
        for i in range(6):
            ang = math.radians(i * 60.0)
            with Locations((sgn * 1.5, 9.0 * math.cos(ang), 9.0 * math.sin(ang))):
                Cylinder(radius=2.2, height=w + 2.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # N20 D-shaft bore (R=1.65mm) + D-flat key + radial M2 clearance bore + Captive M2 Hex Nut Slot!
        Cylinder(radius=1.65, height=w + 4.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((-sgn * 1.0, 0, 1.45)):
            Box(w - 2.0, 3.0, 0.60)
        with Locations((-sgn * 4.5, 0, 3.8)):
            Cylinder(radius=C.M2_CLEAR_DIA / 2.0, height=7.0, mode=Mode.SUBTRACT)
        # Inner-face entry captive M2 hex nut slot (Z=2.3..4.2 -> slides in from inner face, 100% open & single-shell!)
        with Locations((-sgn * 6.0, 0, 3.25)):
            Box(6.8, C.NUT_M2_AF, C.NUT_M2_T, mode=Mode.SUBTRACT)

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
        "A10_hood_lock_key": ("plate_A_charcoal", build_hood_lock_key()),
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
