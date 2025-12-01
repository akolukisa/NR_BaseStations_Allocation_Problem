import argparse
import csv
from env import load_config, Environment
from model import compute_metrics
from algorithms.ga import run as run_ga
from algorithms.hga import run as run_hga
from algorithms.pbig import run as run_pbig
from algorithms.baselines import max_sinr, random_assignment

def run_once(env, method):
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--users", type=int)
    parser.add_argument("--beams", type=int)
    parser.add_argument("--out")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.users:
        cfg["users_min"] = args.users
    if args.beams:
        cfg["beams_per_cell"] = args.beams
    env = Environment(cfg)
    a, m = run_once(env, args.method)
    print("feasible=", m["feasible"]) 
    print("total_bps=", int(m["total"]))
    print("jain=", round(m["jain"], 4))
    print("objective=", round(m["objective"], 2))
    if args.out:
        with open(args.out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["user", "gnb", "beam", "bps"])
            for i, (j, k) in enumerate(a):
                w.writerow([i, j, k, m["rates"][i]])

if __name__ == "__main__":
    main()
