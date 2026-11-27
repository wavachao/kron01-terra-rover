"""
KRON-01V6 (ESP32-S3-CAM N16R8 Edition, v2.1.0) — Industrial-Grade Brain Helmet Parts
=====================================================================================
Zero-soldering, unified M3, zero-exterior-screw wide astronaut helmet (exact 94×76×67mm)
housing the entire AI brain + camera + display + audio stack (only 7 wires cross the neck!):
  - B04_head_shell  : Exact filleted 94×76×67mm pearl-white helmet shell (zero B-spline bloat!),
                      conformal >=2.5mm wall thickness, wide bottom slip-in opening, shallow
                      1.5mm circular ear seats + bayonet keyholes, flat-crown 3020 speaker shelf.
  - A06_head_core   : Structural gunmetal inner frame w/ solid non-pierced top deck, integrated
                      3020 speaker recess, flush-datum side walls (zero micro-steps/slivers!),
                      forgiving ±0.7–0.8mm PCB pockets for GMT020-02 LCD, vertical SF-ESP32-S3-CAM,
                      rear MAX98357A amp, dedicated INMP441 chin mic cradle, 90° bayonet ear
                      receivers, front tapered visor mortises, MG90S horn pocket & M3 right pivot.
  - A08_visor_mask  : Concentric 3.6mm curved pitch-black full-face visor w/ oversized 42.8×32.6mm
                      LCD window, solid rear OV3660 camera housing boss (10×10mm pocket + Ø8.8mm
                      lens bore), and twin recessed tapered wedge tenons.
  - A07_top_grille  : Rear-crown 3020 speaker acoustic grille seated flush on B04's flat crown.
  - A09_ear_hub_L/R : Tool-free 90° camera-lens bayonet twist-lock ear hubs (0.35mm SLA clearance!).
"""

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Cylinder,
    Locations,
    Mode,
    Part,
    Plane,
    Rectangle,
    RectangleRounded,
    add,
    chamfer,
    extrude,
    fillet,
    loft,
)
import config as C

Y_EAR = C.HEAD_Y_CTR - 1.0      # -3.0 mm
Z_EAR = C.HEAD_Z_CTR - 5.5      # 115.0 mm (cleanly centered on helmet cheek!)
VISOR_ZC = C.HEAD_Z_CTR - 1.0   # 119.5 mm (Z = 93.5 .. 145.5 for 52mm visor height)


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
    for A08_Visor_Mask <-> A06_Head_Core at |X| = 33.8, Z = 115.0 (well inside ±35.7 visor rim!).
    """
    c = clearance
    cx = sgn * 33.8
    cz = Z_EAR
    y0, y1 = 20.6, 24.4

    def _lerp(v0: float, v1: float, y: float) -> float:
        t = (y - y0) / (y1 - y0)
        return v0 + t * (v1 - v0)

    plane_tip = Plane(origin=(cx, y_tip, cz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    plane_base = Plane(origin=(cx, y_base, cz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with BuildPart() as bp:
        with BuildSketch(plane_tip):
            Rectangle(_lerp(2.4, 2.8, y_tip) + 2.0 * c, _lerp(8.4, 9.2, y_tip) + 2.0 * c)
        with BuildSketch(plane_base):
            Rectangle(_lerp(2.4, 2.8, y_base) + 2.0 * c, _lerp(8.4, 9.2, y_base) + 2.0 * c)
        loft(ruled=True)
    return bp.part


# ---------------------------------------------------------------------------
# Shared Exact Helmet Outer Dome (94.0 × 76.0 × 67.0 mm — ZERO B-Spline Bloat!)
# ---------------------------------------------------------------------------
def _build_helmet_outer_dome(inset: float = 0.0, extend_bottom: float = 0.0) -> Part:
    """
    Mathematically clean, exact filleted astronaut helmet dome.
    With inset=0: exact 94.0(W) × 76.0(D) × 67.0(H) mm, Y=[-40, +36], Z=[87, 154].
    With inset>0: exact concentric inner offset guaranteeing uniform wall thickness everywhere!
    """
    w = C.HEAD_W - 2.0 * inset
    d = C.HEAD_D - 2.0 * inset
    h = C.HEAD_H - inset + extend_bottom
    z_bot = C.HEAD_Z_BOT - extend_bottom
    r_vert = max(2.0, 18.0 - inset)
    r_top = max(2.0, 13.0 - inset)
    r_bot = max(1.0, 4.0 - inset)

    with BuildPart() as dome_bp:
        with BuildSketch(Plane.XY.offset(z_bot)):
            with Locations((0, C.HEAD_Y_CTR)):
                RectangleRounded(w, d, radius=r_vert)
        extrude(amount=h)
        top_edges = dome_bp.edges().filter_by(lambda e: abs(e.center().Z - (z_bot + h)) < 0.05)
        fillet(top_edges, radius=r_top)
        if extend_bottom == 0.0 and inset == 0.0:
            bot_edges = dome_bp.edges().filter_by(lambda e: abs(e.center().Z - z_bot) < 0.05)
            fillet(bot_edges, radius=r_bot)
    return dome_bp.part


# ---------------------------------------------------------------------------
# A06: Gunmetal Structural Inner Core (Clean Solid-Deck Frame, ZERO Slits!)
# ---------------------------------------------------------------------------
def build_head_core() -> Part:
    """
    Clean structural inner helmet frame (77.0W × 53.5D × 57.5H mm):
      - X: [-38.5, +38.5] (inner bay [-35.0, +35.0] = 70.0mm wide, solid 3.5mm side walls!)
      - Y: [-28.5, +25.0] (solid 3.5mm rear wall at -28.5..-25.0; flush front datum at +25.0!)
      - Z: [88.5, 146.0]  (stays 1.5mm above B04 bottom 87.0; solid top deck Z=139.0..146.0!)
    """
    core_w = 77.0               # |X| <= 38.5 (0.5mm slip-in clearance inside B04 inner 79.0!)
    core_d = 53.5               # Y = -28.5 .. +25.0 (clears B04 curved front corners cleanly!)
    yc = -1.75                  # (-28.5 + 25.0) / 2
    z_bot = C.HEAD_Z_BOT + 1.5  # 88.5 mm (flush with integrated pivot yokes; inside B04 >= 87.0!)
    z_ceil = 139.0              # Solid inner bay ceiling (clears S3-CAM top 138.0 by 1.0mm!)
    z_top = 146.0               # 7.0mm thick structural top deck housing 3020 speaker pocket!

    with BuildPart() as core:
        # Clean rounded outer prism (R=11.5 concentric with B04 R=13.0!) + 3.0mm top chamfer
        with BuildSketch(Plane.XY.offset(z_bot)):
            with Locations((0, yc)):
                RectangleRounded(core_w, core_d, radius=11.5)
        extrude(amount=z_top - z_bot)
        top_edges = core.edges().filter_by(lambda e: abs(e.center().Z - z_top) < 0.05)
        chamfer(top_edges, length=3.0)

        # 1a. Concentric Inner Electronics Bay (70.0×46.5, R=8.0 -> EXACT 3.5mm wall around ALL 4 corners!)
        with BuildSketch(Plane.XY.offset(z_bot - 1.5)):
            with Locations((0, yc)):
                RectangleRounded(core_w - 7.0, core_d - 7.0, radius=8.0)
        extrude(amount=(z_ceil - (z_bot - 1.5)), mode=Mode.SUBTRACT)

        # 1b. Clean Front Display Bay Opening (63.4mm wide = |X|<=31.7 -> leaves sturdy front corners!)
        with Locations((0, 21.0, z_bot - 1.5)):
            Box(63.4, 16.0, (z_ceil - (z_bot - 1.5)), align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 2. Clean Front Upper Clearance Notch (clears OV3660 rear camera boss on A08)
        with Locations((0, 23.0, z_ceil - 0.5)):
            Box(58.0, 12.0, 10.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 3. Dedicated Front Chin Shelf & INMP441 MEMS Mic Cradle (Z=88.5..90.0 shelf + center mic pad Y=13.0..26.5!)
        with Locations((0, 19.0, z_bot)):
            Box(65.0, 12.0, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 19.75, z_bot)):
            Box(22.0, 13.5, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Sturdy lateral retaining cheeks for Ø14mm INMP441 (15.4mm inner width = +0.7mm/side, zero thin ring!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 8.9, 19.5, z_bot + 1.2)):
                Box(2.4, 10.0, 2.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Rear mic stop rib (Y=13.0..14.0 -> clear of neck swing Y<=12.6, clear behind mic Y=14.2!)
        with Locations((0, 13.5, z_bot + 1.2)):
            Box(10.0, 1.0, 1.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # Bottom acoustic port hole (Ø7.0mm clears 4.7×3.8mm INMP441 MEMS sensor cleanly w/ 1.8mm front rim!)
        with Locations((C.MIC_X, C.MIC_Y, z_bot - 1.0)):
            Cylinder(radius=3.5, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 4. Bottom Neck Swing Clearance (clears A02 upper yoke across full -20°..+22° pitch, Y_max=12.6!)
        with Locations((-0.85, -7.7, C.HEAD_Z_BOT - 2.0)):
            Box(52.8, 40.6, 19.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, -24.5, C.HEAD_Z_BOT - 2.0)):
            Box(52.0, 19.0, 24.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 5. Integrated Side Pivot Yoke Blocks (Z=88.5..106.5 -> NEVER protrudes below B04 87.0!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 33.2, C.HEAD_PIVOT_Y, z_bot)):
                Box(10.0, 19.0, 18.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((sgn * 33.2, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=16.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Left yoke MG90S horn & spline pocket (X=-31.6..-26.0, Z=89.1..95.9)
        with Locations((-28.8, 3.0, C.HEAD_PIVOT_Z)):
            Box(5.8, 17.6, 6.8, mode=Mode.SUBTRACT)

        # 6. Forgiving GMT020-02 2.0" LCD Perimeter Cradle (63.4 × 38.9 mm = +0.7mm/side!)
        for sgn in (-1.0, 1.0):
            # Rear LCD backing guide strip (|X|=31.7..35.5, Y=19.8..21.8 -> cleanly backs LCD PCB at Y=22.0!)
            with Locations((sgn * 33.6, C.LCD_Y_PCB - 1.2, C.LCD_Z_CTR)):
                Box(3.8, 2.0, C.LCD_PCB_H + 3.0)
            # Front retaining corner tabs overlapping LCD PCB corners (Y=23.8..25.0, strictly inside Y<=25.0!)
            for sz in (-1.0, 1.0):
                with Locations((sgn * 31.4, C.LCD_Y_PCB + 2.4, C.LCD_Z_CTR + sz * (C.LCD_PCB_H / 2.0 - 2.2))):
                    Box(4.0, 1.2, 4.8)
            # Bottom LCD corner support ledges fused directly into side walls
            with Locations((sgn * 29.2, C.LCD_Y_PCB + 0.2, C.LCD_Z_CTR - C.LCD_PCB_H / 2.0 - 1.8)):
                Box(13.6, 4.2, 2.2)

        # 7. Forgiving VERTICAL SF-ESP32-S3-CAM Cradle (70.0mm open X width clears 65.84mm by +2.08mm/side!)
        for sgn in (-1.0, 1.0):
            # Bottom support ledge under PCB bottom edge (Z=106.8..109.2 -> 0.8mm clear under Z=110.0 PCB!)
            with Locations((sgn * 32.0, C.S3_Y_PCB + 0.8, C.S3_Z_CTR - C.S3_PCB_W / 2.0 - 2.0)):
                Box(8.6, 5.4, 2.4)
            # Front retaining cheeks positioned cleanly ABOVE & BELOW dual Type-C ports (Z=110.1..112.7 & 135.3..137.9!)
            for sz in (-1.0, 1.0):
                with Locations((sgn * 33.2, C.S3_Y_PCB + 3.3, C.S3_Z_CTR + sz * 12.6)):
                    Box(6.2, 2.0, 2.6)
            # Rear retaining stop cheek (Y=4.2..5.8 -> clear of rear pins & TF slot!)
            with Locations((sgn * 33.8, C.S3_Y_PCB - 1.5, C.S3_Z_CTR)):
                Box(4.8, 1.8, 18.0)

        # 8. Integrated Rear-Crown 3020 Cavity Speaker Pocket (carved cleanly into 7.0mm solid top deck!)
        spk_bot = C.SPK_Z_TOP - C.SPK_H  # 141.0 mm
        with Locations((0, C.SPK_Y, spk_bot - 0.3)):
            Box(C.SPK_L + 1.4, C.SPK_W + 1.4, 8.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, C.SPK_Y, z_ceil - 1.0)):
            Box(18.0, 10.0, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 9. Vertical MAX98357A Rear Inner Wall U-Channel (20.6mm wide = +0.8mm/side, fused into Y=-25.0 wall!)
        with Locations((C.AMP_X, -23.8, C.AMP_Z - C.AMP_H / 2.0 - 2.4)):
            Box(C.AMP_W + 5.6, 6.4, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        for sgn in (-1.0, 1.0):
            with Locations((C.AMP_X + sgn * (C.AMP_W / 2.0 + 1.8), -23.8, C.AMP_Z - 1.0)):
                Box(2.0, 6.4, C.AMP_H - 1.5)

        # 10. Dual Side Camera-Lens Bayonet Twist-Lock Receivers (0.35mm generous SLA clearance!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 36.8, Y_EAR, Z_EAR)):
                Cylinder(radius=4.55, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                Box(10.0, 4.4, 15.0, mode=Mode.SUBTRACT)
            with Locations((sgn * 34.0, Y_EAR + 5.6, Z_EAR + 3.5)):
                Box(4.0, 2.6, 2.6)
            with Locations((sgn * 34.0, Y_EAR - 5.6, Z_EAR - 3.5)):
                Box(4.0, 2.6, 2.6)

            # Dual Front Tapered Visor Mortise Slots carved directly into solid front corner cheeks (ZERO B04 protrusion!)
            add(_build_visor_wedge(sgn, y_tip=20.4, y_base=24.8, clearance=0.24), mode=Mode.SUBTRACT)

    return _tag(core.part, "A06_Head_Core", "charcoal")


# ---------------------------------------------------------------------------
# B04: Exact Filleted Wide Astronaut Helmet Shell (94.0 × 76.0 × 67.0 mm!)
# ---------------------------------------------------------------------------
def build_head_shell() -> Part:
    outer_dome = _build_helmet_outer_dome(inset=0.0, extend_bottom=0.0)

    # Exact concentric slip-in cavity: 79.0(W) × 64.0(D), Z up to 150.2 -> uniform >=2.5mm walls everywhere!
    # Leaves 0.50mm vertical slip-in clearance around A06_head_core (77.0 × 55.5)!
    inner_w, inner_d = 79.0, 64.0
    inner_z_top = C.HEAD_Z_TOP - 3.8  # 150.2 mm (3.8mm solid crown -> 1.6mm solid seat under A07!)
    inner_z_bot = C.HEAD_Z_BOT - 2.0  # 85.0 mm (completely open bottom)
    with BuildPart() as inner_bp:
        with BuildSketch(Plane.XY.offset(inner_z_bot)):
            with Locations((0, C.HEAD_Y_CTR)):
                RectangleRounded(inner_w, inner_d, radius=13.0)
        extrude(amount=inner_z_top - inner_z_bot)
        top_e = inner_bp.edges().filter_by(lambda e: abs(e.center().Z - inner_z_top) < 0.05)
        fillet(top_e, radius=8.5)

    with BuildPart() as shell:
        add(outer_dome)
        add(inner_bp.part, mode=Mode.SUBTRACT)

        # Clean Front Visor Aperture (72.0 × 52.0 mm, R=13.0 -> receives A08 with uniform 0.30mm gap!)
        with BuildSketch(Plane.XZ.offset(-18.0)):
            with Locations((0, VISOR_ZC)):
                RectangleRounded(72.0, 52.0, radius=13.0)
        extrude(amount=-30.0, mode=Mode.SUBTRACT)

        # Rear-Crown 3020 Speaker Through-Hole + Flat-Crown Stepped Seating Shelf for A07_Top_Grille
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.0)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(28.0, 18.0, radius=4.5)
        extrude(amount=8.0, mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 2.25)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(32.4, 22.4, radius=6.0)
        extrude(amount=4.0, mode=Mode.SUBTRACT)

        # Shallow 1.5mm Circular Ear Seat Recesses at |X|=45.5 + Vertical Bayonet Keyhole Apertures
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 50.5, Y_EAR, Z_EAR)):
                Cylinder(radius=12.6, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            with Locations((sgn * 43.0, Y_EAR, Z_EAR)):
                Cylinder(radius=4.55, height=16.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                Box(16.0, 4.4, 15.0, mode=Mode.SUBTRACT)

    return _tag(shell.part, "B04_Head_Shell", "white")


# ---------------------------------------------------------------------------
# A08: Flush Curved Pitch-Black Visor Mask (Uniform 3.6mm Wall + OV3660 Boss!)
# ---------------------------------------------------------------------------
def build_visor_mask() -> Part:
    outer_dome = _build_helmet_outer_dome(inset=0.0, extend_bottom=0.0)
    visor_inner = _build_helmet_outer_dome(inset=3.6, extend_bottom=2.0)

    with BuildPart() as clip_bp:
        with BuildSketch(Plane.XZ.offset(-22.0)):
            with Locations((0, VISOR_ZC)):
                RectangleRounded(71.4, 51.4, radius=12.7)
        extrude(amount=-24.0)

    with BuildPart() as visor:
        add(outer_dome)
        add(visor_inner, mode=Mode.SUBTRACT)
        add(clip_bp.part, mode=Mode.INTERSECT)

        # Solid Rear OV3660 Camera Mounting Boss fused cleanly into visor inner surface (Y=29.2..34.2)
        with Locations((0, 31.7, C.CAM_Z_CTR)):
            Box(14.4, 5.0, 14.4)

        # Twin Rear Tapered Wedge Tenons anchored cleanly at |X|=33.8 (strictly inside ±35.7 rim!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 33.8, 29.0, Z_EAR)):
                Box(2.8, 9.4, 9.2)
            add(_build_visor_wedge(sgn, y_tip=20.8, y_base=24.4, clearance=0.0))

        # OV3660 Lens Aperture (Ø8.8mm) + Forgiving 10.0×10.0mm Rear Camera Housing Pocket (+0.75mm/side!)
        with Locations((0, 34.0, C.CAM_Z_CTR)):
            Cylinder(radius=4.4, height=16.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        with Locations((0, C.CAM_Y_PCB + 2.0, C.CAM_Z_CTR)):
            Box(10.0, 5.4, 10.0, mode=Mode.SUBTRACT)

        # Oversized 2.0" GMT020-02 Active Display Window (42.8 × 32.6 mm -> +1.0mm margin/side!)
        with BuildSketch(Plane.XZ.offset(-20.0)):
            with Locations((0, C.LCD_Z_CTR)):
                RectangleRounded(42.8, 32.6, radius=4.5)
        extrude(amount=-24.0, mode=Mode.SUBTRACT)

    return _tag(visor.part, "A08_Visor_Mask", "visor_black")


# ---------------------------------------------------------------------------
# A07: Discreet Rear-Crown 3020 Speaker Acoustic Grille (Seated Flush on B04!)
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
    x_ctr = sgn * 48.8  # Outer dial |X|=45.8..51.8 (0.30mm clear of B04 pad at 45.5 -> proud & sleek!)

    with BuildPart() as pod:
        with Locations((x_ctr, Y_EAR, Z_EAR)):
            Cylinder(radius=12.0, height=6.0, rotation=(0, 90, 0))
        with Locations((x_ctr + sgn * 2.5, Y_EAR, Z_EAR)):
            Cylinder(radius=8.8, height=2.0, rotation=(0, 90, 0))
        with Locations((x_ctr + sgn * 3.6, Y_EAR, Z_EAR)):
            Box(1.8, 15.0, 3.4)
        # Concentric bayonet shaft (R=4.2mm inside R=4.55mm keyhole -> 0.35mm generous SLA fit!)
        with Locations((sgn * 39.2, Y_EAR, Z_EAR)):
            Cylinder(radius=4.2, height=13.6, rotation=(0, 90, 0))  # |X| = 32.4..46.0
        # Dual opposing inner bayonet locking lugs (|X|=32.4..34.6 -> 0.40mm clear behind A06 inner wall 35.0!)
        with Locations((sgn * 33.5, Y_EAR, Z_EAR)):
            Box(2.2, 14.0, 3.6)

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
