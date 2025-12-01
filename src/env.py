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
        self.prb_bw_hz = config.get("prb_bandwidth_hz", 180000)
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
        self.center_lat = config.get("center_lat", 38.43)
        self.center_lon = config.get("center_lon", 27.20)
        self.seed = config.get("seed", 42)
        random.seed(self.seed)
        self.gnb_pos = self._generate_gnb_positions(self.J, self.center_lat, self.center_lon)
        self.ue_pos = self._generate_ue_positions(self.I, self.gnb_pos)
        self.H = []
        for i in range(self.I):
            rowj = []
            for j in range(self.J):
                dist = self._haversine(self.ue_pos[i][0], self.ue_pos[i][1], self.gnb_pos[j][0], self.gnb_pos[j][1])
                gains = [self._path_gain(dist) * self._shadow() * self._rayleigh() for _ in range(self.K)]
                rowj.append(gains)
            self.H.append(rowj)

    def _deg2rad(self, d):
        return d * math.pi / 180.0
    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000.0
        dLat = self._deg2rad(lat2 - lat1)
        dLon = self._deg2rad(lon2 - lon1)
        a = math.sin(dLat/2)**2 + math.cos(self._deg2rad(lat1))*math.cos(self._deg2rad(lat2))*math.sin(dLon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    def _meters_to_deg(self, lat, mLat, mLon):
        dLat = mLat / 111320.0
        dLon = mLon / (111320.0 * math.cos(self._deg2rad(lat)))
        return dLat, dLon
    def _path_gain(self, d_m):
        fc_ghz = 3.5
        pl_db = 28.0 + 22.0 * math.log10(max(d_m, 1.0)) + 20.0 * math.log10(fc_ghz)
        return 10 ** (-pl_db / 10)
    def _shadow(self):
        shadow_db = random.gauss(0, 4)
        return 10 ** (shadow_db / 10)
    def _rayleigh(self):
        return random.expovariate(1.0)
    def _generate_gnb_positions(self, J, lat0, lon0):
        positions = []
        positions.append((lat0, lon0))
        if J == 1:
            return positions
        r = 3500.0
        angles = [0, 60, 120, 180, 240, 300]
        for a in angles:
            dLat, dLon = self._meters_to_deg(lat0, r * math.cos(self._deg2rad(a)), r * math.sin(self._deg2rad(a)))
            positions.append((lat0 + dLat, lon0 + dLon))
            if len(positions) == J:
                break
        return positions[:J]
    def _generate_ue_positions(self, I, gnb_pos):
        positions = []
        min_lat, max_lat = 38.20, 38.70
        min_lon, max_lon = 26.90, 27.50
        for _ in range(I):
            for _try in range(1000):
                gj = random.randrange(len(gnb_pos))
                r = random.random() * 7000.0
                theta = random.random() * 360.0
                dLat, dLon = self._meters_to_deg(gnb_pos[gj][0], r * math.cos(self._deg2rad(theta)), r * math.sin(self._deg2rad(theta)))
                lat = gnb_pos[gj][0] + dLat
                lon = gnb_pos[gj][1] + dLon
                if lat < min_lat or lat > max_lat or lon < min_lon or lon > max_lon:
                    continue
                ok = True
                for j in range(len(gnb_pos)):
                    d = self._haversine(lat, lon, gnb_pos[j][0], gnb_pos[j][1])
                    if d > 7000.0:
                        ok = False
                        break
                if not ok:
                    continue
                positions.append((lat, lon))
                break
        if len(positions) < I:
            positions += [(gnb_pos[0][0], gnb_pos[0][1])] * (I - len(positions))
        return positions

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)
