import csv
from env import load_config, Environment
from model import compute_metrics
from algorithms.ga import run as run_ga
from algorithms.hga import run as run_hga
from algorithms.pbig import run as run_pbig
from algorithms.baselines import max_sinr, random_assignment

def run_methods(env):
    rows = []
    a = run_hga(env, generations=15, pop_size=30, cx_prob=0.9, mut_prob=0.1, ls_fraction=0.1)
    m = compute_metrics(a, env)
    rows.append(("hga", m["jain"]))
    a = run_pbig(env, iterations=50, pop_size=15, destruction_ratio=0.2)
    m = compute_metrics(a, env)
    rows.append(("pbig", m["jain"]))
    a = run_ga(env, generations=15, pop_size=30, cx_prob=0.9, mut_prob=0.1)
    m = compute_metrics(a, env)
    rows.append(("ga", m["jain"]))
    a = max_sinr(env)
    m = compute_metrics(a, env)
    rows.append(("max_sinr", m["jain"]))
    a = random_assignment(env)
    m = compute_metrics(a, env)
    rows.append(("random", m["jain"]))
    return rows

def main():
    cfg = load_config("configs/simulation.json")
    cfg["beams_per_cell"] = 8
    users = list(range(10, 110, 10))
    out = "results/fig_6_2.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["users","hga","pbig","ga","max_sinr","random"]) 
        for u in users:
            cfg["users_min"] = u
            env = Environment(cfg)
            rows = run_methods(env)
            vals = {name: val for name, val in rows}
            w.writerow([u] + [round(vals[name], 4) for name in ["hga","pbig","ga","max_sinr","random"]])

if __name__ == "__main__":
    main()
