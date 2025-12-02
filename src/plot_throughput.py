import argparse
from compare import run_method
from env import load_config, Environment
import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--methods", default="ga,hga,pbig,max_sinr,random")
    p.add_argument("--beams", type=int, required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    users = [10,20,30,40,50,60,70,80,90,100]
    series = {m: [] for m in methods}
    for u in users:
        cfg = load_config(args.config)
        cfg["users_min"] = u
        cfg["beams_per_cell"] = args.beams
        env = Environment(cfg)
        for m in methods:
            _, met = run_method(env, m)
            series[m].append(met["total"] / 1e6)
    plt.figure(figsize=(8,5))
    palette = {
        "hga": "#22c55e",
        "pbig": "#3b82f6",
        "ga": "#f59e0b",
        "max_sinr": "#ef4444",
        "random": "#64748b"
    }
    for m in methods:
        plt.plot(users, series[m], label=m.upper() if m!="max_sinr" else "Max-SINR", color=palette.get(m, None), marker="o")
    plt.title("Sistem Toplam Veri Hızı (Beams={})".format(args.beams))
    plt.xlabel("Kullanıcı Sayısı")
    plt.ylabel("Sistem Toplam Veri Hızı (Mbps)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.out)

if __name__ == "__main__":
    main()
