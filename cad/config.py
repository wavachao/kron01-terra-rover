"""
KRON-01V6 (Terra-Rover 4WD — ESP32-S3-CAM N16R8 Zero-Soldering Edition, v2.0.0)
===============================================================================
Master Parametric Configuration (units: mm)

Hardware Architecture (100% plug-and-play DuPont + unified M3 captive hex nuts):
  - Drivetrain : 4× GA12-N20 (6V, 10mm D-shaft, pre-wired 2P DuPont) +
                 4× Complete Ø43×18mm D-shaft rubber wheels (no printed hubs/rims!)
  - Chassis    : 94×120mm sculpted two-tone Pearl-White + Gunmetal Titanium rover
                 with 5-point mortise-and-tenon lift-off hood + A10 rear dovetail key.
                 Houses Dual-18650 Type-C Power Board (85×44×23mm, dead center 50/50 CG,
                 side waist access window for Type-C / ON-OFF / 4× battery LEDs),
                 2× DRV8833 motor drivers (front & rear centers), and PCA9685A 16-ch PWM!
  - Brain Head : 94×76×67mm wide astronaut helmet housing ESP32-S3-CAM N16R8,
                 OV3660 short-ribbon lens (flush upper visor), GMT020-02 2.0" IPS SPI LCD,
                 3020 cavity speaker, MAX98357A I2S amp, and INMP441 MEMS mic.
                 Only 7 flexible DuPont wires cross the neck!
  - DFM Safety : Forgiving ±0.5–0.8mm/side PCB & module pockets absorb ±0.2–0.5mm SMT/cut
                 batch variance + ±0.15–0.20mm JLC3DP SLA shrinkage. Unified M3 fasteners only!
"""

# ---------------------------------------------------------------------------
# 3D Printing Tolerances (JLC3DP SLA Resin & 0.4mm FDM) — Unified M3 Only!
# ---------------------------------------------------------------------------
SLA_SLIDE_CLEAR = 0.28       # Generous sliding mortise-and-tenon clearance (prevents SLA binding)
PCB_POCKET_CLEAR = 0.70      # +0.70mm per side (+1.4mm total) absorbs ±0.2~0.5mm PCB/SMT variance!
WALL = 2.5

# Unified DIN 934 M3 Captive Hex Nut Pockets (+0.40mm drop-in tolerance, zero heat-set inserts!)
M3_CLEAR_DIA = 3.5           # Generous M3 clearance bore (3.0 + 0.50mm)
NUT_M3_AF = 5.9              # M3 DIN 934 hex nut across flats (5.5 + 0.40mm)
NUT_M3_T = 2.8               # M3 DIN 934 hex nut thickness (2.4 + 0.40mm)

# Mortise-and-tenon hood slide-lock travel
HOOD_SLIDE_TRAVEL = 5.0      # A02 drops at ΔY=-5mm, slides +5mm forward to lock 5 tenons!

# ---------------------------------------------------------------------------
# Wide-Stance 4WD Drivetrain & Ground Contact (4× Complete Ø43×18mm Wheels)
# ---------------------------------------------------------------------------
WHEEL_OD = 43.0              # Complete off-the-shelf 43mm N20 D-shaft rubber tire + rim
WHEEL_R = WHEEL_OD / 2.0     # 21.5 mm -> Axle at Z = 21.5 mm (ground Z_min = 0.00!)
WHEEL_W = 18.0               # Wide 18mm rubber tire
Z_AXLE = WHEEL_R             # 21.5 mm
Y_AXLE_F = 38.0              # Front axle (+38mm)
Y_AXLE_R = -38.0             # Rear axle (-38mm) -> 76mm rock-solid wheelbase!
X_WHEEL = 57.5               # Inner tire ±48.5mm (1.5mm clean gap outside ±47mm tub; 8.5mm D-shaft grip!)

# ---------------------------------------------------------------------------
# Sculpted Aerodynamic Clamshell Rover Chassis (94W × 120L mm)
# ---------------------------------------------------------------------------
CHASSIS_W = 94.0             # X: -47.0 to +47.0 (inner width 89.0 -> fits 85mm Dual-18650 w/ +2mm/side!)
CHASSIS_L = 120.0            # Y: -58.0 to +62.0 (sloped aerodynamic front nose + fastback rear!)
CHASSIS_Y_CTR = 2.0
CHASSIS_Y_MIN = -58.0
CHASSIS_Y_MAX = 62.0
CHASSIS_Z_BOT = 15.0         # 15.0mm off-road belly clearance
CHASSIS_FLOOR_T = 2.5
CHASSIS_Z_FLOOR = CHASSIS_Z_BOT + CHASSIS_FLOOR_T  # 17.5 mm
CHASSIS_SPLIT_Z = 66.0       # Spacious internal height -> clears Dual-18650 & PCA9685A + 14mm DuPont plugs!
CHASSIS_Z_TOP = 72.5         # Crown height (roof ceiling at Z=70.0 -> 2.5mm solid roof!)

# ---------------------------------------------------------------------------
# COTS Hardware Real-World Positions & Dimensions (Verified from User Photos)
# ---------------------------------------------------------------------------
# 1. 4× GA12-N20 Pre-Wired Metal Gear Motors (FL/FR at Y=+38; RL/RR at Y=-38; Z=21.5)
N20_BODY_L = 24.5
N20_GEAR_L = 9.5
N20_W = 10.0
N20_H = 12.0
N20_SHAFT_D = 3.0
N20_SHAFT_FLAT = 2.5
N20_SHAFT_L = 10.0           # Standard 10mm D-shaft (engages 8.5mm inside 43mm wheel!)
N20_OUTER_X = CHASSIS_W / 2.0  # 47.0 mm

# 2. Dual-18650 Parallel Type-C Power Board (85.0 × 44.0 × 23.0 mm) — DEAD CENTER (50/50 CG!)
#    Right (+X) short edge carries Type-C VIN, ON/OFF slide switch, and 4× battery LEDs (25..100%)
PWR_L = 85.0                 # Along X (X = -42.0 .. +43.0 when PWR_X = +0.5)
PWR_W = 44.0                 # Along Y (Y = -22.0 .. +22.0)
PWR_H = 23.0                 # Bottom holder to top PCB surface (Z = 17.5 .. 40.5; headers to 49.0)
PWR_X = 0.5                  # Slightly right so Type-C & switch sit 1.5mm behind right waist window!
PWR_Y = 0.0                  # Dead center between Y_AXLE_F (+38) and Y_AXLE_R (-38)!
PWR_Z = CHASSIS_Z_FLOOR      # 17.5 mm

# 3. 2× DRV8833 Red Motor Drivers (21.0 × 18.0 mm each, pre-soldered headers — 1-to-1 N20 plugs!)
DRV_W = 21.0
DRV_L = 18.0
DRV_F_X = 0.0
DRV_F_Y = Y_AXLE_F           # Front center (+38.0) between FL & FR motors
DRV_R_X = 0.0
DRV_R_Y = Y_AXLE_R           # Rear center (-38.0) between RL & RR motors
DRV_Z = CHASSIS_Z_FLOOR + 2.0  # 19.5 mm (sits on 2mm standoffs inside forgiving 22.6×19.6mm pocket!)

# 4. PCA9685A 16-Channel I2C PWM Driver (Blue Board, 62.0 × 25.0 × ~15mm)
PCA_L = 62.0                 # Along X (X = -31.0 .. +31.0)
PCA_W = 25.0                 # Along Y (Y = -49.0 .. -24.0)
PCA_PCB_T = 1.6
PCA_X = 0.0
PCA_Y = -36.5                # Rear upper shelf above DRV8833 #2 (2.0mm clear of Dual-18650 & 1.5mm clear of A10!)
PCA_Z = 44.0                 # 24.5mm above DRV8833 #2 PCB (clears DuPont plugs) & 26.0mm below A02 ceiling!

# ---------------------------------------------------------------------------
# Low-Profile Sculpted Neck Turret & Head Tilt Mechanism (-20°..+22° Collision-Free!)
# ---------------------------------------------------------------------------
NECK_W = 48.0
NECK_Y_CTR = -8.1
NECK_D = 36.2                # Upper yoke Y: -26.2..+10.0; slim lower stalk 36×22mm for full tilt!
HEAD_PIVOT_Y = -2.0
HEAD_PIVOT_Z = 92.5          # Verified -20°..+22° pitch clears hood, fastback cowl & white wings!

MG90S_L = 22.6
MG90S_W = 12.1
MG90S_H = 22.5
MG90S_FLANGE_L = 32.5
MG90S_SHAFT_OFFSET = 5.4

# ---------------------------------------------------------------------------
# Wide-Sleek Astronaut Helmet Brain Head (94W × 76D × 67H mm)
# ---------------------------------------------------------------------------
HEAD_W = 94.0                # Spacious helmet width fits 64mm ESP32-S3-CAM + 62mm LCD transversely!
HEAD_D = 76.0
HEAD_H = 67.0                # Z = 87.0 .. 154.0 mm (Total robot height = 154.0 mm)
HEAD_Y_CTR = -2.0            # Centered right over HEAD_PIVOT_Y for balanced tilt!
HEAD_Z_CTR = 120.5
HEAD_Z_BOT = HEAD_Z_CTR - HEAD_H / 2.0   # 87.0
HEAD_Z_TOP = HEAD_Z_CTR + HEAD_H / 2.0   # 154.0
HEAD_Y_FRONT = HEAD_Y_CTR + HEAD_D / 2.0 # 36.0
HEAD_Y_BACK = HEAD_Y_CTR - HEAD_D / 2.0  # -40.0

# 5. GMT020-02 2.0" IPS SPI Display (62.0 × 37.5 × 3.4 mm, active area 40.8 × 30.6 mm)
#    Forgiving 63.4 × 38.9 mm perimeter cradle (+0.7mm/side, ZERO rigid M2 screw holes!)
LCD_PCB_W = 62.0
LCD_PCB_H = 37.5
LCD_PCB_T = 1.6
LCD_GLASS_W = 47.8
LCD_GLASS_H = 34.6
LCD_GLASS_T = 2.0
LCD_AA_W = 40.8
LCD_AA_H = 30.6
LCD_Z_CTR = 112.75           # PCB Z: 94.0..131.5 (clears chin mic below & OV3660 lens above!)
LCD_Y_PCB = 21.5             # PCB Y: 21.5..23.1, Glass Y: 23.1..25.1, Eyes Y: 25.1..25.6

# 6. OV3660 Short-Ribbon Camera Sensor (8.5 × 8.5 × 6.0 mm lens head, ~20mm FPC to S3-CAM)
CAM_BODY_W = 8.5
CAM_BODY_H = 8.5
CAM_BODY_L = 6.0
CAM_LENS_DIA = 7.4
CAM_Y_PCB = 26.8             # Rear of OV3660 module at 26.8 -> front glass at 32.8 (flush w/ visor!)
CAM_Z_CTR = 138.25           # Z: 134.0..142.5 -> 2.5mm clear above LCD PCB (131.5)!

# 7. ESP32-S3-CAM N16R8 Main Controller (58.0 × 27.94 mm PCB + 6.04 mm antenna = 64.04 mm total)
#    Mounted horizontally behind LCD/Camera in forgiving 66.0 × 29.4 mm U-cradle (pins pointing DOWN!)
S3_PCB_L = 58.0
S3_ANT_L = 6.04
S3_TOTAL_L = S3_PCB_L + S3_ANT_L  # 64.04 mm along X
S3_PCB_W = 27.94             # Along Y
S3_PCB_T = 1.6
S3_X_CTR = 0.0               # X = -32.02 .. +32.02 (fits inside 69.6mm core cavity w/ +2mm/side!)
S3_Y_CTR = 0.0               # Y = -13.97 .. +13.97 (1.03mm clear behind LCD pins 15.0 & 15.2mm to OV3660!)
S3_Z_PCB = 128.5             # Downward pins to 120.0 (DuPont to 112.0 > 99.0 neck); top shield 134.0 (< 141.0 spk)!

# 8. 3020 Cavity Speaker (30.0 × 20.0 × 7.0 mm, 8Ω 2W) — Rear Crown under A07 Grille
SPK_L = 30.0                 # Along X
SPK_W = 20.0                 # Along Y
SPK_H = 7.0                  # Along Z
SPK_Y = -13.0                # Y: -23.0..-3.0 -> centered cleanly inside B04 crown!
SPK_Z_TOP = HEAD_Z_TOP - 6.0 # 148.0 mm (Z = 141.0..148.0 -> 7.0mm clear above S3-CAM top 134.0!)

# 9. MAX98357A Purple I2S Class-D Amp (19.0 × 18.0 mm) — Vertical Rear Inner Wall of Head!
AMP_W = 19.0                 # Along X
AMP_H = 18.0                 # Along Z
AMP_X = 0.0
AMP_Y = -23.5                # PCB back at -23.5, green terminal reaches -15.4 (1.43mm clear of S3-CAM -13.97!)
AMP_Z = 121.0                # Z: 112.0..130.0 (fuses solidly above 109.5mm pitch-up arch & 11mm below speaker!)

# 10. INMP441 I2S MEMS Microphone (Ø14.0 mm × 1.6 mm circular PCB) — Front Chin Cavity!
MIC_DIA = 14.0
MIC_T = 1.6
MIC_X = 0.0
MIC_Y = 18.0                 # Y: +11.0..+25.0 -> clear in front of neck (+10.0) & inside chin!
MIC_Z = 90.8                 # Z: 90.0..92.6 -> 1.4mm clear below LCD PCB (94.0) & inside B04 (>87.0)!

# ---------------------------------------------------------------------------
# Refined Two-Tone Terra-Rover Consumer Product CMF Palette (RGBA 0..1)
# ---------------------------------------------------------------------------
COLORS = {
    "charcoal":     (0.20, 0.22, 0.26, 1.0),  # Matte Gunmetal Titanium (Plate A)
    "titanium":     (0.32, 0.35, 0.40, 1.0),  # Brushed Titanium Accent
    "white":        (0.93, 0.94, 0.96, 1.0),  # Pearl Tactical White (Plate B)
    "visor_black":  (0.03, 0.04, 0.06, 1.0),  # Glossy Pitch-Black Full-Face Visor
    "rubber":       (0.09, 0.10, 0.11, 1.0),  # Off-Road Matte Black Rubber Tire
    "wheel_hub":    (0.88, 0.89, 0.91, 1.0),  # Complete 43mm Wheel Bright Alloy/White Rim
    "pcb_dark":     (0.08, 0.14, 0.22, 1.0),
    "pcb_blue":     (0.07, 0.32, 0.68, 1.0),
    "pcb_green":    (0.07, 0.44, 0.20, 1.0),
    "pcb_purple":   (0.36, 0.13, 0.48, 1.0),
    "pcb_red":      (0.65, 0.12, 0.14, 1.0),
    "metal_silver": (0.76, 0.79, 0.83, 1.0),
    "brass":        (0.85, 0.67, 0.25, 1.0),
    "gold":         (0.94, 0.77, 0.20, 1.0),
    "black_oxide":  (0.11, 0.11, 0.13, 1.0),
    "screen_glass": (0.02, 0.04, 0.07, 1.0),
    "lens_glass":   (0.08, 0.22, 0.48, 1.0),
    "cyan_glow":    (0.08, 0.94, 1.00, 1.0),
    "servo_blue":   (0.12, 0.38, 0.78, 1.0),
    "battery_green":(0.18, 0.62, 0.34, 1.0),  # EVE 18650-2500mAh Green Power Cells!
    "fpc_copper":   (0.84, 0.44, 0.12, 1.0),
}
