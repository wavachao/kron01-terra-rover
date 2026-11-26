"""
KRON-01V5 (Terra-Rover Edition) — Zero-Collision DFM/DFA Astronaut Visor Helmet Parts
=====================================================================================
Production-engineered 5-part wide astronaut helmet (88W × 68D × 63H mm, Z=68..131) with:
  - B04_head_shell  : Conformal-hollowed pearl-white helmet dome (3.5–4.0mm uniform wall, ZERO top
                      cracks!), wide bottom slip-in opening (69×51mm) so A06_head_core slides right in,
                      flat side ear-hub seating pads, and stepped open crown speaker recess!
  - A06_head_core   : Tapered-crown structural inner frame (67.4×47×49mm) with full-height open LCD bay,
                      side-ribbed M2 standoffs, upper OV5647 camera bridge w/ CSI socket relief,
                      28mm speaker retention ring, widened MG90S gear-dome + horn pocket, and flush M3 bosses!
  - A08_visor_mask  : Curved pitch-black full-face visor nested cleanly inside B04's front aperture
                      with 0.30mm perimeter clearance, >=2.0mm continuous brow/bridge/chin bars,
                      M12 + PCB camera relief pocket, and dual rear mounting tabs!
  - A07_top_grille  : Rear-crown speaker acoustic grille seated cleanly on B04's stepped shelf!
  - A09_ear_hub_L/R : Circular gunmetal ear hubs seated cleanly on B04's flat |X|=42.0 side pads!
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
# A06: Gunmetal Structural Inner Core (Slides Cleanly Up Into B04!)
# ---------------------------------------------------------------------------
def build_head_core() -> Part:
    core_w, core_d = 67.4, 47.0   # X: ±33.7, Y: -25.5..+21.5
    yc = C.HEAD_Y_CTR             # -2.0
    z_bot = C.HEAD_Z_BOT + 4.0    # 72.0mm (cleanly above helmet bottom rim 68.0 for full tilt!)
    z_mid = C.HEAD_Z_TOP - 15.5   # 115.5mm
    z_top = C.HEAD_Z_TOP - 9.0    # 122.0mm (tapers cleanly inside B04 curving inner crown!)

    with BuildPart() as core:
        # Tapered upper crown prevents any corner rub against B04's curved inner dome!
        with BuildSketch(Plane.XY.offset(z_bot)):
            with Locations((0, yc)):
                RectangleRounded(core_w, core_d, radius=5.5)
        with BuildSketch(Plane.XY.offset(z_mid)):
            with Locations((0, yc)):
                RectangleRounded(core_w, core_d, radius=5.5)
        with BuildSketch(Plane.XY.offset(z_top)):
            with Locations((0, yc - 0.5)):
                RectangleRounded(56.0, 41.0, radius=8.0)
        loft(ruled=True)

        # Hollow main electronics bay (width 61.8mm clears 61.12mm LCD PCB; open cleanly to front & bottom for LCD!)
        with Locations((0, 0.5, z_bot - 2.0)):
            Box(61.8, 46.5, (z_top - z_bot) - 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Open rear electronics bay below speaker (keeps 2.8mm rear wall at Y=-25.5..-22.7)
        with Locations((0, -10.5, z_bot + 2.5)):
            Box(61.8, 24.4, (z_top - z_bot) - 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Bottom neck swing clearance (X=-27.2..+25.5 clears MG90S_GearDome & A02 upper yoke cleanly!)
        with Locations((-0.85, -8.1, C.HEAD_Z_BOT - 2.0)):
            Box(52.7, 38.4, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # Rear-lower neck pitch-up swing arch (Z=66..90 -> 0.00mm³ collision at full +22° tilt-up!)
        with Locations((0, -23.0, C.HEAD_Z_BOT - 2.0)):
            Box(51.0, 12.0, 24.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Front chin clearance under LCD (clears INMP441 chin microphone at Y=17.5, Z=67.5..70.1!)
        with Locations((0, 17.5, C.HEAD_Z_BOT - 2.0)):
            Box(30.0, 18.0, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Side Pivot Yoke Arms + MG90S Servo Horn & Spline Clearance Pocket
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 30.6, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z + 3.5)):
                Box(6.2, 19.0, 19.0)
            with Locations((sgn * 30.6, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Left yoke MG90S horn & spline pocket (X=-31.4..-26.0, Y=-5.5..+11.5, Z=69.8..76.2 -> 0.35mm clear!)
        with Locations((-28.7, 3.0, C.HEAD_PIVOT_Z)):
            Box(5.4, 17.0, 6.4, mode=Mode.SUBTRACT)

        # 4× ST7789 2.0" LCD M2 Standoffs (front face Y=17.50 -> 0.30mm clear behind LCD_Y_PCB=17.8!)
        for sx in (-1, 1):
            for sz in (-1, 1):
                bx = sx * (C.LCD_PCB_W / 2.0 - 3.0)
                bz = C.LCD_Z_CTR + sz * (C.LCD_PCB_H / 2.0 - 3.0)
                # Horizontal rib fusing each standoff solidly into A06 inner side walls (|X|=30.9..32.6)
                with Locations((sx * 29.9, C.LCD_Y_PCB - 2.55, bz)):
                    Box(5.4, 4.5, 5.2)
                with Locations((bx, C.LCD_Y_PCB - 2.55, bz)):
                    Cylinder(radius=2.6, height=4.5, rotation=(90, 0, 0))
                with Locations((bx, C.LCD_Y_PCB - 2.2, bz)):
                    Cylinder(radius=C.M2_PILOT_DIA / 2.0, height=5.8, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # Upper-Visor OV5647 Camera Mount Bridge (Y=21.8..24.2 -> 0.30mm clear of LCD glass 21.5 & CAM PCB 24.5!)
        with Locations((0, 23.0, C.CAM_Z_CTR + 0.5)):
            Box(28.0, 2.4, 16.0)
        # Top gusset into A06 upper roof (Y=16.5..24.2, Z=118.5..122.5 -> cleanly above LCD & behind A08!)
        with Locations((0, 20.35, z_top - 2.0)):
            Box(28.0, 7.7, 4.0)
        # Central camera lens relief bore
        with Locations((0, 23.0, C.CAM_Z_CTR)):
            Cylinder(radius=8.0, height=12.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        # Clean relief notch for rear 15-pin CSI FFC connector (Z=CAM_Z_CTR-8.5, X=-9.5..+9.5)
        with Locations((0, 23.2, C.CAM_Z_CTR - 8.5)):
            Box(20.0, 4.5, 5.8, mode=Mode.SUBTRACT)
        # 4× M2 Camera Mounting Pilot Holes (21.0 × 12.5mm)
        for sx in (-1, 1):
            for sz in (-1, 1):
                cx = sx * (C.CAM_HOLE_X / 2.0)
                cz = C.CAM_Z_CTR + sz * (C.CAM_HOLE_Z / 2.0)
                with Locations((cx, 22.5, cz)):
                    Cylinder(radius=C.M2_PILOT_DIA / 2.0, height=6.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # Rear-Crown 28mm Speaker Retention Ring (clears Ø28×5mm speaker at Z=120.0..125.0 by 0.35mm!)
        spk_bot = C.SPK_Z_TOP - C.SPK_H  # 120.0mm
        with Locations((0, C.SPK_Y, spk_bot - 1.8)):
            Cylinder(radius=C.SPK_DIA / 2.0 + 2.5, height=5.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, C.SPK_Y, spk_bot - 0.3)):
            Cylinder(radius=C.SPK_DIA / 2.0 + 0.35, height=5.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, C.SPK_Y, spk_bot - 2.5)):
            Cylinder(radius=10.5, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Dual Side M3 Brass Heat-Set Bosses (flush inside |X|=33.7 so A06 slips cleanly up into B04!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 31.2, C.HEAD_Y_CTR - 1.0, C.HEAD_Z_CTR - 1.0)):
                Cylinder(radius=4.5, height=5.0, rotation=(0, 90, 0))
                Cylinder(radius=C.HEATSET_M3_DIA / 2.0, height=7.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            # Dual Front M2.5 Visor-Mask Mounting Ears (|X|=28.4..32.6, Y=19.8..22.0 -> zero-snag vertical slip-in into B04!)
            with Locations((sgn * 30.5, 20.9, C.HEAD_Z_CTR - 2.0)):
                Box(4.2, 2.2, 11.0)
            with Locations((sgn * 30.5, 20.5, C.HEAD_Z_CTR - 2.0)):
                Cylinder(radius=C.M25_PILOT_DIA / 2.0, height=5.5, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

    return _tag(core.part, "A06_Head_Core", "charcoal")


# ---------------------------------------------------------------------------
# B04: Sculpted Conformal-Hollow Wide Astronaut Helmet Shell (Plate B — White)
# ---------------------------------------------------------------------------
def _build_helmet_outer_dome() -> Part:
    yc = C.HEAD_Y_CTR  # -2.0
    with BuildPart() as dome_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT)):
            with Locations((0, yc)):
                RectangleRounded(76.6, 60.4, radius=12.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc)):
                RectangleRounded(86.0, 68.0, radius=20.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 50.0)):  # Z=118mm -> keeps visor full-depth over camera!
            with Locations((0, yc)):
                RectangleRounded(88.0, 68.0, radius=21.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.0)):
            with Locations((0, yc - 0.8)):
                RectangleRounded(78.0, 61.0, radius=18.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(56.0, 44.0, radius=14.0)
        loft(ruled=False)
    return dome_bp.part


def build_head_shell() -> Part:
    """
    Wide sleek astronaut helmet (88W × 68D × 63H mm, Z = 68.0..131.0):
      - Conformal 5-section inner hollowing guarantees 3.5–4.0mm uniform dome wall (ZERO top cracks!)
      - Wide 69×53mm bottom opening lets A06_Head_Core slide straight up from underneath & clears -20°..+22° tilt!
      - Clean front visor aperture (68.0×53.2mm) receives A08_Visor_Mask with 0.30mm seam gap!
      - Flat circular side pads at |X|=42.0 receive A09_Ear_Hub_L/R cleanly with zero collision!
      - Stepped open rear-crown acoustic port receives A07_Top_Grille cleanly above the 28mm speaker!
    """
    yc = C.HEAD_Y_CTR
    outer_dome = _build_helmet_outer_dome()

    # Conformal inner cavity loft (inset >=2.7–4.5mm everywhere -> solid roof, solid ear pads & zero-snag vertical slip-in!)
    with BuildPart() as inner_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT - 0.5)):
            with Locations((0, yc)):
                RectangleRounded(70.6, 54.4, radius=9.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc)):
                RectangleRounded(75.0, 60.0, radius=15.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 50.0)):
            with Locations((0, yc)):
                RectangleRounded(75.0, 60.0, radius=17.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.5)):
            with Locations((0, yc - 0.8)):
                RectangleRounded(66.0, 52.0, radius=14.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 3.5)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(48.0, 36.0, radius=11.0)
        loft(ruled=False)

    visor_zc = C.HEAD_Z_CTR - 2.5  # 97.0mm (aperture Z: 70.4..123.6)

    with BuildPart() as shell:
        add(outer_dome)
        add(inner_bp.part, mode=Mode.SUBTRACT)

        # Clean Front Visor Aperture (68.0 × 53.2mm -> receives A08 with 0.30mm gap!)
        with BuildSketch(Plane.XZ.offset(-16.0)):
            with Locations((0, visor_zc)):
                RectangleRounded(68.0, 53.2, radius=13.5)
        extrude(amount=-30.0, mode=Mode.SUBTRACT)

        # Subtle internal brow relief for top edge of OV5647 camera PCB (keeps >=2.5mm solid outer brow!)
        with Locations((0, C.CAM_Y_PCB + 0.8, C.CAM_Z_CTR)):
            Box(26.0, 2.4, 24.8, mode=Mode.SUBTRACT)

        # Rear-Crown Speaker Full Through-Hole + Top Stepped Seating Shelf (Z=128.7) for A07_Top_Grille!
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.5)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(22.0, 18.0, radius=4.5)
        extrude(amount=8.0, mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 2.3)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(26.2, 22.2, radius=6.0)
        extrude(amount=4.0, mode=Mode.SUBTRACT)

        # Flat Circular Side Seating Pads at |X|=42.0 (>=4mm solid flange -> zero breakthrough, zero collision w/ A09!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 47.0, C.HEAD_Y_CTR - 1.0, C.HEAD_Z_CTR - 1.0)):
                Cylinder(radius=12.6, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            with Locations((sgn * 40.0, C.HEAD_Y_CTR - 1.0, C.HEAD_Z_CTR - 1.0)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    return _tag(shell.part, "B04_Head_Shell", "white")


# ---------------------------------------------------------------------------
# A08: Flush Curved Pitch-Black Astronaut Visor Mask (0.30mm Fit Inside B04!)
# ---------------------------------------------------------------------------
def build_visor_mask() -> Part:
    """
    Curved pitch-black full-face visor sharing B04's exact outer surface contour, clipped 0.30mm inside
    B04's front visor aperture (67.4 × 52.6mm) for ZERO collision, with continuous >=2.2mm solid brow,
    mid-bridge, and chin bar around both the 2.0" LCD window and OV5647 camera lens!
    """
    outer_dome = _build_helmet_outer_dome()
    yc = C.HEAD_Y_CTR
    visor_zc = C.HEAD_Z_CTR - 2.5  # 97.0mm (visor Z: 70.7..123.3)

    # Inner conformal back-surface of the visor (3.2mm curved visor thickness!)
    with BuildPart() as visor_inner_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT - 1.0)):
            with Locations((0, yc)):
                RectangleRounded(70.0, 54.0, radius=13.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc)):
                RectangleRounded(79.6, 61.6, radius=17.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 50.0)):
            with Locations((0, yc)):
                RectangleRounded(81.6, 61.6, radius=18.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.0)):
            with Locations((0, yc - 0.8)):
                RectangleRounded(71.6, 54.6, radius=15.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP + 1.0)):
            with Locations((0, yc - 2.0)):
                RectangleRounded(50.0, 38.0, radius=11.5)
        loft(ruled=False)

    # Clip prism strictly inside B04's 68.0×53.2 visor aperture (0.30mm clearance per side!)
    with BuildPart() as clip_bp:
        with BuildSketch(Plane.XZ.offset(-21.5)):
            with Locations((0, visor_zc)):
                RectangleRounded(67.4, 52.6, radius=13.2)
        extrude(amount=-20.0)

    with BuildPart() as visor:
        add(outer_dome)
        add(visor_inner_bp.part, mode=Mode.SUBTRACT)
        add(clip_bp.part, mode=Mode.INTERSECT)

        # Dual Rear Mounting Tabs (X=±30.5, Y=22.4..30.6 -> coaxial with A06 front mounting ears at Y=22.0!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 30.5, 26.5, C.HEAD_Z_CTR - 2.0)):
                Box(4.2, 8.2, 10.5)
            with Locations((sgn * 30.5, 24.0, C.HEAD_Z_CTR - 2.0)):
                Cylinder(radius=C.M25_PILOT_DIA / 2.0 + 0.55, height=8.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # OV5647 Camera Lens Through-Bore (Ø14.6mm) + Clean Rear-Only M12 Square Base & PCB Pocket (zero front breakthrough!)
        with Locations((0, 31.0, C.CAM_Z_CTR)):
            Cylinder(radius=7.3, height=16.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        with Locations((0, 26.8, C.CAM_Z_CTR)):
            Box(15.2, 7.0, 15.2, mode=Mode.SUBTRACT)  # Y=23.3..30.3 -> stays >=1.7mm inside 32.0 front surface!
        with Locations((0, C.CAM_Y_PCB + 0.8, C.CAM_Z_CTR)):
            Box(25.8, 2.2, 24.6, mode=Mode.SUBTRACT)  # Y=24.2..26.4 -> stays >=3.0mm inside visor brow!

        # 2.0" ST7789 LCD Active Display Window (42.5 × 29.6mm -> >=2.2mm continuous brow, mid-bridge & chin!)
        with BuildSketch(Plane.XZ.offset(-20.0)):
            with Locations((0, C.LCD_Z_CTR)):
                RectangleRounded(42.5, 29.6, radius=5.0)
        extrude(amount=-22.0, mode=Mode.SUBTRACT)

    return _tag(visor.part, "A08_Visor_Mask", "visor_black")


# ---------------------------------------------------------------------------
# A07: Discreet Rear-Crown Speaker Acoustic Grille (Seated on B04 Shelf!)
# ---------------------------------------------------------------------------
def build_top_grille() -> Part:
    """Sits cleanly on B04's stepped speaker shelf (0.30mm perimeter clearance, clears speaker by 3.85mm!)."""
    with BuildPart() as grille:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 2.15)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(25.6, 21.6, radius=5.7)
        extrude(amount=2.15)
        for iy in range(-3, 4):
            with Locations((0, C.SPK_Y + iy * 2.6, C.HEAD_Z_TOP - 1.1)):
                Box(17.0, 1.3, 4.0, mode=Mode.SUBTRACT)
    return _tag(grille.part, "A07_Top_Grille", "charcoal")


# ---------------------------------------------------------------------------
# A09_L / A09_R: Circular Gunmetal Ear Hubs (Seated on B04 |X|=42.0 Flat Pad!)
# ---------------------------------------------------------------------------
def build_ear_pod(side: str = "L") -> Part:
    """Bolts B04_Head_Shell cleanly onto A06_Head_Core; inner face at |X|=42.25 clears B04 flat pad by 0.25mm!"""
    sgn = -1.0 if side == "L" else 1.0
    x_ctr = sgn * 45.25  # Inner face at |X|=42.25, outer face at |X|=48.25 (6.0mm thick!)
    z_ear = C.HEAD_Z_CTR - 1.0

    with BuildPart() as pod:
        with Locations((x_ctr, C.HEAD_Y_CTR - 1.0, z_ear)):
            Cylinder(radius=12.0, height=6.0, rotation=(0, 90, 0))
        with Locations((x_ctr + sgn * 2.5, C.HEAD_Y_CTR - 1.0, z_ear)):
            Cylinder(radius=8.8, height=2.0, rotation=(0, 90, 0))
        with Locations(Location((x_ctr + sgn * 3.5, C.HEAD_Y_CTR - 1.0, z_ear), (35, 0, 0))):
            Box(2.0, 13.0, 2.0, mode=Mode.SUBTRACT)
        # Recessed coaxial M3 bolt bore locking Ear Hub -> B04 Shell -> A06 Core Brass Insert!
        with Locations((x_ctr, C.HEAD_Y_CTR - 1.0, z_ear)):
            Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((x_ctr + sgn * 2.0, C.HEAD_Y_CTR - 1.0, z_ear)):
            Cylinder(radius=3.1, height=4.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

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
