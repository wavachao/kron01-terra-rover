"""
KRON-01V4 (4WD Rounded Vision Edition) — Master CAD Assembly Builder, Verifier, Exporter & Renderer
====================================================================================================
Builds the complete KRON-01V4 4WD AI Companion Robot from parametric B-Rep solids
(Clamshell Easy-Assembly Rounded Chassis + 4x Ø40mm Wheels + RPi Zero 2W + OV5647 CSI Camera),
runs automated COTS clearance & mass checks, exports STEP / STL / 3MF deliverables
grouped by single-color FDM print plates, and renders crisp multi-view engineering figures.
"""

import json
import math
from pathlib import Path

import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build123d import (
    Compound,
    Location,
    export_step,
    export_stl,
    Mesher,
)

import config as C
from cots_hardware import build_all_cots
from printed_chassis import build_all_chassis_parts
from printed_head import build_all_head_parts

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
EXPORT_DIR = REPO_ROOT / "export"
DOCS_IMG_DIR = REPO_ROOT / "docs" / "images"

# Explode direction vectors (dx, dy, dz) in mm — showcases Terra-Rover Clamshell Open-Hood Assembly!
EXPLODE_VECTORS = {
    "A01_chassis_tub":    (0, 0, 0),
    "A02_top_hood":       (0, 0, 26),
    "A10_hood_lock_key":  (0, -14, 42),
    "A03_motor_clamp_F":  (0, 10, 12),
    "A03_motor_clamp_R":  (0, -10, 12),
    "B01_hood_wing_L":    (-16, 8, 34),
    "B01_hood_wing_R":    (16, 8, 34),
    "B02_side_fairing_L": (-24, 0, 8),
    "B03_side_fairing_R": (24, 0, 8),
    "A04_wheel_hub_FL":   (-30, 10, 0),
    "A04_wheel_hub_FR":   (30, 10, 0),
    "A04_wheel_hub_RL":   (-30, -10, 0),
    "A04_wheel_hub_RR":   (30, -10, 0),
    "C03_wheel_rim_FL":   (-42, 10, 0),
    "C03_wheel_rim_FR":   (42, 10, 0),
    "C03_wheel_rim_RL":   (-42, -10, 0),
    "C03_wheel_rim_RR":   (42, -10, 0),
    "A06_head_core":      (0, 0, 42),
    "A07_top_grille":     (0, 0, 70),
    "A08_visor_mask":     (0, 28, 48),
    "A09_ear_hub_L":      (-24, 0, 48),
    "A09_ear_hub_R":      (24, 0, 48),
    "B04_head_shell":     (0, -12, 56),
    # COTS hardware explode vectors
    "cots_rpi_zero2w":    (0, -6, 14),
    "cots_csi_camera":    (0, 22, 54),
    "cots_st7789_lcd":    (0, 14, 44),
    "cots_n20_FL":        (-12, 6, -4),
    "cots_n20_FR":        (12, 6, -4),
    "cots_n20_RL":        (-12, -6, -4),
    "cots_n20_RR":        (12, -6, -4),
    "cots_mg90s_servo":   (-12, 0, 28),
    "cots_18650_battery": (0, 0, 6),
    "cots_drv8833":       (0, 10, 4),
    "cots_max98357a":     (0, -10, 4),
    "cots_ip5328p_power": (14, -12, 12),
    "cots_power_switch":  (-14, -18, 10),
    "cots_speaker_28mm":  (0, -6, 64),
    "cots_inmp441_mic":   (0, 14, 36),
    "cots_tire_FL":       (-36, 10, 0),
    "cots_tire_FR":       (36, 10, 0),
    "cots_tire_RL":       (-36, -10, 0),
    "cots_tire_RR":       (36, -10, 0),
    "cots_wiring":        (0, 0, 0),
    "cots_fasteners":     (0, 0, 0),
}


def shape_to_trimesh(shape, tolerance: float = 0.25) -> trimesh.Trimesh:
    """Tessellate a build123d Shape/Part/Compound into a single Trimesh."""
    tmp_stl = ROOT / "_tmp_mesh.stl"
    export_stl(shape, str(tmp_stl), tolerance=tolerance, angular_tolerance=0.25)
    mesh = trimesh.load(str(tmp_stl), force="mesh")
    tmp_stl.unlink(missing_ok=True)
    return mesh


def extract_colored_submeshes(
    name: str, shape, category: str, tolerance: float = 0.55, parent_loc: Location | None = None
):
    """Extract sub-meshes with exact global transforms & per-body colors for WebGL & Matplotlib."""
    if parent_loc is None:
        parent_loc = Location()
    submeshes = []
    if hasattr(shape, "children") and shape.children:
        child_parent_loc = parent_loc * shape.location
        for ch in shape.children:
            submeshes.extend(
                extract_colored_submeshes(name, ch, category, tolerance, child_parent_loc)
            )
        return submeshes

    col = getattr(shape, "color", None)
    if col is not None:
        tup = tuple(col)
        rgba = [round(float(tup[0]), 3), round(float(tup[1]), 3), round(float(tup[2]), 3), 1.0]
    else:
        rgba = [0.6, 0.65, 0.7, 1.0]

    located = parent_loc * shape
    mesh = shape_to_trimesh(located, tolerance=tolerance)
    if len(mesh.faces) == 0:
        return []
    submeshes.append({
        "part": name,
        "label": getattr(shape, "label", name) or name,
        "category": category,
        "color": rgba,
        "mesh": mesh,
    })
    return submeshes


def check_cots_clearances(cots_dict: dict):
    """Run automated AABB clearance checks across all critical KRON-01V4 4WD COTS hardware pairs."""
    critical_pairs = [
        ("cots_rpi_zero2w", "cots_18650_battery"),
        ("cots_rpi_zero2w", "cots_n20_FL"),
        ("cots_rpi_zero2w", "cots_n20_FR"),
        ("cots_rpi_zero2w", "cots_n20_RL"),
        ("cots_rpi_zero2w", "cots_n20_RR"),
        ("cots_rpi_zero2w", "cots_mg90s_servo"),
        ("cots_rpi_zero2w", "cots_drv8833"),
        ("cots_rpi_zero2w", "cots_max98357a"),
        ("cots_rpi_zero2w", "cots_ip5328p_power"),
        ("cots_rpi_zero2w", "cots_power_switch"),
        ("cots_18650_battery", "cots_n20_FL"),
        ("cots_18650_battery", "cots_n20_FR"),
        ("cots_18650_battery", "cots_n20_RL"),
        ("cots_18650_battery", "cots_n20_RR"),
        ("cots_18650_battery", "cots_drv8833"),
        ("cots_18650_battery", "cots_max98357a"),
        ("cots_drv8833", "cots_n20_FL"),
        ("cots_drv8833", "cots_n20_FR"),
        ("cots_max98357a", "cots_n20_RL"),
        ("cots_max98357a", "cots_n20_RR"),
        ("cots_csi_camera", "cots_st7789_lcd"),
        ("cots_csi_camera", "cots_speaker_28mm"),
        ("cots_csi_camera", "cots_mg90s_servo"),
        ("cots_st7789_lcd", "cots_speaker_28mm"),
        ("cots_st7789_lcd", "cots_inmp441_mic"),
        ("cots_st7789_lcd", "cots_mg90s_servo"),
    ]
    report = []
    all_clear = True
    for a, b in critical_pairs:
        bb_a = cots_dict[a].bounding_box()
        bb_b = cots_dict[b].bounding_box()
        dx = max(0.0, max(bb_a.min.X - bb_b.max.X, bb_b.min.X - bb_a.max.X))
        dy = max(0.0, max(bb_a.min.Y - bb_b.max.Y, bb_b.min.Y - bb_a.max.Y))
        dz = max(0.0, max(bb_a.min.Z - bb_b.max.Z, bb_b.min.Z - bb_a.max.Z))
        gap = math.sqrt(dx * dx + dy * dy + dz * dz)
        overlap = (dx == 0.0 and dy == 0.0 and dz == 0.0)
        if overlap:
            all_clear = False
        report.append({
            "pair": f"{a} <-> {b}",
            "min_gap_mm": round(gap, 2),
            "status": "COLLISION" if overlap else "PASS",
        })
    return all_clear, report


def render_engineering_views(all_submeshes: list, out_path: Path, dims_str: str):
    """Render a crisp 2x2 shaded CAD engineering sheet from front-hero, x-ray, rear I/O, and clamshell exploded views."""
    fig = plt.figure(figsize=(16, 12), facecolor="#0d1117")
    views = [
        ("1. FRONT 3/4 HERO — 4WD ROUNDED CLOSED SHELL", 18, 52, False, 0.0),
        ("2. X-RAY INTERNAL 4x N20 + RPi ZERO 2W + 18650", 20, 42, True, 0.0),
        ("3. REAR 3/4 CLOSED HULL (SD + 5V/3A TYPE-C + SW)", 18, -132, False, 0.0),
        ("4. CLAMSHELL EXPLODED VIEW (LIFT-OFF TOP LID)", 22, 50, False, 0.85),
    ]
    light_dir = np.array([0.45, 0.65, 0.61])
    light_dir = light_dir / np.linalg.norm(light_dir)

    for idx, (title, elev, azim, xray, explode) in enumerate(views, start=1):
        ax = fig.add_subplot(2, 2, idx, projection="3d", facecolor="#131820")
        ax.set_title(title, color="#e6edf3", fontsize=11.5, fontweight="bold", pad=10)

        all_tris = []
        all_fcolors = []
        all_ecolors = []
        for sm in all_submeshes:
            is_shell = sm["category"].startswith("plate_")
            alpha = 0.14 if (xray and is_shell) else 0.99
            ex, ey, ez = EXPLODE_VECTORS.get(sm["part"], (0, 0, 0))
            offset = np.array([ex * explode, ey * explode, ez * explode])

            verts = sm["mesh"].vertices + offset
            faces = sm["mesh"].faces
            tris = verts[faces]

            v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
            normals = np.cross(v1 - v0, v2 - v0)
            norms = np.linalg.norm(normals, axis=1, keepdims=True) + 1e-9
            normals = normals / norms
            intensity = np.clip(0.42 + 0.58 * np.abs(normals @ light_dir), 0.28, 1.0)

            r, g, b, _ = sm["color"]
            fcolors = np.zeros((len(tris), 4))
            fcolors[:, 0] = np.clip(r * intensity, 0, 1)
            fcolors[:, 1] = np.clip(g * intensity, 0, 1)
            fcolors[:, 2] = np.clip(b * intensity, 0, 1)
            fcolors[:, 3] = alpha

            ecol = np.tile([0.05, 0.07, 0.10, 0.03 if (xray and is_shell) else 0.06], (len(tris), 1))
            all_tris.append(tris)
            all_fcolors.append(fcolors)
            all_ecolors.append(ecol)

        merged_tris = np.concatenate(all_tris, axis=0)
        merged_fc = np.concatenate(all_fcolors, axis=0)
        merged_ec = np.concatenate(all_ecolors, axis=0)
        poly = Poly3DCollection(
            merged_tris,
            facecolors=merged_fc,
            edgecolors=merged_ec,
            linewidths=0.14,
            zsort="average",
        )
        ax.add_collection3d(poly)

        lim = 104 if explode > 0 else 78
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_zlim(-10 if explode > 0 else 0, 210 if explode > 0 else 155)
        ax.set_box_aspect([1, 1, 0.95])
        ax.view_init(elev=elev, azim=azim)
        ax.tick_params(colors="#6e7681", labelsize=8)
        for p in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
            p.fill = False
            p.set_edgecolor("#21262d")
        ax.set_xlabel("X Right (mm)", color="#8b949e", fontsize=8)
        ax.set_ylabel("Y Front (mm)", color="#8b949e", fontsize=8)
        ax.set_zlabel("Z Up (mm)", color="#8b949e", fontsize=8)

    fig.suptitle(
        f"KRON-01V5 Terra-Rover 4WD Edition (Sculpted Astronaut Visor + Clamshell Open-Hood + 4× N20) — {dims_str}",
        color="#ffffff",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(str(out_path), dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)


def export_webgl_json(all_submeshes: list, out_path: Path):
    """Export compact smooth-shaded CAD mesh bundle with lid/head/wheel tags for 60fps WebGL digital twin."""
    items = []
    for sm in all_submeshes:
        mesh = sm["mesh"]
        verts = np.round(mesh.vertices, 2)
        faces = mesh.faces
        part = sm["part"]
        label = sm["label"]
        # Keep hero curved shells smooth & high-res; keep tiny internal fasteners light
        max_faces = 1400 if part in ("B04_head_shell", "A08_visor_mask", "A02_top_hood", "A01_chassis_tub") else (700 if sm["category"].startswith("plate_") else 320)
        if len(faces) > max_faces:
            grid = 0.65 if len(faces) < 3500 else 1.15
            q = np.round(verts / grid) * grid
            uniq_v, inv = np.unique(q, axis=0, return_inverse=True)
            new_f = inv[faces]
            valid = (new_f[:, 0] != new_f[:, 1]) & (new_f[:, 1] != new_f[:, 2]) & (new_f[:, 0] != new_f[:, 2])
            new_f = new_f[valid]
            if len(new_f) > 20:
                verts, faces = np.round(uniq_v, 2), new_f

        is_head = (
            part.startswith(("A06", "A07", "A08", "A09", "B04"))
            or part in ("cots_st7789_lcd", "cots_csi_camera", "cots_speaker_28mm", "cots_inmp441_mic")
            or ("EarPivot" in label)
        )
        is_lid = (
            is_head
            or part in ("A02_top_hood", "A10_hood_lock_key", "B01_hood_wing_L", "B01_hood_wing_R", "cots_mg90s_servo")
            or ("TopHood" in label and "M3x8" in label)
        )
        wh = ""
        for tag in ("FL", "FR", "RL", "RR"):
            if part.endswith("_" + tag):
                wh = tag
                break
        is_shell = sm["category"].startswith("plate_") and (not wh)
        is_gloss = part == "A08_visor_mask" or "Glass" in label or "Lens" in label
        is_eye = "Eye" in label or "Lens_Glass" in label

        ex, ey, ez = EXPLODE_VECTORS.get(part, (0, 0, 0))
        items.append({
            "p": part,
            "l": label,
            "c": sm["category"],
            "col": [int(sm["color"][0] * 255), int(sm["color"][1] * 255), int(sm["color"][2] * 255)],
            "h": 1 if is_head else 0,
            "lid": 1 if is_lid else 0,
            "sh": 1 if is_shell else 0,
            "wh": wh,
            "gl": 1 if is_gloss else 0,
            "eye": 1 if is_eye else 0,
            "e": [ex, ey, ez],
            "v": verts.flatten().tolist(),
            "f": faces.flatten().tolist(),
        })
    out_path.write_text(json.dumps(items, separators=(",", ":")))
    return out_path.stat().st_size


def main():
    print("=" * 74)
    print("  KRON-01V4 4WD Rounded Vision Edition — Industrial CAD Build Pipeline")
    print("=" * 74)

    for d in [
        EXPORT_DIR / "full_assembly",
        EXPORT_DIR / "cots_step",
        EXPORT_DIR / "stl_plate_A_charcoal",
        EXPORT_DIR / "stl_plate_B_white",
        EXPORT_DIR / "stl_plate_C_orange",
        ROOT / "external_step",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # Clear stale plate files from prior 2WD builds
    for old_dir in (
        EXPORT_DIR / "cots_step",
        EXPORT_DIR / "stl_plate_A_charcoal",
        EXPORT_DIR / "stl_plate_B_white",
        EXPORT_DIR / "stl_plate_C_orange",
    ):
        for f in old_dir.iterdir():
            if f.is_file():
                f.unlink()

    # 1. Build Real COTS Hardware
    print("[1/6] Building datasheet-accurate 4WD COTS hardware library...")
    cots = build_all_cots()
    for key, comp in cots.items():
        export_step(comp, str(EXPORT_DIR / "cots_step" / f"{key}.step"))
    print(f"      -> Built & exported {len(cots)} COTS hardware STEP assemblies.")

    # 2. Build 3D-Printable FDM Chassis & Head Parts
    print("[2/6] Building 3D-printable FDM Clamshell 4WD split-color parts...")
    printed = {}
    printed.update(build_all_chassis_parts())
    printed.update(build_all_head_parts())

    plate_dirs = {
        "plate_A_charcoal": EXPORT_DIR / "stl_plate_A_charcoal",
        "plate_B_white": EXPORT_DIR / "stl_plate_B_white",
        "plate_C_orange": EXPORT_DIR / "stl_plate_C_orange",
    }

    plate_stats = {k: {"count": 0, "vol_cm3": 0.0, "est_mass_g": 0.0} for k in plate_dirs}
    part_manifest = []

    for name, (plate, part) in printed.items():
        solids_n = len(part.solids())
        shells_n = len(part.shells())
        if solids_n != 1 or shells_n != 1:
            raise RuntimeError(
                f"DFM ERROR: {name} must be 1 solid & 1 shell (got solids={solids_n}, shells={shells_n})!"
            )
        pdir = plate_dirs[plate]
        stl_path = pdir / f"{name}.stl"
        step_path = pdir / f"{name}.step"
        export_stl(part, str(stl_path), tolerance=0.05, angular_tolerance=0.1)
        export_step(part, str(step_path))

        vol_cm3 = part.volume / 1000.0
        est_mass_g = vol_cm3 * 1.24 * 0.62
        bb = part.bounding_box()
        plate_stats[plate]["count"] += 1
        plate_stats[plate]["vol_cm3"] += vol_cm3
        plate_stats[plate]["est_mass_g"] += est_mass_g
        part_manifest.append({
            "name": name,
            "plate": plate,
            "size_mm": [round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)],
            "vol_cm3": round(vol_cm3, 2),
            "est_mass_g": round(est_mass_g, 1),
        })

    print(f"      -> Built & exported {len(printed)} printable STL + STEP parts across 3 color plates.")

    # 2b. Export JLC3DP-Ready Single-Body Centered STLs (17 unique STLs -> 23 physical parts)
    jlc_dir = EXPORT_DIR / "jlc3dp_ready"
    jlc_dir.mkdir(parents=True, exist_ok=True)
    jlc_spec = [
        ("A01_chassis_tub",    "01_黑_A01_底盘下盆_x1.stl",       1, "黑色树脂 / 尼龙PA12"),
        ("A02_top_hood",       "02_黑_A02_掀盖顶罩_x1.stl",       1, "黑色树脂 / 尼龙PA12"),
        ("A03_motor_clamp_F",  "03_黑_A03_电机压板_x2.stl",       2, "黑色树脂 / 尼龙PA12"),
        ("A04_wheel_hub_FL",   "04_黑_A04_左轮毂_x2.stl",        2, "黑色树脂 / 尼龙PA12"),
        ("A04_wheel_hub_FR",   "05_黑_A04_右轮毂_x2.stl",        2, "黑色树脂 / 尼龙PA12"),
        ("A06_head_core",      "06_黑_A06_头盔内胆_x1.stl",       1, "黑色树脂 / 尼龙PA12"),
        ("A07_top_grille",     "07_黑_A07_顶置喇叭格栅_x1.stl",    1, "黑色树脂 / 尼龙PA12"),
        ("A08_visor_mask",     "08_黑亮_A08_曲面黑面罩_x1.stl",    1, "高光黑树脂 / 喷亮黑漆"),
        ("A09_ear_hub_L",      "09_黑_A09_左耳罩_x1.stl",        1, "黑色树脂 / 尼龙PA12"),
        ("A09_ear_hub_R",      "10_黑_A09_右耳罩_x1.stl",        1, "黑色树脂 / 尼龙PA12"),
        ("B01_hood_wing_L",    "11_白_B01_左引擎盖白翼_x1.stl",    1, "9000R / 6060 白色树脂"),
        ("B01_hood_wing_R",    "12_白_B01_右引擎盖白翼_x1.stl",    1, "9000R / 6060 白色树脂"),
        ("B02_side_fairing_L", "13_白_B02_左侧白护甲_x1.stl",     1, "9000R / 6060 白色树脂"),
        ("B03_side_fairing_R", "14_白_B03_右侧白护甲_x1.stl",     1, "9000R / 6060 白色树脂"),
        ("B04_head_shell",     "15_白_B04_宇航白头盔壳_x1.stl",    1, "9000R / 6060 白色树脂"),
        ("C03_wheel_rim_FL",   "16_金橙_C03_轮毂细圈_x4.stl",     4, "白色树脂自己喷金/橙漆 或 橙色PLA"),
        ("A10_hood_lock_key",  "17_黑_A10_顶盖燕尾锁销_x1.stl",    1, "黑色树脂 / 尼龙PA12"),
    ]
    manifest_lines = [
        "嘉立创 3D 打印（JLC3DP）一键下单核对清单（共 17 个独立 STL，总计 23 个实物零件）",
        "=" * 78,
    ]
    total_jlc_vol = 0.0
    for key, fname, qty, mat in jlc_spec:
        plate, _ = printed[key]
        src_stl = plate_dirs[plate] / f"{key}.stl"
        m = trimesh.load(str(src_stl), force="mesh")
        b = m.bounds
        cx, cy = (b[0][0] + b[1][0]) / 2.0, (b[0][1] + b[1][1]) / 2.0
        zmin = b[0][2]
        m.apply_translation([-cx, -cy, -zmin])
        m.export(str(jlc_dir / fname))
        sx, sy, sz = m.extents
        vol_cm3 = float(m.volume) / 1000.0
        total_jlc_vol += vol_cm3 * qty
        manifest_lines.append(
            f"{fname:28s} | 数量={qty} | {sx:5.1f}×{sy:5.1f}×{sz:5.1f}mm | 单件={vol_cm3:5.1f}cm³ | 推荐材料: {mat}"
        )
    manifest_lines.append("=" * 78)
    manifest_lines.append(
        f"总打印体积（仅外壳，不含电子件）: {total_jlc_vol:.1f} cm³（全部 17 个 STL 均为单体水密流形，可直接上传嘉立创无需拆分！）"
    )
    (jlc_dir / "嘉立创下单数量与材料对照表.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"      -> Exported 17 JLC3DP-ready centered single-body STLs to {jlc_dir}")

    # 3. Export Full Colored Assemblies (STEP & 3MF!)
    print("[3/6] Exporting Master Assemblies (STEP + 3MF)...")
    printed_comp = Compound(label="KRON01V4_Printed_Shells", children=[p for _, p in printed.values()])
    cots_comp = Compound(label="KRON01V4_COTS_Hardware", children=list(cots.values()))

    export_step(printed_comp, str(EXPORT_DIR / "full_assembly" / "KRON01_Printed_Shells.step"))
    export_step(cots_comp, str(EXPORT_DIR / "full_assembly" / "KRON01_COTS_Hardware.step"))

    full_comp = Compound(label="KRON01V4_Full_Assembly", children=[printed_comp, cots_comp])
    export_step(full_comp, str(EXPORT_DIR / "full_assembly" / "KRON01_Full_Assembly.step"))

    mesher = Mesher()
    for name, (_, part) in printed.items():
        mesher.add_shape(part)
    mesher.write(str(EXPORT_DIR / "full_assembly" / "KRON01_Printed_Assembly.3mf"))

    bb_full = full_comp.bounding_box()
    dims_str = f"{bb_full.size.X:.1f} × {bb_full.size.Y:.1f} × {bb_full.size.Z:.1f} mm"
    print(f"      -> Overall Assembly Dimensions: {dims_str}")
    print(f"      -> Ground Contact Check: Z_min = {bb_full.min.Z:.2f} mm (Target: 0.00 mm)")

    # 4. Automated COTS Clearance Verification
    print("[4/6] Running Automated 4WD COTS Clearance & Collision Check...")
    all_clear, clearance_report = check_cots_clearances(cots)
    for row in clearance_report:
        print(f"      [{row['status']:9s}] {row['pair']:45s} min_gap = {row['min_gap_mm']:5.2f} mm")

    # 5. Tessellate & Render Multi-View Engineering Verification Sheets
    print("[5/6] Rendering CAD Verification Sheets (Assembly + Internals/Wiring)...")
    DOCS_IMG_DIR.mkdir(parents=True, exist_ok=True)
    all_submeshes = []
    for name, (plate, part) in printed.items():
        all_submeshes.extend(extract_colored_submeshes(name, part, plate, tolerance=0.45))
    for name, comp in cots.items():
        cat = "wiring" if name == "cots_wiring" else "cots"
        all_submeshes.extend(extract_colored_submeshes(name, comp, cat, tolerance=0.5))

    views_png = DOCS_IMG_DIR / "kron01_cad_views.png"
    render_engineering_views(all_submeshes, views_png, dims_str)
    print(f"      -> Saved CAD verification views to {views_png}")

    # Dedicated Real Hardware + 4WD + RPi Zero 2W + OV5647 CSI Camera + 3D Wiring Sheet
    hw_only = [sm for sm in all_submeshes if sm["category"] in ("cots", "wiring") or sm["part"] == "A08_visor_mask"]
    fig = plt.figure(figsize=(16, 7.5), facecolor="#0d1117")
    light_dir = np.array([0.45, 0.65, 0.61])
    light_dir = light_dir / np.linalg.norm(light_dir)
    hw_views = [
        ("A. 4WD DRIVETRAIN + FOREHEAD OV5647 CSI CAM + 2.0\" ST7789 (FRONT 3/4)", 20, 48),
        ("B. RASPBERRY PI ZERO 2W + CENTER 18650 (50/50 CG) + 4x N20 WIRING (TOP-REAR 3/4)", 36, -138),
    ]
    for idx, (title, elev, azim) in enumerate(hw_views, start=1):
        ax = fig.add_subplot(1, 2, idx, projection="3d", facecolor="#131820")
        ax.set_title(title, color="#e6edf3", fontsize=11, fontweight="bold", pad=10)
        for sm in hw_only:
            verts = sm["mesh"].vertices
            faces = sm["mesh"].faces
            tris = verts[faces]
            v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
            normals = np.cross(v1 - v0, v2 - v0)
            normals = normals / (np.linalg.norm(normals, axis=1, keepdims=True) + 1e-9)
            intensity = np.clip(0.48 + 0.52 * np.abs(normals @ light_dir), 0.35, 1.0)
            r, g, b, _ = sm["color"]
            fcolors = np.zeros((len(tris), 4))
            fcolors[:, 0] = np.clip(r * intensity, 0, 1)
            fcolors[:, 1] = np.clip(g * intensity, 0, 1)
            fcolors[:, 2] = np.clip(b * intensity, 0, 1)
            fcolors[:, 3] = 0.98
            ax.add_collection3d(Poly3DCollection(tris, facecolors=fcolors, edgecolors=(0, 0, 0, 0.08), linewidths=0.15))
        ax.set_xlim(-64, 64); ax.set_ylim(-56, 56); ax.set_zlim(0, 138)
        ax.set_box_aspect([1.0, 0.90, 1.06])
        ax.view_init(elev=elev, azim=azim)
        ax.tick_params(colors="#6e7681", labelsize=8)
        for p in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
            p.fill = False; p.set_edgecolor("#21262d")
        ax.set_xlabel("X (mm)", color="#8b949e", fontsize=8)
        ax.set_ylabel("Y Front (mm)", color="#8b949e", fontsize=8)
        ax.set_zlabel("Z Up (mm)", color="#8b949e", fontsize=8)
    fig.suptitle(
        "KRON-01V4 4WD Real Hardware (4× N20 + Center 18650 + RPi Zero 2W + OV5647 CSI Cam + MIPI FFC Ribbon)",
        color="#ffffff", fontsize=13, fontweight="bold", y=0.98,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    internals_png = DOCS_IMG_DIR / "kron01_internals_wiring.png"
    plt.savefig(str(internals_png), dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"      -> Saved internals & wiring sheet to {internals_png}")

    # 6. Export Compact WebGL Mesh Bundle & Build Summary JSON
    print("[6/6] Exporting Interactive 3D Viewer Mesh Bundle...")
    webgl_json = EXPORT_DIR / "viewer_meshes.json"
    js_bytes = export_webgl_json(all_submeshes, webgl_json)
    print(f"      -> Exported viewer_meshes.json ({js_bytes / 1024:.1f} KB, {len(all_submeshes)} colored bodies)")

    summary = {
        "edition": "KRON-01V4 (4WD Clamshell Rounded Vision Edition)",
        "overall_mm": {
            "width_X": round(bb_full.size.X, 1),
            "length_Y": round(bb_full.size.Y, 1),
            "height_Z": round(bb_full.size.Z, 1),
            "ground_Z_min": round(bb_full.min.Z, 2),
        },
        "plates": {k: {kk: round(vv, 1) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in plate_stats.items()},
        "total_filament_g": round(sum(v["est_mass_g"] for v in plate_stats.values()), 1),
        "all_cots_clear": all_clear,
        "clearances": clearance_report,
        "parts": part_manifest,
    }
    (EXPORT_DIR / "build_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\n=== BUILD COMPLETE ===")
    print(json.dumps(summary["plates"], indent=2))
    print(f"Total Estimated PLA Filament: {summary['total_filament_g']} g (~¥{summary['total_filament_g'] * 0.06:.1f} filament cost)")


if __name__ == "__main__":
    main()
