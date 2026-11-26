"""
KRON-01V5 (Terra-Rover 4WD Edition) — Master Parametric Configuration (units: mm)
=================================================================================
Inspired by sleek cyber-rover industrial design:
  - Wide-stance 4WD (4× Ø42mm chunky off-road tires + 4× GA12-N20, 60mm wheelbase, 122mm stance)
  - Sculpted sloped aerodynamic two-tone Pearl-White + Gunmetal Titanium rover body
  - Clamshell Easy-Assembly Lift-Off Top Hood (100% seamless closed exterior, open-hood assembly)
  - Wide-sleek Astronaut Helmet (86 × 66 × 58 mm) with edge-to-edge glossy pitch-black curved visor
    and flush visor-integrated OV5647 160° camera lens (zero clunky forehead protrusion!)
  - Dead-center 18650 battery (50/50 CG) + Raspberry Pi Zero 2W + IP5328P 5V/3A
"""

# ---------------------------------------------------------------------------
# FDM 3D Printing Tolerances (0.4mm nozzle, 0.2mm layer height)
# ---------------------------------------------------------------------------
FDM_CLEARANCE = 0.25
FDM_TIGHT = 0.15
WALL = 2.5
HEATSET_M3_DIA = 4.0
HEATSET_M3_DEPTH = 5.2
M3_CLEAR_DIA = 3.3
M25_PILOT_DIA = 2.2
M2_PILOT_DIA = 1.85

# ---------------------------------------------------------------------------
# Wide-Stance 4WD Drivetrain & Ground Contact (4× Ø42mm Off-Road Wheels)
# ---------------------------------------------------------------------------
WHEEL_OD = 42.0             # Chunky 42mm rugged off-road rubber tires
WHEEL_R = WHEEL_OD / 2.0    # 21.0 mm -> Axle at Z = 21.0 mm (ground Z_min = 0.00!)
WHEEL_W = 17.0              # Wide athletic 17mm tires
WHEEL_HUB_OD = 30.0         # Deep concave 6-spoke star alloy-style hub
Z_AXLE = WHEEL_R            # 21.0 mm
Y_AXLE_F = 30.0             # Front axle (+30mm)
Y_AXLE_R = -30.0            # Rear axle (-30mm) -> 60mm stable rover wheelbase!
X_WHEEL = 50.5              # Inner tire ±42mm (2mm clean gap to ±40mm tub), standard 10mm N20 shaft engages 8.5mm deep!

# ---------------------------------------------------------------------------
# Sculpted Aerodynamic Clamshell Rover Chassis (100% Closed Exterior)
# ---------------------------------------------------------------------------
CHASSIS_W = 80.0            # X: -40.0 to +40.0 (inner width 75.0 -> fits 74.5mm 18650 holder)
CHASSIS_L = 104.0           # Y: -50.0 to +54.0 (sloped aerodynamic front nose + fastback rear!)
CHASSIS_Y_CTR = 2.0
CHASSIS_Y_MIN = -50.0
CHASSIS_Y_MAX = 54.0
CHASSIS_Z_BOT = 15.0        # 15.0mm off-road belly clearance
CHASSIS_FLOOR_T = 2.5
CHASSIS_Z_FLOOR = CHASSIS_Z_BOT + CHASSIS_FLOOR_T  # 17.5 mm
CHASSIS_SPLIT_Z = 48.5      # Clamshell parting seam (with 2.5mm alignment step-lip + front catch tab!)
CHASSIS_Z_TOP = 55.0        # Rear/mid crown height (front nose slopes smoothly down to Z=38mm!)

# ---------------------------------------------------------------------------
# COTS Hardware Real-World Positions & Dimensions (Datasheet-Verified)
# ---------------------------------------------------------------------------
# 1. 4x N20 Micro Metal Gear Motors (FL, FR at Y=+30; RL, RR at Y=-30; Z=21)
N20_BODY_L = 24.5
N20_GEAR_L = 9.5
N20_W = 10.0
N20_H = 12.0
N20_SHAFT_D = 3.0
N20_SHAFT_FLAT = 2.5
N20_SHAFT_L = 10.0          # Official standard off-the-shelf 10mm D-shaft (engages 8.5mm inside hub collar!)
N20_OUTER_X = CHASSIS_W / 2.0  # 40.0 mm

# 2. Single 18650 High-Drain (3000mAh 10A) Battery Holder + Cell — DEAD CENTER (50/50 CG!)
BAT_HOLDER_L = 74.5
BAT_HOLDER_W = 21.0
BAT_HOLDER_H = 19.5
BAT_Y = 0.0                 # Y: -10.5 to +10.5 -> 14.5mm clear from front & rear N20 (±25mm)!
BAT_Z_BOT = CHASSIS_Z_FLOOR # 17.5 -> top at 37.5mm

# 3. DRV8833 Dual H-Bridge (Front Center between FL & FR motors)
DRV_W = 18.5
DRV_L = 16.0
DRV_X = 0.0
DRV_Y = 30.0                # Y: +22..+38 -> 11.5mm clear from battery (+10.5)!
DRV_Z = CHASSIS_Z_FLOOR + 2.0

# 4. MAX98357A I2S Class-D Audio Amp (Rear Center between RL & RR motors)
AMP_W = 19.0
AMP_L = 18.0
AMP_X = 0.0
AMP_Y = -30.0               # Y: -39..-21 -> 10.5mm clear from battery (-10.5)!
AMP_Z = CHASSIS_Z_FLOOR + 2.0

# 5. Raspberry Pi Zero 2W (Official 30.0 x 65.0 x 1.6mm, holes 23.0 x 58.0mm)
RPI_W = 30.0
RPI_L = 65.0
RPI_PCB_T = 1.6
RPI_HOLE_X = 23.0
RPI_HOLE_Y = 58.0
RPI_X_CTR = -3.0            # X: -18.0..+12.0
RPI_Y_CTR = -14.0           # Y: -46.5..+18.5 (Micro-SD flush at rear wall -50 -> tool-free swap!)
RPI_Z_PCB = 41.0            # 3.5mm clear above 18650 battery top (37.5mm)!

# 6. IP5328P / SW6106 5V 3A Type-C Power Board (18.0 x 30.0mm)
PWR_W = 18.0
PWR_L = 30.0
PWR_X = 23.0                # X: +14.0..+32.0 -> 2.0mm clear of Pi Zero 2W & clear of rear corner/boss
PWR_Y = -31.0               # Rear USB-C port flush inside rear wall Y = -47.0
PWR_Z = 39.5                # Top at 45.3mm -> 0.7mm clear below A02 step-lip (46.0mm)

# 7. SS12D00G3 Slide Power Switch
SW_X = -24.5                # X: -28.8..-20.2 -> clear of rear-left M3 boss (-29.3) & Pi Zero 2W (-18.0)
SW_Y = -44.8                # Body cleanly inside rear wall (-47.0), knob protrudes through rear cutout
SW_Z = 43.0

# ---------------------------------------------------------------------------
# Low-Profile Sculpted Neck Turret & Head Tilt Mechanism (-20°..+22° Collision-Free!)
# ---------------------------------------------------------------------------
NECK_W = 48.0
NECK_Y_CTR = -8.1
NECK_D = 36.2               # Upper yoke Y: -26.2..+10.0; lower stalk slimmed to 36x22mm for full tilt!
HEAD_PIVOT_Y = -2.0
HEAD_PIVOT_Z = 73.0         # Verified full -20°..+22° pitch clears sloped hood, cowl & white wings!

MG90S_L = 22.6
MG90S_W = 12.1
MG90S_H = 22.5
MG90S_FLANGE_L = 32.5
MG90S_SHAFT_OFFSET = 5.4

# ---------------------------------------------------------------------------
# Terra-Rover Wide-Sleek Astronaut Helmet Head (88W × 68D × 63H mm)
# ---------------------------------------------------------------------------
HEAD_W = 88.0               # Wide athletic 1.40:1 proportion
HEAD_D = 68.0
HEAD_H = 63.0               # Z = 68.0 .. 131.0 mm (Total robot height = 131.0 mm)
HEAD_Y_CTR = -2.0           # Centered right over HEAD_PIVOT_Y for balanced full-range tilt!
HEAD_Z_CTR = 99.5
HEAD_Z_BOT = HEAD_Z_CTR - HEAD_H / 2.0   # 68.0
HEAD_Z_TOP = HEAD_Z_CTR + HEAD_H / 2.0   # 131.0
HEAD_Y_FRONT = HEAD_Y_CTR + HEAD_D / 2.0 # 32.0
HEAD_Y_BACK = HEAD_Y_CTR - HEAD_D / 2.0  # -36.0

# 8. 2.0-inch ST7789V IPS TFT Display (Flush behind Edge-to-Edge Pitch-Black Visor!)
LCD_PCB_W = 61.12
LCD_PCB_H = 36.48
LCD_PCB_T = 1.6
LCD_GLASS_W = 47.8
LCD_GLASS_H = 34.6
LCD_GLASS_T = 2.1
LCD_AA_W = 40.8
LCD_AA_H = 30.6
LCD_Z_CTR = 87.2            # PCB Z: 68.96..105.44, Active Z: 71.9..102.5
LCD_Y_PCB = 17.8            # SPI pins Y_min=11.3 (> MG90S 11.0); eyes Y_max=22.55 (< CAM 22.70)!

# 9. Visor-Integrated OV5647 / IMX219 5MP 160° Wide-Angle CSI Camera
CAM_PCB_W = 25.0
CAM_PCB_H = 24.0
CAM_PCB_T = 1.6
CAM_HOLE_X = 21.0
CAM_HOLE_Z = 12.5
CAM_LENS_DIA = 14.0
CAM_LENS_L = 8.5
CAM_Y_PCB = 24.5            # Rear connector at 22.7 -> clear of LCD eyes (22.55mm)!
CAM_Z_CTR = 111.5           # PCB Z: 99.5..123.5 (inside full-depth visor brow!), Lens right in upper visor bar!

# 10. 28mm 8-Ohm 2W Speaker (Rear crown)
SPK_DIA = 28.0
SPK_H = 5.0
SPK_Y = -10.0               # Y: -24.0..+4.0 -> centered cleanly inside B04 crown!
SPK_Z_TOP = HEAD_Z_TOP - 6.0  # 125.0mm (2.5mm clear below B04 inner roof 127.5mm & 3.85mm below A07 grille!)

# 11. INMP441 I2S MEMS Microphone (Mounted cleanly in chin, clear of neck & LCD!)
MIC_W = 14.0
MIC_H = 14.0
MIC_T = 1.6
MIC_X = 0.0
MIC_Y = 17.5                # Y: +10.5..+24.5 -> clear in front of neck (+10.0) & inside B04 chin!
MIC_Z = 66.8                # Z: 66.0..68.6 -> 0.36mm clear below LCD PCB (68.96mm)!

# ---------------------------------------------------------------------------
# Refined Terra-Rover Consumer Product CMF Palette (RGBA 0..1)
# ---------------------------------------------------------------------------
COLORS = {
    "charcoal":     (0.20, 0.22, 0.26, 1.0),  # Matte Gunmetal Titanium (Plate A)
    "titanium":     (0.32, 0.35, 0.40, 1.0),  # Brushed Titanium Accent
    "white":        (0.93, 0.94, 0.96, 1.0),  # Pearl Tactical White (Plate B)
    "orange":       (0.90, 0.64, 0.20, 1.0),  # Refined Satin Gold-Amber Rim Accent (Plate C)
    "visor_black":  (0.03, 0.04, 0.06, 1.0),  # Glossy Pitch-Black Full-Face Visor
    "rubber":       (0.09, 0.10, 0.11, 1.0),  # Off-Road Matte Black Rubber Tire
    "pcb_dark":     (0.08, 0.14, 0.22, 1.0),
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
    "battery_pink": (0.84, 0.28, 0.48, 1.0),
    "ffc_white":    (0.94, 0.94, 0.96, 1.0),
}
