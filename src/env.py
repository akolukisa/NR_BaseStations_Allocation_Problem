import json
import math
import random

class Environment:
    def __init__(self, config):
        self.J = config.get("gnb_count", 7)
        self.K = config.get("beams_per_cell", 8)
        self.I = config.get("users_min", 10)
        self.prb_per_beam = config.get("prb_per_beam", 100)
        self.prb_per_user = config.get("prb_per_user", 4)
        self.noise_power_w = config.get("noise_power_w", 3.98107e-13)
        self.alpha = config.get("alpha", 0.3)
        self.qos_min_bps = config.get("qos_min_bps", 1000000)
        self.p_jmax = config.get("gnb_tx_power_w", 39.810717)
        self.p_jk = [[self.p_jmax / self.K for _ in range(self.K)] for _ in range(self.J)]
        self.beam_prb_capacity = [[self.prb_per_beam for _ in range(self.K)] for _ in range(self.J)]
        ratio = config.get("dl_ul_ratio", [4,1])
        dl = ratio[0] if isinstance(ratio, list) and len(ratio) >= 1 else 4
        ul = ratio[1] if isinstance(ratio, list) and len(ratio) >= 2 else 1
        self.dl_fraction = dl / max(dl + ul, 1)
        self.seed = config.get("seed", 42)
        random.seed(self.seed)
        self.H = [[[self._sample_channel_gain(i, j, k) for k in range(self.K)] for j in range(self.J)] for i in range(self.I)]

    def _sample_channel_gain(self, i, j, k):
        d = 100 + 10 * ((i + j + k) % 10)
        fc_ghz = 3.5
        pl_db = 28.0 + 22.0 * math.log10(max(d, 1)) + 20.0 * math.log10(fc_ghz)
        pl_lin = 10 ** (-pl_db / 10)
        shadow_db = random.gauss(0, 4)
        shadow_lin = 10 ** (shadow_db / 10)
        rayleigh = random.expovariate(1.0)
        return pl_lin * shadow_lin * rayleigh

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)
