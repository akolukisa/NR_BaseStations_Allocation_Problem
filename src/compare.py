import argparse
import csv
from env import load_config, Environment
from model import compute_metrics, compute_metrics_lower
from algorithms.ga import run as run_ga
from algorithms.hga import run as run_hga
from algorithms.pbig import run as run_pbig
from algorithms.baselines import max_sinr, random_assignment, random_assoc_no_repair

def run_method(env, method, fast=False):
    if method == "ga":
        a = run_ga(env, generations=15 if fast else 50, pop_size=30 if fast else 50, cx_prob=0.9, mut_prob=0.1)
    elif method == "hga":
        a = run_hga(env, generations=15 if fast else 50, pop_size=30 if fast else 50, cx_prob=0.9, mut_prob=0.1, ls_fraction=0.1)
    elif method == "pbig":
        a = run_pbig(env, iterations=50 if fast else 100, pop_size=15 if fast else 20, destruction_ratio=0.2)
    elif method == "max_sinr":
        a = max_sinr(env)
    elif method == "random":
        a = random_assignment(env)
    elif method == "random_no_repair":
        a = random_assoc_no_repair(env)
        m = compute_metrics(a, env)
        return a, m
    elif method == "random_rbm_lower_stat":
        a = random_assoc_no_repair(env)
        m = compute_metrics_lower(a, env, mode="stat")
        return a, m
    elif method == "random_rbm_lower_ls":
        a = random_assoc_no_repair(env)
        m = compute_metrics_lower(a, env, mode="ls")
        return a, m
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
    p.add_argument("--fast", action="store_true")
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
        a, m = run_method(env, mname, fast=args.fast)
        rows.append([mname, m["feasible"], int(m["total"]), round(m["jain"], 4), round(m["objective"], 2), args.users or env.I, args.beams or env.K])
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method","feasible","total_bps","jain","objective","users","beams"])
        for r in rows:
            w.writerow(r)

if __name__ == "__main__":
    main()
