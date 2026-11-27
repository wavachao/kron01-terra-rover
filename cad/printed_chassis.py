"""
KRON-01V6 (ESP32-S3-CAM N16R8 Edition, v2.0.0) — Tolerance-Forgiving Chassis Parts
===================================================================================
Zero-soldering, unified M3 captive hex nuts, generous SLA tolerances (±0.5–0.8mm PCB pockets,
0.28mm sliding mortise-and-tenon clearance), 2-color JLC3DP-optimized chassis (no printed wheels!):
  - A01_chassis_tub       : 94×120mm lower tub w/ transverse Dual-18650 forgiving bay + right mid-waist
                            power console window (Type-C + ON/OFF switch + 4× battery LEDs),
                            2× DRV8833 forgiving cradles (front & rear centers), upper-rear PCA9685A
                            open-center bridge shelf, 4× N20 cradles w/ unified M3 captive nut slots,
                            5-point slide-lock catches, rear A10 dovetail mortise, and B02/B03 rails.
  - A02_top_hood          : Lift-off 5-point slide-lock aerodynamic hood + rear fastback cowl + A10 keyway +
                            side fender eaves + B01 wing keyhole dovetails + widened neck turret +
                            MG90S drop-in pocket + top-drop captive M3 hex nut slot for right head pivot.
  - A10_hood_lock_key     : Rear tapered dovetail lock pin (3-second tool-free hood open/close).
  - A03_motor_clamp_F/R   : 2× unified M3 bolt-down N20 motor retaining clamp straps (identical STL!).
  - B01_hood_wing_L/R     : Pearl-white hood wings w/ keyhole sliding dovetail tenons (zero glue/screws!).
  - B02_side_fairing_L    : Left pearl-white side armor panel w/ vertical sliding dovetail.
  - B03_side_fairing_R    : Right pearl-white side armor panel w/ vertical sliding dovetail + clean waist
                            power console arch cutout exposing Type-C, ON/OFF switch & 4× battery LEDs!
"""

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
SIDE_RAIL_YS = (-16.0, 20.0)


def _col(name: str) -> Color:
    r, g, b, a = C.COLORS[name]
    return Color(r, g, b, a)


def _tag(shape, label: str, color_key: str):
    shape.label = label
    shape.color = _col(color_key)
    return shape


def _build_rear_dovetail_prism(z_bot: float, z_top: float, clearance: float = 0.0) -> Part:
    """
    Tapered trapezoidal dovetail prism for A10 rear hood lock key / mortise slot.
    Positioned at Y = -53.8 .. -49.8 (cleanly behind PCA9685A at Y = -49.0 .. -24.0!).
    """
    c = clearance
    z0, z1 = C.CHASSIS_SPLIT_Z - 5.7, C.CHASSIS_Z_TOP + 2.2

    def _lerp(v0: float, v1: float, z: float) -> float:
        t = (z - z0) / (z1 - z0)
        return v0 + t * (v1 - v0)

    def _trap_pts(z: float):
        y_rear = _lerp(-53.5, -53.8, z) - c
        y_front = _lerp(-49.8, -49.5, z) + c
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
# A01: Mortise-and-Tenon Clamshell Lower Chassis Tub (94×120mm, Unified M3)
# ---------------------------------------------------------------------------
def build_chassis_tub() -> Part:
    w = C.CHASSIS_W        # 94.0 (X: -47..+47)
    l = C.CHASSIS_L        # 120.0 (Y: -58..+62)
    yc = C.CHASSIS_Y_CTR   # +2.0
    h = C.CHASSIS_SPLIT_Z - C.CHASSIS_Z_BOT  # 51.0 mm (Z = 15.0..66.0)
    wall = C.WALL          # 2.5
    x_in = w / 2.0 - wall  # 44.5 mm

    with BuildPart() as outer_bp:
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_BOT)):
            with Locations((0, yc - 0.5)):
                RectangleRounded(w - 4.0, l - 4.0, radius=10.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_BOT + 4.0)):
            with Locations((0, yc)):
                RectangleRounded(w, l, radius=11.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z)):
            with Locations((0, yc)):
                RectangleRounded(w, l, radius=11.0)
        loft(ruled=True)

    with BuildPart() as tub:
        add(outer_bp.part)

        # Sloped aerodynamic front nose bevel (matched seamlessly to A02 front bevel -> >=3.0mm solid wall!)
        with Locations(Location((0, 77.5, C.CHASSIS_SPLIT_Z + 5.0), (-32, 0, 0))):
            Box(w + 10.0, 30.0, 20.0, mode=Mode.SUBTRACT)

        # Protective dropped skid pads under 4× N20 motors
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * (w / 2.0 - 14.0), y_ax, 12.8)):
                    Box(28.0, C.N20_W + 8.0, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4× Reinforced Suspension Axle Collar Shrouds (|X| up to 47.8 -> 0.7mm clear of 43mm wheel at 48.5!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                with Locations((sgn * (w / 2.0 - 0.5), y_ax, C.Z_AXLE)):
                    Cylinder(radius=5.0, height=2.6, rotation=(0, 90, 0))

        # External Vertical Sliding Dovetail Rails for B02 (L: full) & B03 (R: upper rail above power bay!)
        # Left (-X): Z = 38.0..63.0
        with BuildSketch(Plane.YZ.offset(-(w / 2.0 - 0.5))):
            with Locations((0.0, 50.5)):
                Rectangle(12.0, 25.0)
        with BuildSketch(Plane.YZ.offset(-(w / 2.0 + 2.0))):
            with Locations((0.0, 50.5)):
                Rectangle(15.2, 25.0)
        loft(ruled=True)

        # Right (+X): Upper vertical dovetail rail at Z = 50.0..63.0 (100% clear above waist Type-C/Switch/LED window!)
        with BuildSketch(Plane.YZ.offset(w / 2.0 - 0.5)):
            with Locations((0.0, 56.5)):
                Rectangle(12.0, 13.0)
        with BuildSketch(Plane.YZ.offset(w / 2.0 + 2.0)):
            with Locations((0.0, 56.5)):
                Rectangle(15.2, 13.0)
        loft(ruled=True)

        # Clean Integrated Front Off-Road Skid Bumper + Recessed Grille & Headlight Bezels
        with Locations(Location((0, 60.5, 22.0), (24, 0, 0))):
            Box(30.0, 4.0, 14.0)
        with Locations((0, 62.0, 36.5)):
            Box(28.0, 4.4, 8.0, mode=Mode.SUBTRACT)
        for sx in (-1, 1):
            with Locations((sx * 24.5, 62.0, 37.5)):
                Box(11.0, 4.4, 6.2, mode=Mode.SUBTRACT)

        # 2. Hollow interior cavity with matching lower corner bevel (guarantees >=2.5mm solid wall at all 4 bottom corners!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_FLOOR)):
            with Locations((0, 0.0)):
                RectangleRounded(w - 2 * wall - 3.6, l - 13.6, radius=8.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_FLOOR + 3.5)):
            with Locations((0, 0.0)):
                RectangleRounded(w - 2 * wall, l - 10.0, radius=8.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z + 4.0)):
            with Locations((0, 0.0)):
                RectangleRounded(w - 2 * wall, l - 10.0, radius=8.5)
        loft(ruled=True, mode=Mode.SUBTRACT)

        # Front Nose Interlock Catch Ledge (fused solidly into front inner wall Y=49.5..56.0)
        with Locations((0, 52.75, C.CHASSIS_SPLIT_Z - 10.1)):
            Box(28.0, 6.5, 3.2)

        # 3. 4× Reinforced Side-Wall Slide-Lock Catch Blocks + Vertical End-Stop Ribs (clears Dual-18650 & PCA9685A!)
        for sgn in (-1.0, 1.0):
            for y_rail in SIDE_RAIL_YS:
                # 6.0mm-thick horizontal catch block (|X|=39.5..45.5, Z=59.5..65.5)
                with Locations((sgn * (x_in - 2.0), y_rail, C.CHASSIS_SPLIT_Z - 6.5)):
                    Box(6.0, 8.0, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Solid vertical end-stop rib (Z=54.0..65.5 -> 5mm above Dual-18650 top pins 49.0!)
                with Locations((sgn * (x_in - 2.0), y_rail + 5.8, C.CHASSIS_SPLIT_Z - 12.0)):
                    Box(6.0, 3.8, 11.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4. Rear Reinforced Dovetail Lock Mortise Block (X=-10..+10, Y=-56.0..-48.0, Z=59.0..66.0)
        with Locations((0.0, -52.0, C.CHASSIS_SPLIT_Z - 7.0)):
            Box(20.0, 8.0, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        add(
            _build_rear_dovetail_prism(C.CHASSIS_SPLIT_Z - 6.0, C.CHASSIS_SPLIT_Z + 1.0, clearance=C.SLA_SLIDE_CLEAR),
            mode=Mode.SUBTRACT,
        )

        # 5. 4× Forgiving N20 Gearmotor Cradles (+0.4mm/side) + Unified M3 Captive Hex Nut Slots!
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            for sgn in (-1.0, 1.0):
                saddle_x = sgn * (w / 2.0 - 14.0)
                with Locations((saddle_x, y_ax, C.CHASSIS_Z_FLOOR)):
                    Box(23.0, 27.0, 10.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Forgiving N20 body + endcap pocket (+0.4mm per side -> 10.8 × 12.8 mm, open inward for wires!)
                with Locations((sgn * (w / 2.0 - 13.0), y_ax, C.Z_AXLE)):
                    Box(29.0, C.N20_W + 0.8, C.N20_H + 0.8, mode=Mode.SUBTRACT)
                with Locations((sgn * (w / 2.0 + 0.5), y_ax, C.Z_AXLE)):
                    Cylinder(radius=3.8, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                # Dual Unified M3 clearance bores (Ø3.5mm) + side-entry Captive DIN 934 M3 Hex Nut Slots!
                bx_clamp = sgn * (w / 2.0 - 13.0)
                for dy_b in (-9.5, 9.5):
                    with Locations((bx_clamp, y_ax + dy_b, C.CHASSIS_Z_FLOOR + 1.5)):
                        Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=10.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
                    slot_y = y_ax + dy_b + (1.6 if dy_b > 0 else -1.6)
                    with Locations((bx_clamp, slot_y, C.CHASSIS_Z_FLOOR + 2.6)):
                        Box(C.NUT_M3_AF, 8.0, C.NUT_M3_T, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 6. Dead-Center Dual-18650 Power Board Forgiving Cradle (45.4mm Y-channel = +0.7mm/side, ZERO rigid screw holes!)
        for sgn_y in (-1.0, 1.0):
            # Retaining rails at Y = ±23.6 (inner face ±22.7mm -> +0.7mm/side around 44.0mm board; fuses smoothly!)
            with Locations((0.0, sgn_y * 23.6, C.CHASSIS_Z_FLOOR)):
                Box(76.0, 1.8, 14.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Left X end-stop rib (X = -44.5..-43.0 -> gives 87.5mm length clearance for 85.0mm board!)
        with Locations((-43.75, 0.0, C.CHASSIS_Z_FLOOR)):
            Box(1.5, 34.0, 12.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 7. 2× Forgiving DRV8833 Motor Driver Pockets (Front & Rear Centers: 22.6×19.6mm = +0.8mm/side!)
        for py in (C.DRV_F_Y, C.DRV_R_Y):
            with Locations((0.0, py, C.CHASSIS_Z_FLOOR)):
                Box(C.DRV_W + 4.4, C.DRV_L + 4.4, 5.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((0.0, py, C.CHASSIS_Z_FLOOR + 2.0)):
                Box(C.DRV_W + 1.6, C.DRV_L + 1.6, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
            # Open side wire notches for N20 factory DuPont plugs
            with Locations((0.0, py, C.CHASSIS_Z_FLOOR + 2.2)):
                Box(C.DRV_W + 8.0, 10.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 8. PCA9685A Upper-Rear Open-Center Forgiving Bridge Shelf (Y=-49.8..-22.8, Z=40.3..43.8 -> clears +0.8mm Dual-18650!)
        for sgn in (-1.0, 1.0):
            # Side bridge ledges cantilevered from inner side walls (|X|=27.5..44.8, leaving center ±27.5 OPEN!)
            with Locations((sgn * 36.15, C.PCA_Y, C.PCA_Z - 3.7)):
                Box(17.3, C.PCA_W + 2.4, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Underside gusset into side wall (|X|=40.0..44.8, Z=33.5..40.5 -> clears A03_R clamp at Z=30.5!)
            with Locations((sgn * 42.4, C.PCA_Y, C.PCA_Z - 10.0)):
                Box(4.8, C.PCA_W + 1.6, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
            # Front/rear forgiving Y-stop lips (+0.8mm/side around 25.0mm PCA9685A!)
            for sy in (-1.0, 1.0):
                with Locations((sgn * 31.0, C.PCA_Y + sy * (C.PCA_W / 2.0 + 1.7), C.PCA_Z - 0.5)):
                    Box(8.0, 1.8, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Left X stop tab (X=-33.6..-31.8 -> +0.8mm clear of PCA9685A left edge -31.0; +X stays open for 6P I2C!)
        with Locations((-32.7, C.PCA_Y, C.PCA_Z - 0.5)):
            Box(1.8, 16.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 9. Right Mid-Waist Power Console Window (Type-C Charge + ON/OFF Switch + 4× Battery LEDs!)
        #    Located cleanly between front (+38) & rear (-38) wheels at X=+44.5..+47.0, Y=-18.0..+16.0, Z=37.0..46.8!
        with Locations((w / 2.0 - 0.5, -1.0, 41.9)):
            Box(8.0, 34.0, 9.8, mode=Mode.SUBTRACT)

        # Rear Convection Vents (clean rear styling + PCA9685A airflow)
        y_rear = C.CHASSIS_Y_MIN
        for sx in (-14.0, -7.0, 0.0, 7.0, 14.0):
            with Locations((sx, y_rear + 1.5, 48.0)):
                Box(3.4, 8.0, 10.0, mode=Mode.SUBTRACT)

    return _tag(tub.part, "A01_Chassis_Tub", "charcoal")


# ---------------------------------------------------------------------------
# A03_F / A03_R: Unified M3 Bolt-Down N20 Motor Clamp Straps (Identical STL!)
# ---------------------------------------------------------------------------
def build_motor_clamp(axle: str = "F") -> Part:
    """Rigid M3 bolt-down clamp strap locking both N20 gearboxes on an axle into A01 captive M3 nuts."""
    y_ax = C.Y_AXLE_F if axle == "F" else C.Y_AXLE_R
    pad_x = C.CHASSIS_W / 2.0 - 13.0  # 34.0 mm
    with BuildPart() as clamp2:
        for sgn in (-1.0, 1.0):
            with Locations((sgn * pad_x, y_ax, C.Z_AXLE + C.N20_H / 2.0 + 1.8)):
                Box(15.0, 26.0, 2.8)
            for dy_b in (-9.5, 9.5):
                with Locations((sgn * pad_x, y_ax + dy_b, C.Z_AXLE + C.N20_H / 2.0 + 1.8)):
                    Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=6.0, mode=Mode.SUBTRACT)
        # Dual perimeter tie-rails at dy = ±11.2mm (outside DRV8833 ±9.0mm -> 100% open center for DuPont plugs!)
        for dy_r in (-11.2, 11.2):
            with Locations((0, y_ax + dy_r, C.Z_AXLE + C.N20_H / 2.0 + 1.8)):
                Box(2.0 * pad_x - 10.0, 3.6, 2.8)
    return _tag(clamp2.part, f"A03_Motor_Clamp_{axle}", "charcoal")


# ---------------------------------------------------------------------------
# A02: Tool-Free 5-Point Slide-Lock Top Hood (94×120mm, Zero Exterior Screws!)
# ---------------------------------------------------------------------------
def build_top_hood() -> Part:
    w = C.CHASSIS_W
    l = C.CHASSIS_L
    yc = C.CHASSIS_Y_CTR
    x_in = w / 2.0 - C.WALL  # 44.5 mm

    # Add 2.0mm vertical perimeter skirt (Z=66.0..68.0) before beveling up to 72.5 -> ZERO 0.02mm knife edges!
    with BuildPart() as hood_bp:
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z)):
            with Locations((0, yc)):
                RectangleRounded(w, l, radius=11.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z + 2.0)):
            with Locations((0, yc)):
                RectangleRounded(w, l, radius=11.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP)):
            with Locations((0, yc - 3.5)):
                RectangleRounded(w - 10.0, l - 13.0, radius=10.0)
        loft(ruled=True)

    with BuildPart() as hood:
        add(hood_bp.part)

        # Match sloped front nose cleanly (leaves >=2.0mm solid vertical front skirt at Z=66..68!)
        with Locations(Location((0, 77.5, C.CHASSIS_SPLIT_Z + 5.0), (-32, 0, 0))):
            Box(w + 10.0, 30.0, 20.0, mode=Mode.SUBTRACT)

        # Sleek Side Fender-Flare Eaves with 1.4mm vertical outer lip (ZERO 0.02mm knife edges!)
        for sgn in (-1.0, 1.0):
            with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z)):
                with Locations((sgn * (w / 2.0 + 1.0), 0.0)):
                    RectangleRounded(5.4, 24.0, radius=2.2)
            with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z + 1.4)):
                with Locations((sgn * (w / 2.0 + 1.0), 0.0)):
                    RectangleRounded(5.4, 24.0, radius=2.2)
            with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z + 3.2)):
                with Locations((sgn * (w / 2.0 - 0.5), 0.0)):
                    RectangleRounded(3.0, 20.0, radius=1.2)
            loft(ruled=True)

        # Mid-Side Alignment Ribs (|X|=41.5..44.0, Y=-2.5..+11.5 -> 0.8mm clear of A01 rear stop at ΔY=-5mm!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * (x_in - 1.75), 4.5, C.CHASSIS_SPLIT_Z - 2.5)):
                Box(2.5, 14.0, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 4× Rigid Side Slide-Lock L-Hooks (generous 0.35mm side & Z clearance for effortless SLA assembly!)
        for sgn in (-1.0, 1.0):
            hx = sgn * (x_in - 2.45)
            for y_rail in SIDE_RAIL_YS:
                with Locations((hx, y_rail - 6.10, C.CHASSIS_SPLIT_Z - 10.8)):
                    Box(4.2, 3.4, 12.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
                with Locations((hx, y_rail - 3.70, C.CHASSIS_SPLIT_Z - 10.8)):
                    Box(4.2, 8.2, 3.9, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 5th Point: Integral Front Nose Interlock L-Hook (locks 4mm deep under Y=49.5 front ledge!)
        with Locations((0, 42.75, C.CHASSIS_SPLIT_Z - 15.2)):
            Box(22.0, 3.5, 16.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 47.25, C.CHASSIS_SPLIT_Z - 15.2)):
            Box(22.0, 12.5, 3.2, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Raised Sporty Rear-Deck Fastback Cowl (houses A10 Dovetail Lock Key!) + Clean Inset Aero Shark-Fin
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 2.0)):
            with Locations((0, -47.5)):
                RectangleRounded(44.0, 18.0, radius=4.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 2.2)):
            with Locations((0, -48.5)):
                RectangleRounded(34.0, 13.0, radius=3.5)
        loft(ruled=True)
        # Shark-fin seated cleanly INSIDE rear cowl top plateau (X=12.2..15.8, Y=-52..-45 -> clear of vents & cowl edge!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 1.2)):
            with Locations((14.0, -48.5)):
                RectangleRounded(3.6, 7.0, radius=1.2)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 12.5)):
            with Locations((14.0, -49.5)):
                RectangleRounded(2.6, 4.6, radius=1.0)
        loft(ruled=True)

        # Spacious Underside Headroom Recess (Y=-46.5..+20.0 -> clears Dual-18650 & PCA9685A while leaving solid 6.5mm roof under B01 wing slots!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_SPLIT_Z - 0.5)):
            with Locations((0, -13.25)):
                RectangleRounded(w - 18.0, 66.5, radius=7.0)
        extrude(amount=4.5, mode=Mode.SUBTRACT)

        # Rear Tapered Dovetail Keyway through A02 rear cowl (coaxial with A01 mortise -> locks ΔY=0!)
        add(
            _build_rear_dovetail_prism(C.CHASSIS_SPLIT_Z - 1.0, C.CHASSIS_Z_TOP + 3.5, clearance=C.SLA_SLIDE_CLEAR),
            mode=Mode.SUBTRACT,
        )

        # Twin Rear Convection Vents (flanking A10 lock key, cleanly clear of shark-fin!)
        for vx in (-9.6, 9.6):
            with Locations((vx, -44.5, C.CHASSIS_Z_TOP - 2.0)):
                Box(2.6, 6.6, 10.0, mode=Mode.SUBTRACT)

        # Dual-Tier Sculpted Neck Turret with 45° Chamfered Transition & Solid 2.0mm Servo Floor!
        neck_top_z = C.HEAD_PIVOT_Z + 6.5  # 99.0 mm
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 2.0)):
            with Locations((0, -5.0)):
                RectangleRounded(36.0, 22.0, radius=5.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_PIVOT_Z - 12.5)):  # Z = 80.0
            with Locations((0, -5.0)):
                RectangleRounded(36.0, 22.0, radius=5.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_PIVOT_Z - 8.5)):   # Z = 84.0 (2.0mm solid floor under servo!)
            with Locations((0, C.NECK_Y_CTR)):
                RectangleRounded(C.NECK_W, C.NECK_D, radius=5.0)
        with BuildSketch(Plane.XY.offset(neck_top_z)):             # Z = 99.0
            with Locations((0, C.NECK_Y_CTR)):
                RectangleRounded(C.NECK_W, C.NECK_D, radius=5.0)
        loft(ruled=True)

        # Widened Right-Side 7-Wire Neck DuPont Ribbon Tunnel (X=+1.5..+12.5 -> 2.5mm solid wall to M3 pivot!)
        with Locations((7.0, -5.0, C.CHASSIS_SPLIT_Z - 1.0)):
            Box(11.0, 16.0, (neck_top_z - C.CHASSIS_SPLIT_Z) + 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Top-Open Drop-In MG90S Servo Pocket (+0.45mm generous tolerance, solid 2.0mm floor at Z=84.0..86.0!)
        servo_z_bot = C.HEAD_PIVOT_Z - C.MG90S_W / 2.0 - 0.45  # 86.0 mm
        with Locations((-11.5, -7.9, servo_z_bot)):
            Box(23.5, 23.6, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((-19.0, -7.9, servo_z_bot)):
            Box(3.6, 33.6, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # Clean flush left gear-dome exit slot (exact same Z=servo_z_bot -> ZERO 0.2mm micro-step!)
        with Locations((-24.0, -2.0, servo_z_bot)):
            Box(5.6, 12.8, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Right Coaxial Head Pivot: Unified M3 Clear Bore + Top-Drop Captive M3 Hex Nut Slot!
        with Locations((20.5, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
            Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=11.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((19.0, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z - C.NUT_M3_AF / 2.0)):
            Box(C.NUT_M3_T, C.NUT_M3_AF, 12.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Keyhole Drop-In + Forward Slide Dovetail Mortise Slots for B01_Hood_Wing_L/R (0.30mm SLA clearance!)
        for sgn in (-1.0, 1.0):
            with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 2.2)):
                with Locations((sgn * 25.0, 33.6)):
                    Rectangle(6.6, 7.8)
            with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 0.2)):
                with Locations((sgn * 25.0, 33.6)):
                    Rectangle(5.0, 7.8)
            loft(ruled=True, mode=Mode.SUBTRACT)
            with Locations((sgn * 25.0, 26.0, C.CHASSIS_Z_TOP - 2.2)):
                Box(6.6, 7.8, 2.6, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    return _tag(hood.part, "A02_Top_Hood", "charcoal")


# ---------------------------------------------------------------------------
# A10: Tapered Rear Dovetail Hood Lock Key (Tool-Free 3-Second Clamshell Lock!)
# ---------------------------------------------------------------------------
def build_hood_lock_key() -> Part:
    z_top = C.CHASSIS_Z_TOP + 2.2  # 74.7 mm
    with BuildPart() as key:
        add(_build_rear_dovetail_prism(C.CHASSIS_SPLIT_Z - 5.7, z_top + 0.6, clearance=0.0))
        with BuildSketch(Plane.XY.offset(z_top + 0.25)):
            with Locations((0.0, -51.6)):
                RectangleRounded(16.0, 7.6, radius=2.2)
        with BuildSketch(Plane.XY.offset(z_top + 1.55)):
            with Locations((0.0, -51.6)):
                RectangleRounded(16.0, 7.6, radius=2.2)
        with BuildSketch(Plane.XY.offset(z_top + 3.0)):
            with Locations((0.0, -51.6)):
                RectangleRounded(14.0, 6.0, radius=1.8)
        loft(ruled=True)
        with Locations((0.0, -55.3, z_top + 0.85)):
            Box(12.0, 2.0, 1.3, mode=Mode.SUBTRACT)
    return _tag(key.part, "A10_Hood_Lock_Key", "charcoal")


# ---------------------------------------------------------------------------
# B01_L / B01_R: Pearl-White Hood Wings w/ Keyhole Sliding Dovetail!
# ---------------------------------------------------------------------------
def build_hood_wing(side: str = "L") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    with BuildPart() as wing:
        # 1.2mm straight vertical perimeter edge before top bevel -> ZERO 0.02mm knife edges!
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 0.25)):
            with Locations((sgn * 25.0, 29.5)):
                RectangleRounded(15.5, 28.0, radius=4.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 1.45)):
            with Locations((sgn * 25.0, 29.5)):
                RectangleRounded(15.5, 28.0, radius=4.5)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 3.0)):
            with Locations((sgn * 24.5, 28.5)):
                RectangleRounded(12.0, 23.0, radius=3.5)
        loft(ruled=True)
        # Keyhole sliding dovetail tenon (0.30mm clearance per side inside 6.6/5.0 slot!)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP - 1.9)):
            with Locations((sgn * 25.0, 33.5)):
                Rectangle(6.0, 7.0)
        with BuildSketch(Plane.XY.offset(C.CHASSIS_Z_TOP + 0.6)):
            with Locations((sgn * 25.0, 33.5)):
                Rectangle(4.4, 7.0)
        loft(ruled=True)
    return _tag(wing.part, f"B01_Hood_Wing_{side}", "white")


# ---------------------------------------------------------------------------
# B02 (L) & B03 (R w/ Power Console Arch): Pearl-White Side Armor!
# ---------------------------------------------------------------------------
def build_side_fairing(side: str = "L") -> Part:
    """
    Sturdy 4.25mm-thick white side armor seated 0.28mm outside A01's flat |X|=47.0 wall.
    Uses a 1.6mm flat perimeter skirt before chamfering outward -> ZERO 0.02mm knife edges!
      - B02 (Left) : Full vertical sliding dovetail (Z=38..63).
      - B03 (Right): Upper vertical sliding dovetail (Z=50..63) + sturdy power console arch
                     (Y=-17.5..+15.5, Z<47.5) exposing Type-C, ON/OFF switch & 4× battery LEDs!
    """
    sgn = -1.0 if side == "L" else 1.0
    x_in = sgn * (C.CHASSIS_W / 2.0 + 0.28)  # |X| = 47.28mm
    with BuildPart() as panel:
        with BuildSketch(Plane.YZ.offset(x_in)):
            with Locations((0.0, 51.0)):
                RectangleRounded(48.0, 29.0, radius=5.0)  # Z = 36.5..65.5 (0.5mm clear under A02 eave at 66.0!)
        with BuildSketch(Plane.YZ.offset(x_in + sgn * 1.6)):
            with Locations((0.0, 51.0)):
                RectangleRounded(48.0, 29.0, radius=5.0)
        with BuildSketch(Plane.YZ.offset(x_in + sgn * 4.25)):
            with Locations((0.0, 51.3)):
                RectangleRounded(41.0, 23.0, radius=4.0)
        loft(ruled=True)

        # Crisp wheel-arch clearance cutouts for Ø43mm tires (R=23.5mm -> 2.0mm radial tire clearance + sturdy pillars!)
        for y_ax in (C.Y_AXLE_F, C.Y_AXLE_R):
            with Locations((x_in + sgn * 2.0, y_ax, C.Z_AXLE)):
                Cylinder(radius=C.WHEEL_R + 2.0, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        if side == "L":
            # Full vertical sliding dovetail mortise (0.30mm clearance on all faces!)
            with BuildSketch(Plane.YZ.offset(x_in - sgn * 0.48)):
                with Locations((0.0, 49.75)):
                    Rectangle(12.6, 27.5)  # Z = 36.0..63.5
            with BuildSketch(Plane.YZ.offset(x_in + sgn * 2.05)):
                with Locations((0.0, 49.75)):
                    Rectangle(15.8, 27.5)
            loft(ruled=True, mode=Mode.SUBTRACT)
        else:
            # Right waist tactical power console arch (exposes Type-C, ON/OFF switch, 4× battery LEDs!)
            with Locations((x_in + sgn * 2.0, -1.0, 41.25)):
                Box(14.0, 33.0, 12.5, mode=Mode.SUBTRACT)  # Z = 35.0..47.5, Y = -17.5..+15.5
            # Upper vertical sliding dovetail mortise opening cleanly into arch at Z=47.5 (slides down onto Z=50..63!)
            with BuildSketch(Plane.YZ.offset(x_in - sgn * 0.48)):
                with Locations((0.0, 55.5)):
                    Rectangle(12.6, 16.0)  # Z = 47.5..63.5
            with BuildSketch(Plane.YZ.offset(x_in + sgn * 2.05)):
                with Locations((0.0, 55.5)):
                    Rectangle(15.8, 16.0)
            loft(ruled=True, mode=Mode.SUBTRACT)

    name = "B02_Side_Fairing_L" if side == "L" else "B03_Side_Fairing_R"
    return _tag(panel.part, name, "white")


def build_all_chassis_parts() -> dict:
    return {
        "A01_chassis_tub": ("plate_A_charcoal", build_chassis_tub()),
        "A02_top_hood": ("plate_A_charcoal", build_top_hood()),
        "A10_hood_lock_key": ("plate_A_charcoal", build_hood_lock_key()),
        "A03_motor_clamp_F": ("plate_A_charcoal", build_motor_clamp("F")),
        "A03_motor_clamp_R": ("plate_A_charcoal", build_motor_clamp("R")),
        "B01_hood_wing_L": ("plate_B_white", build_hood_wing("L")),
        "B01_hood_wing_R": ("plate_B_white", build_hood_wing("R")),
        "B02_side_fairing_L": ("plate_B_white", build_side_fairing("L")),
        "B03_side_fairing_R": ("plate_B_white", build_side_fairing("R")),
    }
