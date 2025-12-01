import argparse
import csv
from env import load_config, Environment
from model import compute_metrics
from algorithms.ga import run as run_ga
from algorithms.hga import run as run_hga
from algorithms.pbig import run as run_pbig
from algorithms.baselines import max_sinr, random_assignment

def run_method(env, method):
    if method == "ga":
        a = run_ga(env)
    elif method == "hga":
        a = run_hga(env)
    elif method == "pbig":
        a = run_pbig(env)
    elif method == "max_sinr":
        a = max_sinr(env)
    elif method == "random":
        a = random_assignment(env)
    else:
        a = max_sinr(env)
    m = compute_metrics(a, env)
    return a, m

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--methods", required=True)
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
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    rows = []
    for mname in methods:
        a, m = run_method(env, mname)
        rows.append([mname, m["feasible"], int(m["total"]), round(m["jain"], 4), round(m["objective"], 2), args.users or env.I, args.beams or env.K])
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method","feasible","total_bps","jain","objective","users","beams"])
        for r in rows:
            w.writerow(r)

if __name__ == "__main__":
    main()
