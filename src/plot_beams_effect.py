import argparse
from compare import run_method
from env import load_config, Environment
import matplotlib.pyplot as plt
import numpy as np

def gather_totals(cfg_base, users, beams, methods):
    cfg = dict(cfg_base)
    cfg["users_min"] = users
    cfg["beams_per_cell"] = beams
    env = Environment(cfg)
    totals = {}
    for m in methods:
        _, met = run_method(env, m)
        totals[m] = met["total"]/1e6
    return totals

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--users", type=int, default=60)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    methods = ["hga","pbig","ga","max_sinr"]
    cfg_base = load_config(args.config)
    totals_b8 = gather_totals(cfg_base, args.users, 8, methods)
    totals_b16 = gather_totals(cfg_base, args.users, 16, methods)
    labels = [m.upper() if m!="max_sinr" else "Max-SINR" for m in methods]
    x = np.arange(len(methods))
    w = 0.35
    plt.figure(figsize=(8,5))
    plt.bar(x - w/2, [totals_b8[m] for m in methods], width=w, label="8 Hüzme", color="#64748b")
    plt.bar(x + w/2, [totals_b16[m] for m in methods], width=w, label="16 Hüzme", color="#3b82f6")
    plt.xticks(x, labels)
    plt.ylabel("Sistem Toplam Veri Hızı (Mbps)")
    plt.xlabel("Algoritmalar")
    plt.title("Hüzme Sayısının Etkisi (Users={})".format(args.users))
    plt.grid(True, axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.out)

if __name__ == "__main__":
    main()
