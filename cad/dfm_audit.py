"""
KRON-01V5 Automated FDM 3D-Printing DFM (Design for Manufacturing) Mesh Audit
=============================================================================
Checks every single exported STL across Plates A, B, and C for:
  1. Watertightness (manifold solid ready for Bambu Studio / OrcaSlicer / PrusaSlicer)
  2. Positive non-degenerate volume
  3. Build-plate fit (<= 180 x 180 x 180 mm -> prints even on Bambu A1 mini!)
"""

from pathlib import Path
import trimesh

EXPORT = Path(__file__).resolve().parent.parent / "export"
PLATES = ["stl_plate_A_charcoal", "stl_plate_B_white", "stl_plate_C_orange", "jlc3dp_ready"]


def main():
    print("=" * 92)
    print("  KRON-01V5 AUTOMATED 3D-PRINTING DFM AUDIT (WATERTIGHT + SINGLE-BODY + BED FIT)")
    print("=" * 92)
    total = 0
    passed = 0
    for pl in PLATES:
        pdir = EXPORT / pl
        if not pdir.exists():
            continue
        for stl in sorted(pdir.glob("*.stl")):
            total += 1
            m = trimesh.load(str(stl), force="mesh")
            wt = bool(m.is_watertight)
            shells = len(m.split(only_watertight=False))
            vol = float(m.volume) / 1000.0
            sx, sy, sz = m.extents
            fits_a1m = (sx <= 180.0 and sy <= 180.0 and sz <= 180.0)
            ok = wt and shells == 1 and vol > 0.05 and fits_a1m
            if ok:
                passed += 1
            status = "PASS" if ok else "FAIL"
            print(
                f"[{status:4s}] {pl + '/' + stl.name:50s} | {sx:5.1f}×{sy:5.1f}×{sz:5.1f} mm | "
                f"Vol={vol:5.1f} cm³ | WT={str(wt):5s} | Shells={shells} | A1m={fits_a1m}"
            )
    print("-" * 92)
    print(f"DFM SUMMARY: {passed}/{total} STL files PASSED watertight single-body manifold & A1-mini bed check!")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
