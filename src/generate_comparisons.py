import argparse
import os
from compare import run_method
from env import load_config, Environment

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--methods", default="ga,hga,pbig,max_sinr,random")
    p.add_argument("--users", required=True)
    p.add_argument("--beams", type=int, required=True)
    p.add_argument("--out_dir", required=True)
    args = p.parse_args()
    users_list = [int(x) for x in args.users.split(",") if x.strip()]
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    os.makedirs(args.out_dir, exist_ok=True)
    for u in users_list:
        cfg = load_config(args.config)
        cfg["users_min"] = u
        cfg["beams_per_cell"] = args.beams
        env = Environment(cfg)
        rows = []
        for mname in methods:
            a, m = run_method(env, mname)
            rows.append([mname, m["feasible"], int(m["total"]), round(m["jain"], 4), round(m["objective"], 2), u, args.beams])
        out_path = os.path.join(args.out_dir, f"comparison_u{u}_b{args.beams}.csv")
        with open(out_path, "w") as f:
            f.write("method,feasible,total_bps,jain,objective,users,beams\n")
            for r in rows:
                f.write(",".join(map(str, r)) + "\n")

if __name__ == "__main__":
    main()
