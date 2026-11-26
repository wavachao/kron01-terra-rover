"""
KRON-01V5 (Terra-Rover Edition) — Wide-Sleek Astronaut Visor Helmet Head Parts
===============================================================================
Replaces the tall square marshmallow head + ugly protruding forehead donut with a
true consumer-product Terra-Rover wide astronaut helmet (86W × 66D × 58H mm):
  - B04_head_shell  : Smooth organic lofted pearl-white helmet dome (1.48:1 wide proportion!)
  - A08_visor_mask  : Edge-to-edge curved glossy pitch-black full-face visor seamlessly
                      integrating BOTH the 2.0" ST7789V display AND upper-center OV5647 lens!
  - A06_head_core   : Gunmetal structural inner frame + sleek chin jaw trim
  - A07_top_grille  : Discreet rear-crown speaker acoustic grille
  - A09_ear_pod_L/R : Circular gunmetal headphone-style ear hubs with diagonal metallic accent
"""

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
    fillet,
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
# A06: Gunmetal Structural Inner Core + Chin Trim (Plate A — Charcoal)
# ---------------------------------------------------------------------------
def build_head_core() -> Part:
    core_w, core_d, core_h = 70.0, 50.0, 48.0
    yc, zc = C.HEAD_Y_CTR - 1.5, C.HEAD_Z_CTR

    with BuildPart() as core:
        with BuildSketch(Plane.XY.offset(zc - core_h / 2.0)):
            with Locations((0, yc)):
                RectangleRounded(core_w, core_d, radius=11.0)
        extrude(amount=core_h)

        # Hollow main electronics bay
        with Locations((0, yc - 1.5, zc - 0.5)):
            Box(core_w - 6.0, core_d - 5.0, core_h - 5.0, mode=Mode.SUBTRACT)

        # Bottom neck swing clearance
        with Locations((0, C.NECK_Y_CTR, C.HEAD_PIVOT_Z - 2.0)):
            Box(C.NECK_W + 4.0, C.NECK_D + 12.0, 20.0, mode=Mode.SUBTRACT)

        # Side Pivot Yoke Arms + MG90S servo horn pocket
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 30.5, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z + 4.0)):
                Box(6.0, 18.0, 20.0)
            with Locations((sgn * 30.5, C.HEAD_PIVOT_Y, C.HEAD_PIVOT_Z)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((-31.0, C.HEAD_PIVOT_Y + 5.0, C.HEAD_PIVOT_Z)):
            Box(3.0, 16.5, 6.0, mode=Mode.SUBTRACT)

        # Front 2.0" LCD Active Window Cutout + 4× M2 Bosses
        with Locations((0, C.LCD_Y_PCB + 2.0, C.LCD_Z_CTR)):
            Box(C.LCD_AA_W + 4.0, 14.0, C.LCD_AA_H + 3.0, mode=Mode.SUBTRACT)
        for sx in (-1, 1):
            for sz in (-1, 1):
                bx = sx * (C.LCD_PCB_W / 2.0 - 3.0)
                bz = C.LCD_Z_CTR + sz * (C.LCD_PCB_H / 2.0 - 3.0)
                with Locations((bx, C.LCD_Y_PCB - 2.5, bz)):
                    Cylinder(radius=2.6, height=4.5, rotation=(90, 0, 0))
                with Locations((bx, C.LCD_Y_PCB - 2.0, bz)):
                    Cylinder(radius=C.M2_PILOT_DIA / 2.0, height=6.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # Upper-Visor OV5647 Camera Mount + 4× M2 Bosses (21.0 × 12.5mm)
        with Locations((0, C.CAM_Y_PCB - 2.0, C.CAM_Z_CTR)):
            Box(28.0, 3.0, 22.0)
        with Locations((0, C.CAM_Y_PCB + 1.0, C.CAM_Z_CTR)):
            Cylinder(radius=8.0, height=14.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        for sx in (-1, 1):
            for sz in (-1, 1):
                cx = sx * (C.CAM_HOLE_X / 2.0)
                cz = C.CAM_Z_CTR + sz * (C.CAM_HOLE_Z / 2.0)
                with Locations((cx, C.CAM_Y_PCB - 1.5, cz)):
                    Cylinder(radius=2.2, height=3.5, rotation=(90, 0, 0))
                with Locations((cx, C.CAM_Y_PCB - 1.0, cz)):
                    Cylinder(radius=C.M2_PILOT_DIA / 2.0, height=5.5, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # Rear-Crown 28mm Speaker Retention Ring
        with Locations((0, C.SPK_Y, C.SPK_Z_TOP - 3.0)):
            Cylinder(radius=C.SPK_DIA / 2.0 + 2.5, height=6.0)
        with Locations((0, C.SPK_Y, C.SPK_Z_TOP - 2.5)):
            Cylinder(radius=C.SPK_DIA / 2.0 + 0.3, height=6.5, mode=Mode.SUBTRACT)

        # Chin INMP441 Mic Acoustic Pinhole
        with Locations((0, C.MIC_Y + 4.0, C.MIC_Z)):
            Cylinder(radius=1.8, height=12.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # Dual Side M3 Brass Heat-Set Bosses (locks B04_Head_Shell cleanly hidden behind A09_Ear_Hubs!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * (core_w / 2.0 - 2.0), C.HEAD_Y_CTR - 2.0, C.HEAD_Z_CTR - 1.0)):
                Cylinder(radius=4.2, height=6.0, rotation=(0, 90, 0))
                Cylinder(radius=C.HEATSET_M3_DIA / 2.0, height=8.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            # Dual Front M2.5 Visor-Mask Mounting Ears (locks A08_Visor_Mask flush!)
            with Locations((sgn * 32.0, C.HEAD_Y_CTR + 18.0, C.HEAD_Z_CTR - 1.0)):
                Cylinder(radius=3.0, height=5.0, rotation=(90, 0, 0))
                Cylinder(radius=C.M25_PILOT_DIA / 2.0, height=7.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

    return _tag(core.part, "A06_Head_Core", "charcoal")


# ---------------------------------------------------------------------------
# B04: Sculpted Organic Wide Astronaut Helmet Shell (Plate B — Pearl White)
# ---------------------------------------------------------------------------
def build_head_shell() -> Part:
    """
    Terra-Rover wide sleek astronaut helmet (86W × 66D × 58H mm, Z = 64.5..122.5):
      - Smooth 5-section organic loft; slips cleanly over A06_Head_Core after neck pivot is bolted!
      - Locked rock-solid via 2× coaxial M3 side bolts hidden cleanly behind A09_Ear_Hubs!
    """
    yc = C.HEAD_Y_CTR

    with BuildPart() as dome_bp:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT)):
            with Locations((0, yc + 1.0)):
                RectangleRounded(66.0, 50.0, radius=16.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 12.0)):
            with Locations((0, yc + 0.5)):
                RectangleRounded(84.0, 64.0, radius=20.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_CTR + 11.0)):
            with Locations((0, yc)):
                RectangleRounded(86.0, 66.0, radius=21.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 7.0)):
            with Locations((0, yc - 2.5)):
                RectangleRounded(74.0, 56.0, radius=18.0)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP)):
            with Locations((0, yc - 4.0)):
                RectangleRounded(50.0, 38.0, radius=14.0)
        loft(ruled=False)

    with BuildPart() as shell:
        add(dome_bp.part)

        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 3.5)):
            with Locations((0, yc - 1.0)):
                RectangleRounded(72.0, 53.0, radius=14.0)
        extrude(amount=49.5, mode=Mode.SUBTRACT)

        with Locations((0, C.NECK_Y_CTR, C.HEAD_Z_BOT)):
            Box(56.0, 40.0, 12.0, mode=Mode.SUBTRACT)

        with BuildSketch(Plane.XZ.offset(-(C.HEAD_Y_FRONT - 14.0))):
            with Locations((0, C.HEAD_Z_CTR - 1.0)):
                RectangleRounded(74.0, 42.0, radius=13.0)
        extrude(amount=-24.0, mode=Mode.SUBTRACT)

        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 5.5)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(26.0, 22.0, radius=6.0)
        extrude(amount=8.0, mode=Mode.SUBTRACT)

        # Unified Side M3 Shell-Lock Through-Holes (aligned directly with A06 bosses & A09 ear hubs!)
        for sgn in (-1.0, 1.0):
            with Locations((sgn * (C.HEAD_W / 2.0 - 2.0), C.HEAD_Y_CTR - 2.0, C.HEAD_Z_CTR - 1.0)):
                Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=14.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    return _tag(shell.part, "B04_Head_Shell", "white")


# ---------------------------------------------------------------------------
# A08: Flush Curved Edge-to-Edge Pitch-Black Astronaut Visor Mask (Plate A)
# ---------------------------------------------------------------------------
def build_visor_mask() -> Part:
    yc = C.HEAD_Y_CTR
    with BuildPart() as visor:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_BOT + 4.0)):
            with Locations((0, yc + 1.0)):
                RectangleRounded(78.0, 61.5, radius=18.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_CTR + 11.0)):
            with Locations((0, yc + 0.5)):
                RectangleRounded(84.5, 65.5, radius=20.5)
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 6.0)):
            with Locations((0, yc - 1.5)):
                RectangleRounded(74.0, 58.0, radius=18.0)
        loft(ruled=False)

        with Locations((0, -24.0, C.HEAD_Z_CTR)):
            Box(100.0, 80.0, 80.0, mode=Mode.SUBTRACT)
        with Locations((0, 26.0, C.HEAD_Z_BOT - 8.0)):
            Box(100.0, 40.0, 30.0, mode=Mode.SUBTRACT)
        with Locations((0, 26.0, C.HEAD_Z_TOP + 6.5)):
            Box(100.0, 40.0, 28.0, mode=Mode.SUBTRACT)

        with Locations((0, 15.0, C.HEAD_Z_CTR - 1.0)):
            Box(68.0, 18.0, 44.0, mode=Mode.SUBTRACT)

        # Dual Rear Alignment & Snap-Clip Tabs engaging A06_Head_Core cleanly!
        for sgn in (-1.0, 1.0):
            with Locations((sgn * 34.5, 19.5, C.HEAD_Z_CTR - 1.0)):
                Box(3.0, 7.0, 12.0)

        with Locations((0, C.HEAD_Y_FRONT - 2.0, C.CAM_Z_CTR)):
            Cylinder(radius=7.3, height=16.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        with BuildSketch(Plane.XZ.offset(-(C.HEAD_Y_FRONT - 12.0))):
            with Locations((0, C.LCD_Z_CTR)):
                RectangleRounded(C.LCD_AA_W + 2.5, C.LCD_AA_H + 1.5, radius=6.0)
        extrude(amount=-18.0, mode=Mode.SUBTRACT)

    return _tag(visor.part, "A08_Visor_Mask", "visor_black")


# ---------------------------------------------------------------------------
# A07: Discreet Rear-Crown Speaker Acoustic Grille (Plate A — Gunmetal)
# ---------------------------------------------------------------------------
def build_top_grille() -> Part:
    with BuildPart() as grille:
        with BuildSketch(Plane.XY.offset(C.HEAD_Z_TOP - 3.6)):
            with Locations((0, C.SPK_Y)):
                RectangleRounded(25.5, 21.5, radius=5.5)
        extrude(amount=3.2)
        for iy in range(-3, 4):
            with Locations((0, C.SPK_Y + iy * 2.8, C.HEAD_Z_TOP - 2.0)):
                Box(17.0, 1.3, 6.0, mode=Mode.SUBTRACT)
    return _tag(grille.part, "A07_Top_Grille", "charcoal")


# ---------------------------------------------------------------------------
# A09_L / A09_R: Circular Gunmetal Ear Hubs (Bolt-Through Locking B04 + A06!)
# ---------------------------------------------------------------------------
def build_ear_pod(side: str = "L") -> Part:
    """Bolts B04_Head_Shell cleanly onto A06_Head_Core via coaxial M3 screw recessed inside hub."""
    sgn = -1.0 if side == "L" else 1.0
    x_ctr = sgn * (C.HEAD_W / 2.0 + 0.5)
    z_ear = C.HEAD_Z_CTR - 1.0

    with BuildPart() as pod:
        with Locations((x_ctr, C.HEAD_Y_CTR - 2.0, z_ear)):
            Cylinder(radius=12.0, height=6.5, rotation=(0, 90, 0))
        with Locations((x_ctr + sgn * 2.8, C.HEAD_Y_CTR - 2.0, z_ear)):
            Cylinder(radius=8.8, height=2.0, rotation=(0, 90, 0))
        with Locations(Location((x_ctr + sgn * 3.8, C.HEAD_Y_CTR - 2.0, z_ear), (35, 0, 0))):
            Box(2.2, 13.0, 2.0, mode=Mode.SUBTRACT)
        # Recessed coaxial M3 bolt bore locking Ear Hub -> B04 Shell -> A06 Core Brass Insert!
        with Locations((x_ctr, C.HEAD_Y_CTR - 2.0, z_ear)):
            Cylinder(radius=C.M3_CLEAR_DIA / 2.0, height=12.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
        with Locations((x_ctr + sgn * 2.4, C.HEAD_Y_CTR - 2.0, z_ear)):
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
