# backend/main.py — 根据 cadence 产出 /output/*.json
import argparse, json, datetime as dt, pathlib
OUT = pathlib.Path("output"); OUT.mkdir(exist_ok=True)
def now(): return dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
def build(cadence):
    return {"schema_version":"1.3.x","cadence":cadence,"updated_at": now(),"items":[],"market_regime":{"s5_regime":"neutral","score":0.5}}
def build_stages(cadence): return {"cadence":cadence,"stages":{"S1":{"pool":[]}, "S2":{"pool":[]}, "S3":{"pool":[]}, "S4":{"pool":[]}, "S5":{"pool":[]}},"fake_start":0,"watchlist":[]}
def build_sensors(cadence): return {"cadence":cadence,"layers":[]}
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--cadence", required=True)
    args = ap.parse_args()
    (OUT/"board.json").write_text(json.dumps(build(args.cadence), ensure_ascii=False, indent=2))
    (OUT/"stages.json").write_text(json.dumps(build_stages(args.cadence), ensure_ascii=False, indent=2))
    (OUT/"sensors.json").write_text(json.dumps(build_sensors(args.cadence), ensure_ascii=False, indent=2))
