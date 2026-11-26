"""
KRON-01 External Hardware STEP Importer Helper
==============================================
Usage:
    python import_external_step.py <part_key> <path_to_vendor.step>

Example:
    python import_external_step.py esp32_s3_devkitc1 ~/Downloads/ESP32-S3-DevKitC-1.step

Supported part_key values:
    esp32_s3_devkitc1, st7789_2inch_lcd, n20_motor_L, n20_motor_R,
    mg90s_servo, battery_18650, drv8833_driver, max98357a_amp,
    mh_cd42_power, power_switch, speaker_28mm, inmp441_mic,
    cy12a_caster, rubber_tire_L, rubber_tire_R
"""

import shutil
import subprocess
import sys
from pathlib import Path

VALID_KEYS = [
    "esp32_s3_devkitc1",
    "st7789_2inch_lcd",
    "n20_motor_L",
    "n20_motor_R",
    "mg90s_servo",
    "battery_18650",
    "drv8833_driver",
    "max98357a_amp",
    "mh_cd42_power",
    "power_switch",
    "speaker_28mm",
    "inmp441_mic",
    "cy12a_caster",
    "rubber_tire_L",
    "rubber_tire_R",
]

ROOT = Path(__file__).parent
EXT_DIR = ROOT / "external_step"


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in VALID_KEYS:
        print(__doc__)
        sys.exit(1)

    part_key, src_path = sys.argv[1], Path(sys.argv[2]).expanduser().resolve()
    if not src_path.exists():
        print(f"Error: file not found: {src_path}")
        sys.exit(1)

    EXT_DIR.mkdir(parents=True, exist_ok=True)
    dst = EXT_DIR / f"{part_key}.step"
    shutil.copy2(src_path, dst)
    print(f"Imported vendor STEP -> {dst}")
    print("Rebuilding KRON-01 full assembly & running clearance check...")
    subprocess.run([sys.executable, str(ROOT / "build_all.py")], check=True)


if __name__ == "__main__":
    main()
