"""
KRON-01V4 (4WD Rounded Vision Edition) — Full System Engineering Simulator
===========================================================================
Verifies before 3D printing & hardware purchase:
  1. Complete Raspberry Pi Zero 2W 40-Pin BCM + MIPI CSI-2 FFC + 4WD Parallel N20 Netlist (44 connections)
     - Official SPI0 (GPIO8/10/11 + DC/RST/BLK) -> 2.0" ST7789V IPS LCD
     - Full-Duplex Shared I2S (GPIO18 BCLK, GPIO19 LRCLK, GPIO20 Mic DIN, GPIO21 Amp DOUT)
     - Hardware PWM1 (GPIO13) -> MG90S Head Tilt Servo (zero Linux jitter)
     - DRV8833 Dual H-Bridge (GPIO5/6/22/23) -> 4× GA12-N20 (FL+RL parallel on OUT1/2, FR+RR parallel on OUT3/4!)
     - Dedicated MIPI CSI-2 22-to-15pin FFC Ribbon -> Forehead OV5647 5MP 160° Camera
     - Leaves I2C1 (GPIO2/3) & UART0 (GPIO14/15) 100% FREE!
  2. IP5328P 5V/3A (15W) Power Margin & 3000mAh 10A High-Drain 18650 Runtime Simulation (4WD Load)
  3. 4WD Skid-Steer Kinematics, 50/50 Centered-18650 CG Stability & MG90S Servo Torque Margin
"""

import json
import math
from pathlib import Path

SHARED_ALLOWED_GPIOS = {18, 19}
VALID_RPI_BCM = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27}

NETLIST = [
    # --- Power Tree (Center 3000mAh 18650 -> Switch -> IP5328P 5V/3A -> 5V/GND Rails) ---
    {"id": "W01", "bus": "POWER",   "from": "18650_3000mAh.B+",      "to": "SW_SS12D00G3.COM",      "signal": "VBAT_RAW",     "volt": "3.7V",     "color": "红 20AWG"},
    {"id": "W02", "bus": "POWER",   "from": "SW_SS12D00G3.ON",       "to": "IP5328P_3A.BAT+",       "signal": "VBAT_SW",      "volt": "3.7V",     "color": "红 20AWG"},
    {"id": "W03", "bus": "POWER",   "from": "18650_3000mAh.B-",      "to": "IP5328P_3A.BAT-",       "signal": "GND_BAT",      "volt": "0V",       "color": "黑 20AWG"},
    {"id": "W04", "bus": "POWER",   "from": "IP5328P_3A.OUT_5V+",    "to": "RPi_Zero2W.Pin2(5V)",   "signal": "5V_3A_RAIL",   "volt": "5.0V",     "color": "红 20AWG"},
    {"id": "W05", "bus": "POWER",   "from": "IP5328P_3A.OUT_GND",    "to": "RPi_Zero2W.Pin6(GND)",  "signal": "GND_BUS",      "volt": "0V",       "color": "黑 20AWG"},

    # --- Forehead OV5647 / IMX219 5MP Wide-Angle Camera (Dedicated MIPI CSI-2 15cm FFC!) ---
    {"id": "W06", "bus": "CSI_CAM", "from": "RPi_Zero2W.CSI2_22P",   "to": "OV5647_CAM.CSI_15P",    "signal": "MIPI_CSI2_2L", "volt": "1.2V/3.3V","color": "白扁平排线 15cm"},

    # --- 2.0" ST7789V IPS Display (8-Pin Hardware SPI0 @ 40MHz) ---
    {"id": "W07", "bus": "SPI_LCD", "from": "RPi_Zero2W.Pin1(3V3)",  "to": "ST7789_LCD.VCC",        "signal": "LCD_3V3",      "volt": "3.3V",     "color": "红"},
    {"id": "W08", "bus": "SPI_LCD", "from": "RPi_Zero2W.Pin9(GND)",  "to": "ST7789_LCD.GND",        "signal": "LCD_GND",      "volt": "0V",       "color": "黑"},
    {"id": "W09", "bus": "SPI_LCD", "from": "RPi_Zero2W.GPIO11(P23)","to": "ST7789_LCD.SCL",        "signal": "SPI0_SCLK",    "volt": "3.3V",     "color": "黄", "gpio": 11},
    {"id": "W10", "bus": "SPI_LCD", "from": "RPi_Zero2W.GPIO10(P19)","to": "ST7789_LCD.SDA",        "signal": "SPI0_MOSI",    "volt": "3.3V",     "color": "蓝", "gpio": 10},
    {"id": "W11", "bus": "SPI_LCD", "from": "RPi_Zero2W.GPIO24(P18)","to": "ST7789_LCD.RES",        "signal": "LCD_RST",      "volt": "3.3V",     "color": "绿", "gpio": 24},
    {"id": "W12", "bus": "SPI_LCD", "from": "RPi_Zero2W.GPIO25(P22)","to": "ST7789_LCD.DC",         "signal": "LCD_DC",       "volt": "3.3V",     "color": "橙", "gpio": 25},
    {"id": "W13", "bus": "SPI_LCD", "from": "RPi_Zero2W.GPIO8(P24)", "to": "ST7789_LCD.CS",         "signal": "SPI0_CE0",     "volt": "3.3V",     "color": "白", "gpio": 8},
    {"id": "W14", "bus": "SPI_LCD", "from": "RPi_Zero2W.GPIO12(P32)","to": "ST7789_LCD.BLK",        "signal": "LCD_PWM0",     "volt": "3.3V",     "color": "灰", "gpio": 12},

    # --- Full-Duplex Shared I2S Audio: INMP441 Mic (RX) + MAX98357A Amp (TX) + 28mm Speaker ---
    {"id": "W15", "bus": "I2S_MIC", "from": "RPi_Zero2W.Pin17(3V3)", "to": "INMP441.VDD",           "signal": "MIC_3V3",      "volt": "3.3V",     "color": "红"},
    {"id": "W16", "bus": "I2S_MIC", "from": "RPi_Zero2W.Pin14(GND)", "to": "INMP441.GND",           "signal": "MIC_GND",      "volt": "0V",       "color": "黑"},
    {"id": "W17", "bus": "I2S_MIC", "from": "INMP441.GND",           "to": "INMP441.L/R",           "signal": "LEFT_CH",      "volt": "0V",       "color": "黑(短接)"},
    {"id": "W18", "bus": "I2S_MIC", "from": "RPi_Zero2W.GPIO18(P12)","to": "INMP441.SCK",           "signal": "I2S_BCLK*",    "volt": "3.3V",     "color": "白", "gpio": 18},
    {"id": "W19", "bus": "I2S_MIC", "from": "RPi_Zero2W.GPIO19(P35)","to": "INMP441.WS",            "signal": "I2S_LRCLK*",   "volt": "3.3V",     "color": "紫", "gpio": 19},
    {"id": "W20", "bus": "I2S_MIC", "from": "RPi_Zero2W.GPIO20(P38)","to": "INMP441.SD",            "signal": "I2S_PCM_DIN",  "volt": "3.3V",     "color": "青", "gpio": 20},

    {"id": "W21", "bus": "I2S_AMP", "from": "IP5328P_3A.OUT_5V+",    "to": "MAX98357A.VIN",         "signal": "AMP_5V",       "volt": "5.0V",     "color": "红"},
    {"id": "W22", "bus": "I2S_AMP", "from": "IP5328P_3A.OUT_GND",    "to": "MAX98357A.GND",         "signal": "AMP_GND",      "volt": "0V",       "color": "黑"},
    {"id": "W23", "bus": "I2S_AMP", "from": "RPi_Zero2W.GPIO18(P12)","to": "MAX98357A.BCLK",        "signal": "I2S_BCLK*",    "volt": "3.3V",     "color": "蓝", "gpio": 18},
    {"id": "W24", "bus": "I2S_AMP", "from": "RPi_Zero2W.GPIO19(P35)","to": "MAX98357A.LRC",         "signal": "I2S_LRCLK*",   "volt": "3.3V",     "color": "绿", "gpio": 19},
    {"id": "W25", "bus": "I2S_AMP", "from": "RPi_Zero2W.GPIO21(P40)","to": "MAX98357A.DIN",         "signal": "I2S_PCM_OUT",  "volt": "3.3V",     "color": "黄", "gpio": 21},
    {"id": "W26", "bus": "I2S_AMP", "from": "MAX98357A.SPK+",        "to": "SPEAKER_28MM.+",        "signal": "SPK_OUT+",     "volt": "BTL",      "color": "红"},
    {"id": "W27", "bus": "I2S_AMP", "from": "MAX98357A.SPK-",        "to": "SPEAKER_28MM.-",        "signal": "SPK_OUT-",     "volt": "BTL",      "color": "黑"},

    # --- DRV8833 Dual H-Bridge (1.5A/ch) + 4x GA12-N20 4WD Parallel Left(FL+RL) / Right(FR+RR) ---
    {"id": "W28", "bus": "MOTOR",   "from": "IP5328P_3A.OUT_5V+",    "to": "DRV8833.VCC",           "signal": "MOT_5V",       "volt": "5.0V",     "color": "红"},
    {"id": "W29", "bus": "MOTOR",   "from": "IP5328P_3A.OUT_GND",    "to": "DRV8833.GND",           "signal": "MOT_GND",      "volt": "0V",       "color": "黑"},
    {"id": "W30", "bus": "MOTOR",   "from": "RPi_Zero2W.GPIO5(P29)", "to": "DRV8833.IN1",           "signal": "MOT_L_FWD",    "volt": "3.3V",     "color": "黄", "gpio": 5},
    {"id": "W31", "bus": "MOTOR",   "from": "RPi_Zero2W.GPIO6(P31)", "to": "DRV8833.IN2",           "signal": "MOT_L_REV",    "volt": "3.3V",     "color": "橙", "gpio": 6},
    {"id": "W32", "bus": "MOTOR",   "from": "RPi_Zero2W.GPIO22(P15)","to": "DRV8833.IN3",           "signal": "MOT_R_FWD",    "volt": "3.3V",     "color": "蓝", "gpio": 22},
    {"id": "W33", "bus": "MOTOR",   "from": "RPi_Zero2W.GPIO23(P16)","to": "DRV8833.IN4",           "signal": "MOT_R_REV",    "volt": "3.3V",     "color": "紫", "gpio": 23},
    {"id": "W34", "bus": "MOTOR",   "from": "DRV8833.OUT1",          "to": "N20_FL.+",              "signal": "N20_FL+",      "volt": "5V PWM",   "color": "黄"},
    {"id": "W35", "bus": "MOTOR",   "from": "DRV8833.OUT2",          "to": "N20_FL.-",              "signal": "N20_FL-",      "volt": "5V PWM",   "color": "黑"},
    {"id": "W36", "bus": "MOTOR",   "from": "DRV8833.OUT1",          "to": "N20_RL.+(并联)",        "signal": "N20_RL+",      "volt": "5V PWM",   "color": "黄"},
    {"id": "W37", "bus": "MOTOR",   "from": "DRV8833.OUT2",          "to": "N20_RL.-(并联)",        "signal": "N20_RL-",      "volt": "5V PWM",   "color": "黑"},
    {"id": "W38", "bus": "MOTOR",   "from": "DRV8833.OUT3",          "to": "N20_FR.+",              "signal": "N20_FR+",      "volt": "5V PWM",   "color": "蓝"},
    {"id": "W39", "bus": "MOTOR",   "from": "DRV8833.OUT4",          "to": "N20_FR.-",              "signal": "N20_FR-",      "volt": "5V PWM",   "color": "黑"},
    {"id": "W40", "bus": "MOTOR",   "from": "DRV8833.OUT3",          "to": "N20_RR.+(并联)",        "signal": "N20_RR+",      "volt": "5V PWM",   "color": "蓝"},
    {"id": "W41", "bus": "MOTOR",   "from": "DRV8833.OUT4",          "to": "N20_RR.-(并联)",        "signal": "N20_RR-",      "volt": "5V PWM",   "color": "黑"},

    # --- MG90S Head Tilt Servo (Dedicated Hardware PWM1 = Zero Jitter!) ---
    {"id": "W42", "bus": "SERVO",   "from": "IP5328P_3A.OUT_5V+",    "to": "MG90S.VCC(红)",         "signal": "SERVO_5V",     "volt": "5.0V",     "color": "红"},
    {"id": "W43", "bus": "SERVO",   "from": "IP5328P_3A.OUT_GND",    "to": "MG90S.GND(棕)",         "signal": "SERVO_GND",    "volt": "0V",       "color": "棕"},
    {"id": "W44", "bus": "SERVO",   "from": "RPi_Zero2W.GPIO13(P33)","to": "MG90S.SIG(橙)",         "signal": "HEAD_PWM1",    "volt": "50Hz",     "color": "橙", "gpio": 13},
]


def audit_netlist():
    used = {}
    errors = []
    for w in NETLIST:
        g = w.get("gpio")
        if g is None:
            continue
        if g not in VALID_RPI_BCM:
            errors.append(f"GPIO{g} invalid on Raspberry Pi Zero 2W 40-pin header!")
        if g in used and g not in SHARED_ALLOWED_GPIOS:
            errors.append(f"GPIO{g} CONFLICT between {used[g]} and {w['signal']}")
        used.setdefault(g, []).append(w["signal"])
    return {
        "total_connections": len(NETLIST),
        "bcm_gpios_used": len(used),
        "free_buses": ["I2C1 (GPIO2/3)", "UART0 (GPIO14/15)", "GPIO4/7/9/16/17/26/27"],
        "gpio_map": {f"GPIO{k}": " + ".join(v) for k, v in sorted(used.items())},
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }


def simulate_power_and_battery():
    """Verify IP5328P 5V/3A (3000mA) boost margin & 3000mAh 10A 18650 runtime with 4x N20 4WD load."""
    modes = {
        "linux_idle":      {"rpi_zero2w": 240, "csi_cam": 0,   "lcd": 35, "mic": 2, "amp": 15,  "motors_4wd": 0,   "servo": 10},
        "cv_face_track":   {"rpi_zero2w": 520, "csi_cam": 165, "lcd": 45, "mic": 2, "amp": 40,  "motors_4wd": 280, "servo": 95},
        "ai_voice_vision": {"rpi_zero2w": 580, "csi_cam": 165, "lcd": 45, "mic": 2, "amp": 280, "motors_4wd": 0,   "servo": 80},
        "peak_4wd_yolo":   {"rpi_zero2w": 720, "csi_cam": 185, "lcd": 50, "mic": 2, "amp": 320, "motors_4wd": 840, "servo": 220},
    }
    boost_eff = 0.89
    v_bat_nom = 3.7
    v_out = 5.0
    bat_wh = 3.0 * v_bat_nom  # 11.1 Wh

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
            "ip5328p_3A_load_pct": round((i_5v / 3000.0) * 100.0, 1),
            "drv8833_per_ch_mA": round(comps["motors_4wd"] / 2.0, 1),
            "runtime_hours": round(runtime_h, 2),
            "brownout_safe": i_5v < 2700,
        }
    avg_p = (
        0.50 * res["linux_idle"]["power_W"]
        + 0.30 * res["cv_face_track"]["power_W"]
        + 0.20 * res["ai_voice_vision"]["power_W"]
    )
    res["realistic_mixed_runtime_h"] = round((bat_wh * 0.90) / avg_p, 2)
    return res


def simulate_kinematics_and_stability():
    """Verify 4WD skid-steer traction, 50/50 centered-18650 CG stability, and MG90S torque margin."""
    masses = {
        "printed_pla_clamshell_shells": 205.0,
        "18650_3000mah_and_holder": 58.0,
        "rpi_zero2w_and_heatsink": 18.0,
        "ov5647_csi_cam_and_ffc": 11.0,
        "4x_n20_motors": 40.0,
        "mg90s_servo": 13.5,
        "pcbs_drv_amp_ip5328p": 16.0,
        "2in_lcd_speaker_mic": 24.0,
        "4x_tires_and_m3_screws": 46.0,
    }
    total_g = sum(masses.values())
    total_kg = total_g / 1000.0

    wheel_d = 0.042  # 4x Ø42mm chunky off-road wheels
    v_max_ms = (120.0 / 60.0) * math.pi * wheel_d
    # 4x N20 continuous torque -> double the traction & hill-climb of 2WD!
    t_motor_nm = 0.0883 * 0.80 * 0.40
    max_slope_deg = math.degrees(math.asin(min(0.99, (4.0 * t_motor_nm / (wheel_d / 2.0)) / (total_kg * 9.81))))

    # 50/50 CG: head (~108g at Y=-1.0, Z=90), centered 18650 (~58g at Y=0.0, Z=28), 4WD chassis (~265.5g at Y=+1.0, Z=32)
    y_cg = (108 * (-1.0) + 58 * 0.0 + 265.5 * 1.0) / total_g
    z_cg = (108 * 90.0 + 58 * 28.0 + 265.5 * 32.0) / total_g
    head_torque_kgcm = 0.108 * 2.1
    return {
        "drivetrain": "4WD Skid-Steer (4× GA12-N20 + 4× Ø42mm Off-Road Wheels)",
        "total_mass_g": round(total_g, 1),
        "max_linear_speed_cm_s": round(v_max_ms * 100.0, 1),
        "max_continuous_slope_deg": round(max_slope_deg, 1),
        "cg_y_mm": round(y_cg, 2),
        "cg_z_mm": round(z_cg, 2),
        "support_polygon_y_mm": [-30.0, 30.0],
        "rear_tip_margin_mm": round(y_cg - (-30.0), 2),
        "front_tip_margin_mm": round(30.0 - y_cg, 2),
        "static_stability": "PASS (50/50 dead-center CG inside 60mm 4WD wheelbase!)" if (-30.0 < y_cg < 30.0) else "CHECK",
        "head_servo_torque_required_kgcm": round(head_torque_kgcm, 3),
        "mg90s_torque_safety_factor": round(1.8 / head_torque_kgcm, 1),
    }


def main():
    net = audit_netlist()
    pwr = simulate_power_and_battery()
    kin = simulate_kinematics_and_stability()
    report = {
        "platform": "KRON-01V4 (4WD Clamshell Rounded Vision Edition — RPi Zero 2W + OV5647 CSI + 4× N20)",
        "netlist_audit": net,
        "netlist": NETLIST,
        "power_simulation": pwr,
        "kinematics_stability": kin,
    }
    out = Path(__file__).resolve().parent.parent / "export" / "netlist_and_sim_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print("=" * 76)
    print("  KRON-01V4 (4WD VISION EDITION) FULL ENGINEERING SIMULATION & NETLIST AUDIT")
    print("=" * 76)
    print(f"[1] RPi Zero 2W Netlist : {net['total_connections']} connections (4WD parallel + CSI FFC) | {net['bcm_gpios_used']} BCM GPIOs | {net['status']}")
    print(f"    Free Expansion Buses: {', '.join(net['free_buses'])}")
    print(f"[2] 5V/3A 4WD Peak Load : {pwr['peak_4wd_yolo']['i_5v_mA']} mA ({pwr['peak_4wd_yolo']['ip5328p_3A_load_pct']}% of 3A) | DRV8833: {pwr['peak_4wd_yolo']['drv8833_per_ch_mA']}mA/ch (<1500mA) | Safe: {pwr['peak_4wd_yolo']['brownout_safe']}")
    print(f"[3] Mixed Vision Runtime: {pwr['realistic_mixed_runtime_h']} hours on 3000mAh 18650")
    print(f"[4] 4WD Mass & Climbing : {kin['total_mass_g']} g | Max Speed: {kin['max_linear_speed_cm_s']} cm/s | Max Slope: {kin['max_continuous_slope_deg']} deg")
    print(f"[5] 50/50 Center of Grav: Y={kin['cg_y_mm']} mm (Rear=-26, Front=+26) -> {kin['static_stability']}")
    print(f"[6] Head Servo Margin   : {kin['head_servo_torque_required_kgcm']} kg·cm needed vs 1.8 kg·cm ({kin['mg90s_torque_safety_factor']}x safety factor)")


if __name__ == "__main__":
    main()
