import argparse
import json
from env import load_config, Environment

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--users", type=int)
    p.add_argument("--beams", type=int)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    cfg = load_config(args.config)
    if args.users:
        cfg["users_min"] = args.users
    if args.beams:
        cfg["beams_per_cell"] = args.beams
    env = Environment(cfg)
    data = {
        "gnb": [{"lat": lat, "lon": lon} for (lat, lon) in env.gnb_pos],
        "ue": [{"lat": lat, "lon": lon} for (lat, lon) in env.ue_pos]
    }
    with open(args.out, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    main()
