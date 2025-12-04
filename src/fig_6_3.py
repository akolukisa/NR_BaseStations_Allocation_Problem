import csv
from env import load_config, Environment
from model import compute_metrics
from algorithms.ga import run as run_ga
from algorithms.hga import run as run_hga
from algorithms.pbig import run as run_pbig
from algorithms.baselines import max_sinr, random_assignment

def run_all(env):
    rows = []
    a = run_hga(env, generations=15, pop_size=30, cx_prob=0.9, mut_prob=0.1, ls_fraction=0.1)
    m = compute_metrics(a, env)
    rows.append(("HGA", m["total"]))
    a = run_pbig(env, iterations=50, pop_size=15, destruction_ratio=0.2)
    m = compute_metrics(a, env)
    rows.append(("PBIG", m["total"]))
    a = run_ga(env, generations=15, pop_size=30, cx_prob=0.9, mut_prob=0.1)
    m = compute_metrics(a, env)
    rows.append(("GA", m["total"]))
    a = max_sinr(env)
    m = compute_metrics(a, env)
    rows.append(("Max-SINR", m["total"]))
    a = random_assignment(env)
    m = compute_metrics(a, env)
    rows.append(("Random", m["total"]))
    return rows

def main():
    cfg = load_config("configs/simulation.json")
    cfg["users_min"] = 60
    out = "results/fig_6_3.csv"
    cfg8 = dict(cfg)
    cfg16 = dict(cfg)
    cfg8["beams_per_cell"] = 8
    cfg16["beams_per_cell"] = 16
    env8 = Environment(cfg8)
    env16 = Environment(cfg16)
    rows8 = run_all(env8)
    rows16 = run_all(env16)
    m8 = {name: total for name, total in rows8}
    m16 = {name: total for name, total in rows16}
    methods = ["HGA","PBIG","GA","Max-SINR","Random"]
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method","beams_8_mbps","beams_16_mbps"]) 
        for name in methods:
            w.writerow([name, int(m8[name]/1e6), int(m16[name]/1e6)])

if __name__ == "__main__":
    main()
