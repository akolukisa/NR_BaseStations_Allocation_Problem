import csv
from env import load_config, Environment
from model import compute_metrics
from algorithms.ga import run as run_ga
from algorithms.hga import run as run_hga
from algorithms.pbig import run as run_pbig
from algorithms.baselines import max_sinr, random_assignment

def run_method(env, name):
    if name == "hga":
        a = run_hga(env, generations=15, pop_size=30, cx_prob=0.9, mut_prob=0.1, ls_fraction=0.1)
    elif name == "pbig":
        a = run_pbig(env, iterations=50, pop_size=15, destruction_ratio=0.2)
    elif name == "ga":
        a = run_ga(env, generations=15, pop_size=30, cx_prob=0.9, mut_prob=0.1)
    elif name == "max_sinr":
        a = max_sinr(env)
    elif name == "random":
        a = random_assignment(env)
    else:
        a = max_sinr(env)
    m = compute_metrics(a, env)
    return m

def write_table(users, beams, out):
    cfg = load_config("configs/simulation.json")
    cfg["users_min"] = users
    cfg["beams_per_cell"] = beams
    env = Environment(cfg)
    methods = ["hga","pbig","ga","max_sinr","random"]
    rows = []
    for name in methods:
        m = run_method(env, name)
        rows.append([name, m["feasible"], round(m["total"]/1e6, 2), round(m["jain"], 4), round(m["objective"], 2), users, beams])
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method","feasible","total_Mbps","jain","objective","users","beams"]) 
        for r in rows:
            w.writerow(r)

def main():
    for u in [20, 60, 100]:
        out = f"results/table_u{u}_b8.csv"
        write_table(u, 8, out)

if __name__ == "__main__":
    main()
