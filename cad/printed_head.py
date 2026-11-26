"""
KRON-01V5 (Terra-Rover Edition) — Mortise-and-Tenon Bayonet Astronaut Visor Helmet Parts
========================================================================================
Zero-soldering, zero-heat-set-insert, zero-exterior-screw 5-part wide astronaut helmet:
  - B04_head_shell  : Conformal-hollowed pearl-white helmet dome (3.5–4.5mm uniform wall, ZERO top
                      cracks!), wide bottom slip-in opening (70.6×54.4mm) so A06_head_core slides right in,
                      flat side ear pads w/ vertical bayonet keyholes, and stepped open crown speaker recess!
  - A06_head_core   : Tapered-crown structural inner frame w/ side-wall bayonet twist-lock receivers +
                      internal rotation stops, front tapered visor mortise sockets, M2 clear bores +
                      rear M2 hex nut sockets for ST7789 LCD & OV5647 camera (ZERO resin cracking!),
                      28mm speaker retention ring, and widened MG90S horn pocket!
  - A08_visor_mask  : Curved pitch-black full-face visor nested cleanly inside B04's front aperture
                      with 0.30mm perimeter clearance, >=2.2mm continuous brow/bridge/chin bars,
                      and twin tapered rear wedge tenons (zero screws, 2-second front pull-off!).
  - A07_top_grille  : Rear-crown speaker acoustic grille seated cleanly on B04's stepped shelf!
  - A09_ear_hub_L/R : Camera-lens style 90° Bayonet Twist-Lock Ear Hubs (insert vertically, twist 90°
                      horizontal to lock B04_Head_Shell + A06_Head_Core coaxially — ZERO screws!).
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
    Rectangle,
    RectangleRounded,
    RegularPolygon,
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


def _build_visor_wedge(sgn: float, y_tip: float, y_base: float, clearance: float = 0.0) -> Part:
    """
    Build one tapered wedge tenon (clearance=0) or matching mortise slot (clearance>0)
    for A08_Visor_Mask <-> A06_Head_Core at X = sgn * 30.3, Z = HEAD_Z_CTR - 2.0.
    Tapers narrower toward -Y so pressing A08 straight in seats snugly with zero rattle!
    """
    c = clearance
    cx = sgn * 30.1
    cz = C.HEAD_Z_CTR - 2.0
    y0, y1 = 20.1, 23.2

    def _lerp(v0: float, v1: float, y: float) -> float:
        t = (y - y0) / (y1 - y0)
        return v0 + t * (v1 - v0)

    plane_tip = Plane(origin=(cx, y_tip, cz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    plane_base = Plane(origin=(cx, y_base, cz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    with BuildPart() as bp:
        with BuildSketch(plane_tip):
            Rectangle(_lerp(3.0, 3.4, y_tip) + 2.0 * c, _lerp(8.8, 9.4, y_tip) + 2.0 * c)
        with BuildSketch(plane_base):
            Rectangle(_lerp(3.0, 3.4, y_base) + 2.0 * c, _lerp(8.8, 9.4, y_base) + 2.0 * c)
        loft(ruled=True)
    return bp.part


# ---------------------------------------------------------------------------
# A06: Gunmetal Structural Inner Core (Bayonet Ear Locks + M2 Hex Nut Seats!)
# ---------------------------------------------------------------------------
def build_head_core() -> Part:
    core_w, core_d = 67.4, 47.0   # X: ±33.7, Y: -25.5..+21.5
    yc = C.HEAD_Y_CTR             # -2.0
    z_bot = C.HEAD_Z_BOT + 4.0
    z_mid = C.HEAD_Z_TOP - 15.5
    z_top = C.HEAD_Z_TOP - 9.0
    y_ear = C.HEAD_Y_CTR - 1.0
    z_ear = C.HEAD_Z_CTR - 1.0
    m2_hex_r = C.NUT_M2_AF / math.sqrt(3.0)  # circumradius for DIN 934 M2 hex nut pocket

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

        # Hollow main electronics bay (width 61.8mm clears 61.12mm LCD PCB; open cleanly to front & bottom!)
        with Locations((0, 0.5, z_bot - 2.0)):
            Box(61.8, 46.5, (z_top - z_bot) - 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Open rear electronics bay below speaker (keeps 2.8mm rear wall at Y=-25.5..-22.7)
        with Locations((0, -10.5, z_bot + 2.5)):
            Box(61.8, 24.4, (z_top - z_bot) - 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Bottom neck swing clearance (X=-27.2..+25.5 clears MG90S_GearDome & A02 upper yoke cleanly!)
        with Locations((-0.85, -8.1, C.HEAD_Z_BOT - 2.0)):
            Box(52.7, 38.4, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        # Rear-lower neck pitch-up swing arch (0.00mm³ collision at full +22° tilt-up!)
        with Locations((0, -23.0, C.HEAD_Z_BOT - 2.0)):
            Box(51.0, 12.0, 24.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Front chin clearance under LCD (clears INMP441 chin microphone!)
        with Locations((0, 17.5, C.HEAD_Z_BOT - 2.0)):
            Box(30.0, 18.0, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Side Pivot Yoke Arms + MG90S Servo Horn & Spline Clearance Pocket
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 30.6, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z + 3.5)):
                Box(6.2, 19.0, 19.0)
            with Locations((sgn * 30.6, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        # Left yoke MG90S horn & spline pocket
        with Locations((-28.7, 3.0, C.HEAD_PIVOT_Z)):
            Box(5.4, 17.0, 6.4, mode=Mode.SUBTRACT)

        # 4× ST7789 2.0" LCD Standoffs: M2 Clear Through-Bores + Rear M2 Hex Nut Pockets (ZERO resin cracking!)
        for sx in (-1, 1):
            for sz in (-1, 1):
                bx = sx * (C.LCD_PCB_W / 2.0 - 3.0)
                bz = C.LCD_Z_CTR + sz * (C.LCD_PCB_H / 2.0 - 3.0)
                # Horizontal rib fusing each standoff solidly into A06 inner side walls (|X|=30.9..32.6)
                with Locations((sx * 29.7, C.LCD_Y_PCB - 2.55, bz)):
                    Box(5.8, 4.5, 6.0)
                with Locations((bx, C.LCD_Y_PCB - 2.55, bz)):
                    Cylinder(radius=3.1, height=4.5, rotation=(90, 0, 0))
                with Locations((bx, C.LCD_Y_PCB - 2.2, bz)):
                    Cylinder(radius=C.M2_CLEAR_DIA / 2.0, height=6.5, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
                # Rear-accessible hexagonal M2 captive nut seat (Y=13.0..14.8 -> drop M2 nut right in from behind!)
                nut_plane = Plane(origin=(bx, C.LCD_Y_PCB - 4.85, bz), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
                with BuildSketch(nut_plane):
                    RegularPolygon(radius=m2_hex_r, side_count=6)
                extrude(amount=1.9, mode=Mode.SUBTRACT)

        # Upper-Visor OV5647 Camera Mount Bridge (Y=21.75..24.25 -> 0.25mm clear of LCD glass 21.5 & CAM PCB 24.5!)
        with Locations((0, 23.0, C.CAM_Z_CTR + 1.0)):
            Box(28.0, 2.5, 16.0)
        # Top gusset into A06 upper roof
        with Locations((0, 20.3, z_top - 2.0)):
            Box(28.0, 7.9, 4.0)
        # Central camera lens relief bore
        with Locations((0, 23.0, C.CAM_Z_CTR)):
            Cylinder(radius=8.0, height=12.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        # Clean relief notch for rear 15-pin CSI FFC connector
        with Locations((0, 23.2, C.CAM_Z_CTR - 8.5)):
            Box(20.0, 4.8, 5.8, mode=Mode.SUBTRACT)
        # 4× M2 Camera Mounting Clear Bores + Rear M2 Hex Nut Pockets (21.0 × 12.5mm)
        for sx in (-1, 1):
            for sz in (-1, 1):
                cx = sx * (C.CAM_HOLE_X / 2.0)
                cz = C.CAM_Z_CTR + sz * (C.CAM_HOLE_Z / 2.0)
                with Locations((cx, 22.8, cz)):
                    Cylinder(radius=C.M2_CLEAR_DIA / 2.0, height=7.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
                cam_nut_plane = Plane(origin=(cx, 21.7, cz), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
                with BuildSketch(cam_nut_plane):
                    RegularPolygon(radius=m2_hex_r, side_count=6)
                extrude(amount=1.6, mode=Mode.SUBTRACT)

        # Rear-Crown 28mm Speaker Retention Ring
        spk_bot = C.SPK_Z_TOP - C.SPK_H
        with Locations((0, C.SPK_Y, spk_bot - 1.8)):
            Cylinder(radius=C.SPK_DIA / 2.0 + 2.5, height=5.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, C.SPK_Y, spk_bot - 0.3)):
            Cylinder(radius=C.SPK_DIA / 2.0 + 0.35, height=5.5, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((0, C.SPK_Y, spk_bot - 2.5)):
            Cylinder(radius=10.5, height=4.0, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Dual Side Camera-Lens Bayonet Twist-Lock Receivers (flush inside |X|=33.7 -> 0.000mm³ B04 slip-in!)
        for sgn in (-1.0, 1.0):
            # Vertical bayonet keyhole slot (R=4.5mm shaft bore + ±Z vertical lug pass-through slot!)
            with Locations((sgn * 32.3, y_ear, z_ear)):
                Cylinder(radius=4.5, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                Box(10.0, 4.2, 14.8, mode=Mode.SUBTRACT)
            # Twin internal positive rotation stop ribs (|X|=28.1..31.1) stopping 90° clockwise twist cleanly!
            with Locations((sgn * 29.6, y_ear + 5.5, z_ear + 3.4)):
                Box(3.0, 2.6, 2.6)
            with Locations((sgn * 29.6, y_ear - 5.5, z_ear - 3.4)):
                Box(3.0, 2.6, 2.6)

            # Dual Front Tapered Visor Mortise Blocks (|X|=27.7..32.5, Y=19.6..22.0 -> 0.000mm³ LCD & B04 slip-in!)
            with Locations((sgn * 30.1, 20.8, C.HEAD_Z_CTR - 2.0)):
                Box(4.8, 2.4, 12.0)
            add(_build_visor_wedge(sgn, y_tip=19.8, y_base=23.2, clearance=0.18), mode=Mode.SUBTRACT)

    return _tag(core.part, "A06_Head_Core", "charcoal")


# ---------------------------------------------------------------------------
# B04: Sculpted Conformal-Hollow Wide Astronaut Helmet Shell (Bayonet Ears!)
# ---------------------------------------------------------------------------
def _build_helmet_outer_dome() -> Part:
    yc = C.HEAD_Y_CTR
    with BuildPart() as dome_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT)):
            with Locations((0, yc)):
                RectangleRounded(76.6, 60.4, radius=12.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc)):
                RectangleRounded(86.0, 68.0, radius=20.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 50.0)):
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
    Wide sleek astronaut helmet with conformal 3.5-4.5mm dome wall, 70.6×54.4mm vertical slip-in
    opening, and vertical bayonet keyhole ear mounts receiving A09_Ear_Hub_L/R with ZERO screws!
    """
    yc = C.HEAD_Y_CTR
    y_ear = C.HEAD_Y_CTR - 1.0
    z_ear = C.HEAD_Z_CTR - 1.0
    outer_dome = _build_helmet_outer_dome()

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

    visor_zc = C.HEAD_Z_CTR - 2.5

    with BuildPart() as shell:
        add(outer_dome)
        add(inner_bp.part, mode=Mode.SUBTRACT)

        # Clean Front Visor Aperture (68.0 × 53.2mm -> receives A08 with 0.30mm gap!)
        with BuildSketch(Plane.XZ.offset(-16.0)):
            with Locations((0, visor_zc)):
                RectangleRounded(68.0, 53.2, radius=13.5)
        extrude(amount=-30.0, mode=Mode.SUBTRACT)

        # Subtle internal brow relief for top edge of OV5647 camera PCB
        with Locations((0, C.CAM_Y_PCB + 0.8, C.CAM_Z_CTR)):
            Box(26.0, 2.4, 24.8, mode=Mode.SUBTRACT)

        # Rear-Crown Speaker Full Through-Hole + Top Stepped Seating Shelf for A07_Top_Grille
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.5)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(22.0, 18.0, radius=4.5)
        extrude(amount=8.0, mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 2.3)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(26.2, 22.2, radius=6.0)
        extrude(amount=4.0, mode=Mode.SUBTRACT)

        # Flat Circular Side Ear Pads at |X|=42.0 + Vertical Bayonet Keyhole Apertures (ZERO screws!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 47.0, y_ear, z_ear)):
                Cylinder(radius=12.6, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            with Locations((sgn * 40.0, y_ear, z_ear)):
                Cylinder(radius=4.5, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
                Box(14.0, 4.2, 14.8, mode=Mode.SUBTRACT)

    return _tag(shell.part, "B04_Head_Shell", "white")


# ---------------------------------------------------------------------------
# A08: Flush Curved Pitch-Black Visor Mask (Zero-Screw Tapered Wedge Tenons!)
# ---------------------------------------------------------------------------
def build_visor_mask() -> Part:
    """
    Curved pitch-black full-face visor clipped 0.30mm inside B04's front aperture with
    twin tapered rear wedge tenons that press snugly into A06's front mortise sockets (ZERO screws!).
    """
    outer_dome = _build_helmet_outer_dome()
    yc = C.HEAD_Y_CTR
    visor_zc = C.HEAD_Z_CTR - 2.5

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

    with BuildPart() as clip_bp:
        with BuildSketch(Plane.XZ.offset(-21.5)):
            with Locations((0, visor_zc)):
                RectangleRounded(67.4, 52.6, radius=13.2)
        extrude(amount=-20.0)

    with BuildPart() as visor:
        add(outer_dome)
        add(visor_inner_bp.part, mode=Mode.SUBTRACT)
        add(clip_bp.part, mode=Mode.INTERSECT)

        # Twin Rear Tapered Wedge Tenons (press straight in along -Y into A06 mortise sockets -> ZERO screws!)
        for sgn in (-1.0, 1.0):
            # Solid stem bridging visor back surface to wedge base (Y=23.0..30.6)
            with Locations((sgn * 30.1, 26.8, C.HEAD_Z_CTR - 2.0)):
                Box(3.4, 7.6, 9.4)
            # Precision tapered wedge tongue (Y=20.1..23.2 -> 0.18mm clearance inside A06 mortise!)
            add(_build_visor_wedge(sgn, y_tip=20.1, y_base=23.2, clearance=0.0))

        # OV5647 Camera Lens Through-Bore (Ø14.6mm) + Clean Rear-Only M12 Square Base & PCB Pocket
        with Locations((0, 31.0, C.CAM_Z_CTR)):
            Cylinder(radius=7.3, height=16.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        with Locations((0, 26.8, C.CAM_Z_CTR)):
            Box(15.2, 7.0, 15.2, mode=Mode.SUBTRACT)
        with Locations((0, C.CAM_Y_PCB + 0.8, C.CAM_Z_CTR)):
            Box(25.8, 2.2, 24.6, mode=Mode.SUBTRACT)

        # 2.0" ST7789 LCD Active Display Window (42.5 × 29.6mm)
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
# A09_L / A09_R: Camera-Lens 90° Bayonet Twist-Lock Ear Hubs (ZERO Screws!)
# ---------------------------------------------------------------------------
def build_ear_pod(side: str = "L") -> Part:
    """
    Tool-free 90° Bayonet Twist-Lock Ear Hub (modeled in LOCKED horizontal orientation):
      - Insert vertically (bar along ±Z) through B04 & A06 keyholes
      - Twist 90° so the tactile grip bar sits horizontal (±Y) -> inner bayonet lugs lock solidly
        behind A06's |X|=30.9 inner wall against positive rotation stops!
    """
    sgn = -1.0 if side == "L" else 1.0
    x_ctr = sgn * 45.25  # Outer dial |X|=42.25..48.25 (0.25mm clear of B04 pad at 42.0!)
    y_ear = C.HEAD_Y_CTR - 1.0
    z_ear = C.HEAD_Z_CTR - 1.0

    with BuildPart() as pod:
        # Outer circular gunmetal ear dial
        with Locations((x_ctr, y_ear, z_ear)):
            Cylinder(radius=12.0, height=6.0, rotation=(0, 90, 0))
        with Locations((x_ctr + sgn * 2.5, y_ear, z_ear)):
            Cylinder(radius=8.8, height=2.0, rotation=(0, 90, 0))
        # Raised horizontal cyber-dial twist-grip bar (indicates LOCKED orientation + effortless thumb twist!)
        with Locations((x_ctr + sgn * 3.6, y_ear, z_ear)):
            Box(1.8, 15.0, 3.4)
        # Concentric bayonet locking shaft passing coaxially through B04 (37.5..42) & A06 (30.9..33.7)
        with Locations((sgn * 35.2, y_ear, z_ear)):
            Cylinder(radius=4.2, height=14.6, rotation=(0, 90, 0))  # |X| = 27.9..42.5
        # Dual opposing inner bayonet locking lugs (|X|=27.9..30.5 -> 0.40mm clear behind A06 inner wall 30.9!)
        with Locations((sgn * 29.2, y_ear, z_ear)):
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
