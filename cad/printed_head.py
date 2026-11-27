"""
KRON-01V6 (ESP32-S3-CAM N16R8 Edition, v2.0.0) — Tolerance-Forgiving Brain Helmet Parts
========================================================================================
Zero-soldering, unified M3, zero-exterior-screw wide astronaut helmet (94×76×67mm)
housing the entire AI brain + camera + display + audio stack (only 7 wires cross the neck!):
  - B04_head_shell  : Conformal-hollowed pearl-white helmet dome (94×76×67mm), wide bottom
                      slip-in opening, vertical bayonet ear keyholes, rear-crown 3020 speaker shelf.
  - A06_head_core   : Structural gunmetal inner frame w/ forgiving ±0.7–0.8mm PCB pockets (ZERO rigid
                      M2 screw holes!): GMT020-02 2.0" LCD cradle, horizontal ESP32-S3-CAM N16R8
                      dual-ledge bay (clears 2×22P headers!), rear-crown 3020 speaker pocket,
                      vertical MAX98357A rear U-channel, chin INMP441 mic recess, 90° bayonet ear
                      receivers, front tapered visor mortises, MG90S horn pocket & M3 right pivot!
  - A08_visor_mask  : Glossy curved pitch-black full-face visor w/ oversized 42.8×32.6mm LCD window
                      (+1.0mm/side margin for LCD alignment variance!), Ø8.8mm OV3660 lens aperture
                      + 10.0×10.0mm forgiving rear pocket, and twin tapered rear wedge tenons.
  - A07_top_grille  : Rear-crown 3020 speaker acoustic grille seated cleanly on B04's stepped shelf.
  - A09_ear_hub_L/R : Tool-free 90° camera-lens bayonet twist-lock ear hubs (0.35mm SLA clearance!).
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
    Rectangle,
    RectangleRounded,
    add,
    extrude,
    loft,
)
import config as C

Y_EAR = C.HEAD_Y_CTR - 1.0      # -3.0 mm
Z_EAR = C.HEAD_Z_CTR - 5.5      # 115.0 mm (cleanly below S3-CAM pins at Z=120.0!)


def _col(name: str) -> Color:
    r, g, b, a = C.COLORS[name]
    return Color(r, g, b, a)


def _tag(shape, label: str, color_key: str):
    shape.label = label
    shape.color = _col(color_key)
    return shape


def _build_visor_wedge(sgn: float, y_tip: float, y_base: float, clearance: float = 0.0) -> Part:
    """
    Tapered wedge tenon (clearance=0) or matching mortise slot (clearance>0)
    for A08_Visor_Mask <-> A06_Head_Core at X = sgn * 33.4, Z = 115.0 (outside 62mm LCD!).
    """
    c = clearance
    cx = sgn * 34.0
    cz = Z_EAR
    y0, y1 = 23.0, 26.2

    def _lerp(v0: float, v1: float, y: float) -> float:
        t = (y - y0) / (y1 - y0)
        return v0 + t * (v1 - v0)

    plane_tip = Plane(origin=(cx, y_tip, cz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    plane_base = Plane(origin=(cx, y_base, cz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with BuildPart() as bp:
        with BuildSketch(plane_tip):
            Rectangle(_lerp(2.8, 3.2, y_tip) + 2.0 * c, _lerp(8.6, 9.2, y_tip) + 2.0 * c)
        with BuildSketch(plane_base):
            Rectangle(_lerp(2.8, 3.2, y_base) + 2.0 * c, _lerp(8.6, 9.2, y_base) + 2.0 * c)
        loft(ruled=True)
    return bp.part


# ---------------------------------------------------------------------------
# A06: Gunmetal Structural Inner Core (Forgiving Pockets for All 6 Head Modules!)
# ---------------------------------------------------------------------------
def build_head_core() -> Part:
    core_w, core_d = 75.6, 53.0   # X: ±37.8 (inner ±34.8 = 69.6mm!), Y: -28.5..+24.5
    yc = C.HEAD_Y_CTR             # -2.0
    z_bot = C.HEAD_Z_BOT + 4.0    # 91.0
    z_mid = C.HEAD_Z_TOP - 15.0   # 139.0
    z_top = C.HEAD_Z_TOP - 8.5    # 145.5

    with BuildPart() as core:
        # Tapered upper crown clears B04's curved inner dome cleanly!
        with BuildSketch(Plane.XY.offset(z_bot)):
            with Locations((0, yc)):
                RectangleRounded(core_w, core_d, radius=3.0)
        with BuildSketch(Plane.XY.offset(z_mid)):
            with Locations((0, yc)):
                RectangleRounded(core_w, core_d, radius=3.0)
        with BuildSketch(Plane.XY.offset(z_top)):
            with Locations((0, yc - 0.5)):
                RectangleRounded(62.0, 46.0, radius=7.5)
        loft(ruled=True)

        # 1. Hollow main electronics bay (inner width 69.6mm -> fits 64mm S3-CAM & 62mm LCD w/ generous margin!)
        with Locations((0, 0.8, z_bot - 2.0)):
            Box(69.6, 52.0, (z_top - z_bot) - 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Open rear bay below speaker (keeps 3.0mm rear wall at Y=-28.5..-25.5)
        with Locations((0, -12.0, z_bot + 2.5)):
            Box(69.6, 27.0, (z_top - z_bot) - 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 2. Bottom neck swing clearance (clears MG90S_GearDome & A02 upper yoke across full -20°..+22° pitch!)
        with Locations((-0.85, -8.1, C.HEAD_Z_BOT - 2.0)):
            Box(52.7, 38.4, 18.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, -23.5, C.HEAD_Z_BOT - 2.0)):
            Box(52.0, 17.0, 24.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 3. Front Chin Recess for INMP441 MEMS Mic (Ø14mm at Y=18.0, Z=90.8 -> 0.7mm/side clearance!)
        with Locations((0, C.MIC_Y, C.HEAD_Z_BOT - 2.0)):
            Box(30.0, 18.0, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 4. Side Pivot Yoke Arms + MG90S Horn Pocket (L) & Unified M3 Pivot Bore (R)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 32.6, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z + 3.5)):
                Box(10.0, 19.0, 19.0)
            with Locations((sgn * 32.6, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=16.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Left yoke MG90S horn & spline pocket (X=-31.5..-26.0 -> clears spline & horn cleanly!)
        with Locations((-28.8, 3.0, C.HEAD_PIVOT_Z)):
            Box(5.8, 17.5, 6.8, mode=Mode.SUBTRACT)

        # 5. Forgiving GMT020-02 2.0" LCD Perimeter Cradle (63.4 × 38.9 mm = +0.7mm/side, ZERO M2 screws!)
        #    Fused cleanly into side walls |X|=34.8..36.2!
        for sgn in (-1.0, 1.0):
            # Side guide rail (|X|=31.7..36.2 -> 63.4mm inner width for 62.0mm LCD PCB!)
            with Locations((sgn * 33.95, C.LCD_Y_PCB + 0.3, C.LCD_Z_CTR)):
                Box(4.5, 4.6, C.LCD_PCB_H + 3.0)
            # Front retaining corner tabs overlapping LCD PCB corners by 2.0mm (Y=23.3..24.4)
            for sz in (-1.0, 1.0):
                with Locations((sgn * 32.6, C.LCD_Y_PCB + 2.35, C.LCD_Z_CTR + sz * (C.LCD_PCB_H / 2.0 - 2.0))):
                    Box(7.2, 1.5, 4.5)
            # Bottom LCD corner support ledges fused directly into side guide rail (|X|=22.0..35.8)
            with Locations((sgn * 28.9, C.LCD_Y_PCB + 0.8, C.LCD_Z_CTR - C.LCD_PCB_H / 2.0 - 1.7)):
                Box(13.8, 4.0, 2.0)

        # 6. Forgiving VERTICAL SF-ESP32-S3-CAM Cradle (69.6mm open X width clears 65.84mm Type-C+antenna by +1.88mm/side!)
        #    Two bottom corner ledges + front/rear PCB guide cheeks hold S3-CAM cleanly at Y=10.0..11.6, Z=112.5..140.5!
        for sgn in (-1.0, 1.0):
            # Bottom support ledge under PCB bottom edge (Z=109.5..111.7 -> 0.8mm clear under Z=112.5 PCB!)
            with Locations((sgn * 31.8, C.S3_Y_PCB + 0.8, C.S3_Z_CTR - C.S3_PCB_W / 2.0 - 1.9)):
                Box(8.6, 5.4, 2.2)
            # Front retaining cheek (Y=12.3..14.1 -> +0.7mm PCB thickness margin!)
            for sz in (-1.0, 1.0):
                with Locations((sgn * 33.0, C.S3_Y_PCB + 3.2, C.S3_Z_CTR + sz * 11.8)):
                    Box(6.4, 1.8, 3.6)
            # Rear retaining stop cheek (Y=7.9..9.5, clear of rear pins & TF slot -> only touches outer X=±31..36!)
            with Locations((sgn * 33.8, C.S3_Y_PCB - 1.3, C.S3_Z_CTR)):
                Box(4.8, 1.6, 18.0)

        # 7. Rear-Crown 3020 Cavity Speaker Forgiving Pocket (31.4 × 21.4 mm = +0.7mm/side!)
        spk_bot = C.SPK_Z_TOP - C.SPK_H  # 141.0 mm
        with Locations((0, C.SPK_Y, spk_bot - 2.2)):
            Box(C.SPK_L + 5.4, C.SPK_W + 5.4, 6.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, C.SPK_Y, spk_bot - 0.3)):
            Box(C.SPK_L + 1.4, C.SPK_W + 1.4, 6.8, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # Bottom acoustic/wire pass-through window straight down toward MAX98357A
        with Locations((0, C.SPK_Y, spk_bot - 3.0)):
            Box(18.0, 10.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 8. Vertical MAX98357A Rear Inner Wall U-Channel (20.6mm wide = +0.8mm/side, fused above 109.5mm arch!)
        with Locations((C.AMP_X, -24.0, C.AMP_Z - C.AMP_H / 2.0 - 2.2)):
            Box(C.AMP_W + 5.2, 6.2, 1.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
        for sgn in (-1.0, 1.0):
            with Locations((C.AMP_X + sgn * (C.AMP_W / 2.0 + 1.8), -23.9, C.AMP_Z - 1.0)):
                Box(2.0, 6.0, C.AMP_H - 1.5)

        # 9. Dual Side Camera-Lens Bayonet Twist-Lock Receivers (0.35mm generous SLA clearance!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 36.2, Y_EAR, Z_EAR)):
                Cylinder(radius=4.55, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                Box(10.0, 4.4, 15.0, mode=Mode.SUBTRACT)
            # Twin internal positive rotation stops fused cleanly into |X|=34.8..36.0 inner wall!
            with Locations((sgn * 33.8, Y_EAR + 5.6, Z_EAR + 3.5)):
                Box(4.0, 2.6, 2.6)
            with Locations((sgn * 33.8, Y_EAR - 5.6, Z_EAR - 3.5)):
                Box(4.0, 2.6, 2.6)

            # Dual Front Tapered Visor Mortise Blocks fused cleanly into side walls (|X|=31.8..36.4 -> clears +0.8mm LCD!)
            with Locations((sgn * 34.1, 22.8, Z_EAR)):
                Box(4.6, 3.2, 12.0)
            add(_build_visor_wedge(sgn, y_tip=22.6, y_base=26.2, clearance=0.24), mode=Mode.SUBTRACT)

    return _tag(core.part, "A06_Head_Core", "charcoal")


# ---------------------------------------------------------------------------
# B04: Sculpted Conformal-Hollow Wide Astronaut Helmet Shell (94×76×67mm)
# ---------------------------------------------------------------------------
def _build_helmet_outer_dome() -> Part:
    yc = C.HEAD_Y_CTR
    with BuildPart() as dome_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT)):
            with Locations((0, yc)):
                RectangleRounded(82.6, 66.4, radius=13.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc)):
                RectangleRounded(92.0, 75.0, radius=21.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 53.0)):
            with Locations((0, yc)):
                RectangleRounded(94.0, 76.0, radius=22.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.0)):
            with Locations((0, yc - 0.8)):
                RectangleRounded(83.0, 67.0, radius=18.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(60.0, 48.0, radius=14.5)
        loft(ruled=False)
    return dome_bp.part


def build_head_shell() -> Part:
    yc = C.HEAD_Y_CTR
    outer_dome = _build_helmet_outer_dome()

    with BuildPart() as inner_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT - 0.5)):
            with Locations((0, yc)):
                RectangleRounded(77.6, 61.0, radius=10.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc)):
                RectangleRounded(81.0, 66.0, radius=16.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 53.0)):
            with Locations((0, yc)):
                RectangleRounded(81.0, 66.0, radius=18.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.5)):
            with Locations((0, yc - 0.8)):
                RectangleRounded(71.0, 57.0, radius=15.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 3.5)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(52.0, 40.0, radius=11.0)
        loft(ruled=False)

    visor_zc = C.HEAD_Z_CTR - 1.5

    with BuildPart() as shell:
        add(outer_dome)
        add(inner_bp.part, mode=Mode.SUBTRACT)

        # Clean Front Visor Aperture (72.0 × 56.8 mm -> receives A08 with 0.30mm gap!)
        with BuildSketch(Plane.XZ.offset(-18.0)):
            with Locations((0, visor_zc)):
                RectangleRounded(72.0, 56.8, radius=14.0)
        extrude(amount=-30.0, mode=Mode.SUBTRACT)

        # Rear-Crown 3020 Speaker Through-Hole + Top Stepped Seating Shelf for A07_Top_Grille
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.5)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(28.0, 18.0, radius=4.5)
        extrude(amount=8.0, mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 2.3)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(32.4, 22.4, radius=6.0)
        extrude(amount=4.0, mode=Mode.SUBTRACT)

        # Flat Circular Side Ear Pads at |X|=45.0 + Vertical Bayonet Keyhole Apertures
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 50.0, Y_EAR, Z_EAR)):
                Cylinder(radius=12.6, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            with Locations((sgn * 43.0, Y_EAR, Z_EAR)):
                Cylinder(radius=4.55, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                Box(14.0, 4.4, 15.0, mode=Mode.SUBTRACT)

    return _tag(shell.part, "B04_Head_Shell", "white")


# ---------------------------------------------------------------------------
# A08: Flush Curved Pitch-Black Visor Mask (Oversized LCD Window + OV3660 Pocket!)
# ---------------------------------------------------------------------------
def build_visor_mask() -> Part:
    outer_dome = _build_helmet_outer_dome()
    yc = C.HEAD_Y_CTR
    visor_zc = C.HEAD_Z_CTR - 1.5

    with BuildPart() as visor_inner_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT - 1.0)):
            with Locations((0, yc)):
                RectangleRounded(76.0, 60.0, radius=14.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc)):
                RectangleRounded(85.2, 68.2, radius=17.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 53.0)):
            with Locations((0, yc)):
                RectangleRounded(87.2, 69.2, radius=18.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.0)):
            with Locations((0, yc - 0.8)):
                RectangleRounded(76.2, 60.2, radius=15.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP + 1.0)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(53.0, 41.0, radius=11.5)
        loft(ruled=False)

    with BuildPart() as clip_bp:
        with BuildSketch(Plane.XZ.offset(-23.5)):
            with Locations((0, visor_zc)):
                RectangleRounded(71.4, 56.2, radius=13.7)
        extrude(amount=-22.0)

    with BuildPart() as visor:
        add(outer_dome)
        add(visor_inner_bp.part, mode=Mode.SUBTRACT)
        add(clip_bp.part, mode=Mode.INTERSECT)

        # Twin Rear Tapered Wedge Tenons (0.24mm SLA clearance inside A06 mortise sockets!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 34.0, 30.0, Z_EAR)):
                Box(3.2, 8.0, 9.2)
            add(_build_visor_wedge(sgn, y_tip=23.0, y_base=26.2, clearance=0.0))

        # OV3660 Short-Ribbon Camera Lens Aperture (Ø8.8mm) + Forgiving 10.0×10.0mm Rear Pocket (+0.75mm/side!)
        with Locations((0, 34.0, C.CAM_Z_CTR)):
            Cylinder(radius=4.4, height=16.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        with Locations((0, C.CAM_Y_PCB + 2.0, C.CAM_Z_CTR)):
            Box(10.0, 6.2, 10.0, mode=Mode.SUBTRACT)

        # Oversized 2.0" GMT020-02 Active Display Window (42.8 × 32.6 mm -> +1.0mm margin/side absorbs LCD variance!)
        with BuildSketch(Plane.XZ.offset(-22.0)):
            with Locations((0, C.LCD_Z_CTR)):
                RectangleRounded(42.8, 32.6, radius=5.0)
        extrude(amount=-24.0, mode=Mode.SUBTRACT)

    return _tag(visor.part, "A08_Visor_Mask", "visor_black")


# ---------------------------------------------------------------------------
# A07: Discreet Rear-Crown 3020 Speaker Acoustic Grille (Seated on B04 Shelf!)
# ---------------------------------------------------------------------------
def build_top_grille() -> Part:
    with BuildPart() as grille:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 2.15)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(31.8, 21.8, radius=5.7)
        extrude(amount=2.15)
        for iy in range(-3, 4):
            with Locations((0, C.SPK_Y + iy * 2.6, C.HEAD_Z_TOP - 1.1)):
                Box(22.0, 1.3, 4.0, mode=Mode.SUBTRACT)
    return _tag(grille.part, "A07_Top_Grille", "charcoal")


# ---------------------------------------------------------------------------
# A09_L / A09_R: Camera-Lens 90° Bayonet Twist-Lock Ear Hubs (0.35mm SLA Fit!)
# ---------------------------------------------------------------------------
def build_ear_pod(side: str = "L") -> Part:
    sgn = -1.0 if side == "L" else 1.0
    x_ctr = sgn * 48.3  # Outer dial |X|=45.3..51.3 (0.30mm clear of B04 pad at 45.0!)

    with BuildPart() as pod:
        with Locations((x_ctr, Y_EAR, Z_EAR)):
            Cylinder(radius=12.0, height=6.0, rotation=(0, 90, 0))
        with Locations((x_ctr + sgn * 2.5, Y_EAR, Z_EAR)):
            Cylinder(radius=8.8, height=2.0, rotation=(0, 90, 0))
        with Locations((x_ctr + sgn * 3.6, Y_EAR, Z_EAR)):
            Box(1.8, 15.0, 3.4)
        # Concentric bayonet shaft (R=4.2mm inside R=4.55mm keyhole -> 0.35mm generous SLA fit!)
        with Locations((sgn * 38.6, Y_EAR, Z_EAR)):
            Cylinder(radius=4.2, height=13.6, rotation=(0, 90, 0))  # |X| = 31.8..45.4
        # Dual opposing inner bayonet locking lugs (|X|=31.8..34.4 -> 0.40mm clear behind A06 inner wall 34.8!)
        with Locations((sgn * 33.1, Y_EAR, Z_EAR)):
            Box(2.6, 14.0, 3.6)

    return _tag(pod.part, f"A09_Ear_Hub_{side}", "charcoal")


def build_all_head_parts() -> dict:
    return {
        "A06_head_core": ("plate_A_charcoal", build_head_core()),
        "A07_top_grille": ("plate_A_charcoal", build_top_grille()),
        "A08_visor_mask": ("plate_A_charcoal", build_visor_mask()),
        "A09_ear_hub_L": ("plate_A_charcoal", build_ear_pod("L")),
        "A09_ear_hub_R": ("plate_A_charcoal", build_ear_pod("R")),
        "B04_head_shell": ("plate_B_white", build_head_shell()),
    }
