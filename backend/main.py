# backend/main.py
# EtherionOS 数据生成器（无外部依赖 / 可重复 / 稳定）
# 说明：
# - 根据 cadence 生成 /output/board.json /output/stages.json /output/sensors.json
# - 不访问网络、不依赖第三方库，确保 GitHub Actions 可稳定跑通
# - “种子项目”写在本文件里；分数按日期 + 项目名稳定伪随机，便于演示与对比

import json, os, math, hashlib, datetime
from pathlib import Path

# ---------- 配置 ----------
SCHEMA_VERSION = "1.3.x"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# cadence 从工作流传入：daily / tplus3 / weekly
CADENCE = os.getenv("CADENCE", "daily").strip().lower()

# 固定 UTC 时间戳
updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

# 1000x / 10000x 两类“榜单”，以及阶段池
SEED_PROJECTS = [
    # bucket,  structure, stage, name
    ("1000x",  "再质押（Restaking 协议）",     "S1", "Karak"),
    ("1000x",  "社交基础设施（Social Infra）", "S1", "OLAS"),
    ("1000x",  "数据可用性（DA）",             "S2", "Seed1"),
    ("10000x", "零知识基础设施（ZK Infra）",   "S2", "ZKM"),
    ("10000x", "RWA 资产通道",                 "S2", "Ondo"),
]

# 传感器层（S0–S0′），每层 2~3 个探针键
SENSOR_LAYERS = {
    "L1_supply":   ["lp_lock_ratio", "holder_gini"],
    "L2_demand":   ["tg_growth_7d", "x_engagement"],
    "L3_liquidity":["depth_usd"],
    "L4_devops":   ["commit_7d"],
    "L5_narrative":["news_pulse"],
    "L6_risk":     ["contract_risk"],
}

# ---------- 工具 ----------
def stable_rand_0_1(key: str) -> float:
    """基于 key 的稳定伪随机 [0,1)"""
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    # 取前 12 位转整数，归一化
    return (int(h[:12], 16) % 10_000_000) / 10_000_000.0

def pct01(x):
    return max(0.0, min(1.0, float(x)))

def round1(x):
    return float(f"{x:.1f}")

def cadence_tag(cadence: str) -> str:
    return {"daily": "daily", "tplus3": "t+3", "weekly": "weekly"}.get(cadence, "daily")

# 根据 cadence 对强度做微调（比如周报波动大、t+3 居中、日更最平滑）
def cadence_boost(keybase: str, base: float) -> float:
    r = stable_rand_0_1(f"{keybase}|{CADENCE}")
    if CADENCE == "weekly":
        return pct01(base * (0.85 + 0.40 * r))  # ±15~40%
    if CADENCE in ("tplus3", "t+3"):
        return pct01(base * (0.90 + 0.20 * r))  # ±10~20%
    return pct01(base * (0.95 + 0.10 * r))      # ±5~10%

# ---------- 生成 board.json ----------
def gen_board():
    items = []
    for (bucket, structure, stage, name) in SEED_PROJECTS:
        key = f"{name}|{bucket}|{CADENCE}"
        # 八个代理因子（0~100），内部用 0~1 表示
        agents = {
            "A1_vol_mcap":   round(pct01(cadence_boost(key+":A1", 0.50 + 0.45 * stable_rand_0_1(key+":a")) )*100),
            "A2_tvl":        round(pct01(cadence_boost(key+":A2", 0.45 + 0.50 * stable_rand_0_1(key+":b")) )*100),
            "A3_sns":        round(pct01(cadence_boost(key+":A3", 0.40 + 0.55 * stable_rand_0_1(key+":c")) )*100),
            "A4_depth":      round(pct01(cadence_boost(key+":A4", 0.40 + 0.50 * stable_rand_0_1(key+":d")) )*100),
            "B1_leverage":   round(pct01(cadence_boost(key+":B1", 0.40 + 0.55 * stable_rand_0_1(key+":e")) )*100),
            "B2_whale":      round(pct01(cadence_boost(key+":B2", 0.35 + 0.60 * stable_rand_0_1(key+":f")) )*100),
            "B3_dev":        round(pct01(cadence_boost(key+":B3", 0.45 + 0.50 * stable_rand_0_1(key+":g")) )*100),
            "B4_ecosys":     round(pct01(cadence_boost(key+":B4", 0.40 + 0.50 * stable_rand_0_1(key+":h")) )*100),
        }
        # 评分（简单加权）
        score = (
            0.18*agents["A1_vol_mcap"] + 0.15*agents["A2_tvl"] + 0.12*agents["A3_sns"] + 0.10*agents["A4_depth"] +
            0.15*agents["B1_leverage"] + 0.10*agents["B2_whale"] + 0.10*agents["B3_dev"] + 0.10*agents["B4_ecosys"]
        ) / 100.0
        score_total = round1(score*100)  # 0~100 一位小数

        # KPI 补充
        tvl3 = round1(  -2.0 + 8.0 * stable_rand_0_1(key+":tvl3") )  # -2% ~ +6%
        vol1 = round1(   2.0 + 8.0 * stable_rand_0_1(key+":vol1") )  # +2% ~ +10%
        actions = "仅事件/短线；严格风控" if bucket=="10000x" else "分批建仓至 50%；失去关键指标转弱减仓"

        items.append({
            "project": name,
            "bucket": bucket,
            "structure": structure,
            "stage": stage,
            "score_total": score_total,
            "confidence": round1(0.55 + 0.35 * stable_rand_0_1(key+":conf")),
            "current_price": None,
            "agents": agents,
            "metrics": {
                "TVL_3d": tvl3,
                "VolMcap_1d": vol1,
            },
            "actions": actions
        })

    # 市场状态（S5）
    mr_key = f"market|{CADENCE}"
    s5_score = round1(0.30 + 0.40 * stable_rand_0_1(mr_key))
    regime = "bull" if s5_score >= 0.66 else ("bear" if s5_score <= 0.34 else "neutral")

    board = {
        "schema_version": SCHEMA_VERSION,
        "cadence": cadence_tag(CADENCE),
        "updated_at": updated_at,
        "items": items,
        "market_regime": {"s5_regime": regime, "score": s5_score}
    }
    (OUTPUT_DIR/"board.json").write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- 生成 stages.json ----------
def gen_stages():
    stages = {"S1":{"pool":[]}, "S2":{"pool":[]}, "S3":{"pool":[]}, "S4":{"pool":[]}, "S5":{"pool":[]}}
    watchlist = []

    for (bucket, structure, stage, name) in SEED_PROJECTS:
        # 简单的流转：t+3 或 weekly 时，按概率把若干候选推进一级
        st = stage
        r = stable_rand_0_1(f"stage|{name}|{CADENCE}")
        if CADENCE in ("tplus3","t+3") and r>0.70 and st!="S5":
            st = f"S{min(int(st[1])+1,5)}"
        if CADENCE=="weekly" and r>0.55 and st!="S5":
            st = f"S{min(int(st[1])+1,5)}"
        stages[st]["pool"].append(name)

        # 少量项目放入观察池
        if r < 0.25:
            watchlist.append(name)

    fake_start = sum(1 for n in watchlist if stable_rand_0_1("fake|"+n) > 0.6)

    out = {
        "cadence": cadence_tag(CADENCE),
        "stages": stages,
        "fake_start": fake_start,
        "watchlist": watchlist
    }
    (OUTPUT_DIR/"stages.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- 生成 sensors.json ----------
def gen_sensors():
    layers = []
    for layer, probes in SENSOR_LAYERS.items():
        q_base = 0.55 + 0.35 * stable_rand_0_1(f"quality|{layer}|{CADENCE}")
        q = round1(pct01(cadence_boost(layer, q_base)) * 100)  # 显示成 0~100
        pr = []
        for k in probes:
            key = f"{layer}|{k}|{CADENCE}"
            # 数值型/百分比型混合
            if k in ("lp_lock_ratio","holder_gini"):
                v = round1(50 + 50*stable_rand_0_1(key))  # 0~100
            elif k in ("tg_growth_7d","x_engagement","news_pulse"):
                v = round1(-2.0 + 8.0*stable_rand_0_1(key))  # -2%~+6%
            elif k=="depth_usd":
                v = int(50_000 + 200_000*stable_rand_0_1(key))  # 5万到25万
            elif k=="commit_7d":
                v = int(5 + 40*stable_rand_0_1(key))           # 5~45
            elif k=="contract_risk":
                v = ["低","中","高"][ int(3*stable_rand_0_1(key)) % 3 ]
            else:
                v = round1(100*stable_rand_0_1(key))
            pr.append({"k": k, "v": v})
        layers.append({"layer": layer, "quality": q/100.0, "probes": pr})

    out = {"cadence": cadence_tag(CADENCE), "layers": layers}
    (OUTPUT_DIR/"sensors.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- 主程 ----------
if __name__ == "__main__":
    gen_board()
    gen_stages()
    gen_sensors()
    print(f"[ok] wrote output/*.json | cadence={CADENCE} | updated_at={updated_at}")
