"""
KRON-01V6 (ESP32-S3-CAM N16R8 Zero-Soldering Edition, v2.0.0) — System Engineering Simulator
============================================================================================
Verifies before 3D printing & final wiring:
  1. Complete ESP32-S3-CAM N16R8 + PCA9685A + 2× DRV8833 + Dual-18650 1-to-1 DuPont Netlist:
     - ZERO pin sharing, ZERO Y-splices, ZERO breadboard, ZERO soldering!
     - Reserved Camera DVP (GPIO4..13, 15..18), Octal PSRAM (GPIO33..37), Native USB-JTAG (GPIO19..20)
       are strictly protected from external assignments!
     - External I2C (GPIO1 SDA, GPIO2 SCL) -> PCA9685A 16-ch PWM -> MG90S (CH0) + 2× DRV8833 (CH1..CH8)
     - SPI LCD GMT020-02 (GPIO21/47/14/41/42 + 3V3 BLK)
     - Dedicated Hardware I2S1 (GPIO39/40/38) -> INMP441 MEMS Mic
     - Dedicated Hardware I2S0 (GPIO3/43/44) -> MAX98357A Class-D Amp -> 3020 Cavity Speaker
     - Only 7 flexible DuPont wires cross the neck!
  2. Dual-18650 1S2P (5000mAh EVE 12C) Power Margin & Cloud Multimodal AI Runtime Simulation
  3. 4WD Skid-Steer Kinematics (4× Ø43×18mm Wheels), 50/50 CG Stability & MG90S Servo Margin
"""

import json
import math
from pathlib import Path

# Strictly reserved on ESP32-S3-CAM N16R8 (Camera DVP + Octal PSRAM + Native USB-CDC + Strapping)
RESERVED_S3_CAM_GPIOS = {
    0,                          # BOOT button
    4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18,  # Onboard OV3660 DVP + SCCB
    19, 20,                     # Native USB-CDC / JTAG (flashing & console!)
    33, 34, 35, 36, 37,         # Internal Octal PSRAM (R8)
    45, 46,                     # Boot strapping pins
    48,                         # Onboard WS2812 RGB LED
}
VALID_S3_FREE_GPIOS = {1, 2, 3, 14, 21, 38, 39, 40, 41, 42, 43, 44, 47}

NETLIST = [
    # --- 1. Power Distribution (Dual-18650 1S2P Type-C Power Board -> 1-to-1 DuPont Headers!) ---
    {"id": "W01", "bus": "POWER_NECK", "from": "Dual18650.5V_Pin1",     "to": "S3CAM.5V",              "signal": "S3_5V",         "volt": "5.0V", "color": "红 (穿颈1)"},
    {"id": "W02", "bus": "POWER_NECK", "from": "Dual18650.GND_Pin1",    "to": "S3CAM.GND_1",           "signal": "S3_GND",        "volt": "0V",   "color": "黑 (穿颈2)"},
    {"id": "W03", "bus": "POWER_NECK", "from": "Dual18650.5V_Pin2",     "to": "MAX98357A.VIN",         "signal": "AMP_5V",        "volt": "5.0V", "color": "橙 (穿颈3)"},
    {"id": "W04", "bus": "POWER_NECK", "from": "Dual18650.3V3_Pin1",    "to": "GMT020_LCD.BLK",        "signal": "LCD_BLK_3V3",   "volt": "3.3V", "color": "黄 (穿颈4)"},
    {"id": "W05", "bus": "POWER_NECK", "from": "Dual18650.GND_Pin2",    "to": "INMP441.L/R",           "signal": "MIC_LEFT_GND",  "volt": "0V",   "color": "棕 (穿颈5)"},
    {"id": "W06", "bus": "POWER_CH",   "from": "Dual18650.3V3_Pin2",    "to": "PCA9685A.VCC",          "signal": "PCA_LOGIC_3V3", "volt": "3.3V", "color": "黄"},
    {"id": "W07", "bus": "POWER_CH",   "from": "Dual18650.5V_Pin3",     "to": "PCA9685A.V+",           "signal": "SERVO_5V",      "volt": "5.0V", "color": "红"},
    {"id": "W08", "bus": "POWER_CH",   "from": "Dual18650.GND_Pin3",    "to": "PCA9685A.GND",          "signal": "PCA_GND",       "volt": "0V",   "color": "黑"},
    {"id": "W09", "bus": "POWER_CH",   "from": "Dual18650.5V_Pin4",     "to": "DRV8833_F.VCC",         "signal": "MOT_F_5V",      "volt": "5.0V", "color": "红"},
    {"id": "W10", "bus": "POWER_CH",   "from": "Dual18650.GND_Pin4",    "to": "DRV8833_F.GND",         "signal": "MOT_F_GND",     "volt": "0V",   "color": "黑"},
    {"id": "W11", "bus": "POWER_CH",   "from": "Dual18650.5V_Pin5",     "to": "DRV8833_R.VCC",         "signal": "MOT_R_5V",      "volt": "5.0V", "color": "红"},
    {"id": "W12", "bus": "POWER_CH",   "from": "Dual18650.GND_Pin5",    "to": "DRV8833_R.GND",         "signal": "MOT_R_GND",     "volt": "0V",   "color": "黑"},

    # --- 2. Neck I2C Control Bus (Only 2 Signal Wires Control 4 Motors + Head Servo!) ---
    {"id": "W13", "bus": "I2C_NECK",   "from": "S3CAM.GPIO1",           "to": "PCA9685A.SDA",          "signal": "I2C_SDA",       "volt": "3.3V", "color": "蓝 (穿颈6)", "gpio": 1},
    {"id": "W14", "bus": "I2C_NECK",   "from": "S3CAM.GPIO2",           "to": "PCA9685A.SCL",          "signal": "I2C_SCL",       "volt": "3.3V", "color": "绿 (穿颈7)", "gpio": 2},

    # --- 3. Onboard OV3660 Short-Ribbon Camera (Head Internal FPC, 0 External Wires!) ---
    {"id": "W15", "bus": "CAM_FPC",    "from": "S3CAM.FPC_24P",         "to": "OV3660_CAM.FPC",        "signal": "OV3660_DVP_8B", "volt": "2.8V", "color": "铜色短排线"},

    # --- 4. GMT020-02 2.0" IPS SPI Display (Head Internal, 1-to-1 DuPont!) ---
    {"id": "W16", "bus": "SPI_LCD",    "from": "S3CAM.3V3_1",           "to": "GMT020_LCD.VCC",        "signal": "LCD_3V3",       "volt": "3.3V", "color": "红"},
    {"id": "W17", "bus": "SPI_LCD",    "from": "S3CAM.GND_2",           "to": "GMT020_LCD.GND",        "signal": "LCD_GND",       "volt": "0V",   "color": "黑"},
    {"id": "W18", "bus": "SPI_LCD",    "from": "S3CAM.GPIO21",          "to": "GMT020_LCD.SCL",        "signal": "SPI_SCLK",      "volt": "3.3V", "color": "黄", "gpio": 21},
    {"id": "W19", "bus": "SPI_LCD",    "from": "S3CAM.GPIO47",          "to": "GMT020_LCD.SDA",        "signal": "SPI_MOSI",      "volt": "3.3V", "color": "蓝", "gpio": 47},
    {"id": "W20", "bus": "SPI_LCD",    "from": "S3CAM.GPIO14",          "to": "GMT020_LCD.RES",        "signal": "LCD_RST",       "volt": "3.3V", "color": "绿", "gpio": 14},
    {"id": "W21", "bus": "SPI_LCD",    "from": "S3CAM.GPIO41",          "to": "GMT020_LCD.DC",         "signal": "LCD_DC",        "volt": "3.3V", "color": "橙", "gpio": 41},
    {"id": "W22", "bus": "SPI_LCD",    "from": "S3CAM.GPIO42",          "to": "GMT020_LCD.CS",         "signal": "LCD_CS",        "volt": "3.3V", "color": "白", "gpio": 42},

    # --- 5. Dedicated I2S1 Mic (INMP441, Head Internal, 1-to-1 DuPont!) ---
    {"id": "W23", "bus": "I2S1_MIC",   "from": "S3CAM.3V3_2",           "to": "INMP441.VDD",           "signal": "MIC_3V3",       "volt": "3.3V", "color": "红"},
    {"id": "W24", "bus": "I2S1_MIC",   "from": "S3CAM.GND_3",           "to": "INMP441.GND",           "signal": "MIC_GND",       "volt": "0V",   "color": "黑"},
    {"id": "W25", "bus": "I2S1_MIC",   "from": "S3CAM.GPIO39",          "to": "INMP441.SCK",           "signal": "I2S1_SCK",      "volt": "3.3V", "color": "白", "gpio": 39},
    {"id": "W26", "bus": "I2S1_MIC",   "from": "S3CAM.GPIO40",          "to": "INMP441.WS",            "signal": "I2S1_WS",       "volt": "3.3V", "color": "紫", "gpio": 40},
    {"id": "W27", "bus": "I2S1_MIC",   "from": "S3CAM.GPIO38",          "to": "INMP441.SD",            "signal": "I2S1_SD_IN",    "volt": "3.3V", "color": "青", "gpio": 38},

    # --- 6. Dedicated I2S0 Speaker Amp (MAX98357A + 3020 Speaker, Head Internal, 1-to-1!) ---
    {"id": "W28", "bus": "I2S0_AMP",   "from": "S3CAM.GND_4",           "to": "MAX98357A.GND",         "signal": "AMP_GND",       "volt": "0V",   "color": "黑"},
    {"id": "W29", "bus": "I2S0_AMP",   "from": "S3CAM.GPIO3",           "to": "MAX98357A.BCLK",        "signal": "I2S0_BCLK",     "volt": "3.3V", "color": "蓝", "gpio": 3},
    {"id": "W30", "bus": "I2S0_AMP",   "from": "S3CAM.GPIO43",          "to": "MAX98357A.LRC",         "signal": "I2S0_LRC",      "volt": "3.3V", "color": "绿", "gpio": 43},
    {"id": "W31", "bus": "I2S0_AMP",   "from": "S3CAM.GPIO44",          "to": "MAX98357A.DIN",         "signal": "I2S0_DOUT",     "volt": "3.3V", "color": "黄", "gpio": 44},
    {"id": "W32", "bus": "I2S0_AMP",   "from": "MAX98357A.SPK+",        "to": "SPEAKER_3020.+",        "signal": "SPK_BTL+",      "volt": "BTL",  "color": "红 (螺丝端子)"},
    {"id": "W33", "bus": "I2S0_AMP",   "from": "MAX98357A.SPK-",        "to": "SPEAKER_3020.-",        "signal": "SPK_BTL-",      "volt": "BTL",  "color": "黑 (螺丝端子)"},

    # --- 7. PCA9685A -> MG90S Servo (CH0) + 2× DRV8833 (CH1..CH8) + 4× Pre-Wired N20 Motors ---
    {"id": "W34", "bus": "SERVO",      "from": "PCA9685A.CH0_3P",       "to": "MG90S.3P_Plug",         "signal": "HEAD_TILT_PWM", "volt": "5V/50Hz","color": "原装3P直插"},
    {"id": "W35", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH1_PWM",      "to": "DRV8833_F.IN1",         "signal": "FL_FWD",        "volt": "3.3V", "color": "黄"},
    {"id": "W36", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH2_PWM",      "to": "DRV8833_F.IN2",         "signal": "FL_REV",        "volt": "3.3V", "color": "橙"},
    {"id": "W37", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH3_PWM",      "to": "DRV8833_F.IN3",         "signal": "FR_FWD",        "volt": "3.3V", "color": "蓝"},
    {"id": "W38", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH4_PWM",      "to": "DRV8833_F.IN4",         "signal": "FR_REV",        "volt": "3.3V", "color": "紫"},
    {"id": "W39", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH5_PWM",      "to": "DRV8833_R.IN1",         "signal": "RL_FWD",        "volt": "3.3V", "color": "黄"},
    {"id": "W40", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH6_PWM",      "to": "DRV8833_R.IN2",         "signal": "RL_REV",        "volt": "3.3V", "color": "橙"},
    {"id": "W41", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH7_PWM",      "to": "DRV8833_R.IN3",         "signal": "RR_FWD",        "volt": "3.3V", "color": "蓝"},
    {"id": "W42", "bus": "MOTOR_CTL",  "from": "PCA9685A.CH8_PWM",      "to": "DRV8833_R.IN4",         "signal": "RR_REV",        "volt": "3.3V", "color": "紫"},
    {"id": "W43", "bus": "MOTOR_PWR",  "from": "DRV8833_F.OUT1_OUT2",   "to": "N20_FL.2P_Plug",        "signal": "N20_FL_DRIVE",  "volt": "5V PWM","color": "原装2P直插"},
    {"id": "W44", "bus": "MOTOR_PWR",  "from": "DRV8833_F.OUT3_OUT4",   "to": "N20_FR.2P_Plug",        "signal": "N20_FR_DRIVE",  "volt": "5V PWM","color": "原装2P直插"},
    {"id": "W45", "bus": "MOTOR_PWR",  "from": "DRV8833_R.OUT1_OUT2",   "to": "N20_RL.2P_Plug",        "signal": "N20_RL_DRIVE",  "volt": "5V PWM","color": "原装2P直插"},
    {"id": "W46", "bus": "MOTOR_PWR",  "from": "DRV8833_R.OUT3_OUT4",   "to": "N20_RR.2P_Plug",        "signal": "N20_RR_DRIVE",  "volt": "5V PWM","color": "原装2P直插"},
]


def audit_netlist():
    used = {}
    errors = []
    for w in NETLIST:
        g = w.get("gpio")
        if g is None:
            continue
        if g in RESERVED_S3_CAM_GPIOS:
            errors.append(f"GPIO{g} collides with ESP32-S3-CAM reserved Camera/PSRAM/USB pin!")
        if g not in VALID_S3_FREE_GPIOS:
            errors.append(f"GPIO{g} is not in verified free ESP32-S3-CAM GPIO set!")
        if g in used:
            errors.append(f"GPIO{g} CONFLICT between {used[g]} and {w['signal']} (must be 1-to-1 DuPont!)")
        used[g] = w["signal"]

    neck_wires = sum(1 for w in NETLIST if "NECK" in w["bus"])
    return {
        "total_connections": len(NETLIST),
        "s3_gpios_used": len(used),
        "neck_wires": neck_wires,
        "pca9685_free_channels": "CH9..CH15 (7 spare PWM channels)",
        "gpio_map": {f"GPIO{k}": v for k, v in sorted(used.items())},
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }


def simulate_power_and_battery():
    """Verify Dual-18650 1S2P (5000mAh EVE 12C) 5V boost margin & Cloud Multimodal AI runtime."""
    modes = {
        "wifi_standby":     {"s3_cam": 110, "ov3660": 0,   "lcd": 35, "mic": 2, "amp": 12,  "pca": 10, "motors_4wd": 0,   "servo": 10},
        "ai_voice_chat":    {"s3_cam": 190, "ov3660": 0,   "lcd": 45, "mic": 2, "amp": 260, "pca": 10, "motors_4wd": 0,   "servo": 60},
        "vision_patrol":    {"s3_cam": 230, "ov3660": 95,  "lcd": 45, "mic": 2, "amp": 45,  "pca": 15, "motors_4wd": 320, "servo": 90},
        "peak_4wd_vision":  {"s3_cam": 280, "ov3660": 110, "lcd": 50, "mic": 2, "amp": 320, "pca": 15, "motors_4wd": 840, "servo": 220},
    }
    boost_eff = 0.88
    v_bat_nom = 3.7
    v_out = 5.0
    bat_wh = 5.0 * v_bat_nom  # 2× 2500mAh parallel = 5000mAh (18.5 Wh!)

    res = {}
    for m, comps in modes.items():
        i_5v = sum(comps.values())
        p_out = (i_5v / 1000.0) * v_out
        p_bat = p_out / boost_eff
        i_bat = (p_bat / v_bat_nom) * 1000.0
        runtime_h = (bat_wh * 0.90) / p_bat
        res[m] = {
            "i_5v_mA": i_5v,
            "i_bat_mA": round(i_bat, 1),
            "power_W": round(p_bat, 2),
            "board_3A_load_pct": round((i_5v / 3000.0) * 100.0, 1),
            "drv8833_per_ch_mA": round(comps["motors_4wd"] / 4.0, 1),
            "runtime_hours": round(runtime_h, 2),
            "brownout_safe": i_5v < 2600,
        }
    avg_p = (
        0.45 * res["wifi_standby"]["power_W"]
        + 0.30 * res["ai_voice_chat"]["power_W"]
        + 0.25 * res["vision_patrol"]["power_W"]
    )
    res["realistic_mixed_runtime_h"] = round((bat_wh * 0.90) / avg_p, 2)
    return res


def simulate_kinematics_and_stability():
    """Verify 4WD skid-steer traction, 50/50 Dual-18650 CG stability, and MG90S servo torque margin."""
    masses = {
        "printed_shells_15_parts": 225.0,
        "dual_18650_board_and_2x_eve": 118.0,
        "esp32_s3_cam_and_ov3660": 16.0,
        "4x_n20_motors": 42.0,
        "mg90s_servo": 13.5,
        "pca9685_2x_drv8833_amp": 24.0,
        "gmt020_lcd_3020spk_mic": 30.0,
        "4x_43mm_complete_wheels_m3": 68.0,
    }
    total_g = sum(masses.values())
    total_kg = total_g / 1000.0

    wheel_d = 0.043  # 4× Ø43×18mm complete rubber wheels
    v_max_ms = (120.0 / 60.0) * math.pi * wheel_d
    t_motor_nm = 0.0883 * 0.80 * 0.40
    max_slope_deg = math.degrees(math.asin(min(0.99, (4.0 * t_motor_nm / (wheel_d / 2.0)) / (total_kg * 9.81))))

    # 50/50 CG: head (~132g at Y=-1.0, Z=120), centered dual-18650 (~118g at Y=0.0, Z=29), chassis (~286.5g at Y=+0.5, Z=34)
    y_cg = (132.0 * (-1.0) + 118.0 * 0.0 + 286.5 * 0.5) / total_g
    z_cg = (132.0 * 120.0 + 118.0 * 29.0 + 286.5 * 34.0) / total_g
    head_torque_kgcm = 0.132 * 2.2
    return {
        "drivetrain": "4WD Skid-Steer (4× GA12-N20 + 4× Complete Ø43×18mm Rubber Wheels)",
        "total_mass_g": round(total_g, 1),
        "max_linear_speed_cm_s": round(v_max_ms * 100.0, 1),
        "max_continuous_slope_deg": round(max_slope_deg, 1),
        "cg_y_mm": round(y_cg, 2),
        "cg_z_mm": round(z_cg, 2),
        "support_polygon_y_mm": [-38.0, 38.0],
        "rear_tip_margin_mm": round(y_cg - (-38.0), 2),
        "front_tip_margin_mm": round(38.0 - y_cg, 2),
        "static_stability": "PASS (50/50 dead-center Dual-18650 CG inside 76mm 4WD wheelbase!)" if (-38.0 < y_cg < 38.0) else "CHECK",
        "head_servo_torque_required_kgcm": round(head_torque_kgcm, 3),
        "mg90s_torque_safety_factor": round(1.8 / head_torque_kgcm, 1),
    }


def main():
    net = audit_netlist()
    pwr = simulate_power_and_battery()
    kin = simulate_kinematics_and_stability()
    report = {
        "platform": "KRON-01V6 (ESP32-S3-CAM N16R8 Zero-Soldering Edition — Dual-18650 + PCA9685A + 2× DRV8833)",
        "netlist_audit": net,
        "netlist": NETLIST,
        "power_simulation": pwr,
        "kinematics_stability": kin,
    }
    out = Path(__file__).resolve().parent.parent / "export" / "netlist_and_sim_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print("=" * 82)
    print("  KRON-01V6 (ESP32-S3-CAM N16R8 v2.0.0) FULL SYSTEM SIMULATION & NETLIST AUDIT")
    print("=" * 82)
    print(f"[1] 1-to-1 S3-CAM Netlist : {net['total_connections']} connections | {net['s3_gpios_used']} GPIOs | {net['neck_wires']} neck wires | {net['status']}")
    print(f"    PCA9685A Spare PWM    : {net['pca9685_free_channels']}")
    print(f"[2] 5V Peak Load (4WD+AI) : {pwr['peak_4wd_vision']['i_5v_mA']} mA ({pwr['peak_4wd_vision']['board_3A_load_pct']}% of 3A) | DRV8833: {pwr['peak_4wd_vision']['drv8833_per_ch_mA']}mA/ch (<1500mA) | Safe: {pwr['peak_4wd_vision']['brownout_safe']}")
    print(f"[3] Mixed AI Runtime      : {pwr['realistic_mixed_runtime_h']} hours on 5000mAh 1S2P Dual-18650!")
    print(f"[4] 4WD Mass & Climbing   : {kin['total_mass_g']} g | Max Speed: {kin['max_linear_speed_cm_s']} cm/s | Max Slope: {kin['max_continuous_slope_deg']} deg")
    print(f"[5] 50/50 Center of Grav  : Y={kin['cg_y_mm']} mm (Rear=-38, Front=+38) -> {kin['static_stability']}")
    print(f"[6] Head Servo Margin     : {kin['head_servo_torque_required_kgcm']} kg·cm needed vs 1.8 kg·cm ({kin['mg90s_torque_safety_factor']}x safety factor)")
    if net["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
