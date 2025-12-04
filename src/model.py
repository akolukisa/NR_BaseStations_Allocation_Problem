import math

def compute_metrics(assignment, env):
    def deg2rad(d):
        return d * math.pi / 180.0
    def bearing(lat1, lon1, lat2, lon2):
        dLon = deg2rad(lon2 - lon1)
        y = math.sin(dLon) * math.cos(deg2rad(lat2))
        x = math.cos(deg2rad(lat1)) * math.sin(deg2rad(lat2)) - math.sin(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.cos(dLon)
        b = math.atan2(y, x)
        if b < 0:
            b += 2 * math.pi
        return b
    def beam_center(k, K):
        return (2 * math.pi * k) / max(K, 1)
    def pattern_gain(delta, sharp):
        d = abs((delta + math.pi) % (2 * math.pi) - math.pi)
        return max(0.0, math.cos(d)) ** max(1, int(sharp))
    beams_usage = [[0 for _ in range(env.K)] for _ in range(env.J)]
    for i, (j, k) in enumerate(assignment):
        beams_usage[j][k] += env.prb_per_user
    feasible = True
    for j in range(env.J):
        total_power = sum(env.p_jk[j])
        if total_power > env.p_jmax + 1e-9:
            feasible = False
        for k in range(env.K):
            if beams_usage[j][k] > env.beam_prb_capacity[j][k]:
                feasible = False
    rates = []
    sll_pen = 0.0
    for i, (j, k) in enumerate(assignment):
        theta = bearing(env.gnb_pos[j][0], env.gnb_pos[j][1], env.ue_pos[i][0], env.ue_pos[i][1])
        theta0 = beam_center(k, env.K)
        pg = pattern_gain(theta - theta0, env.beam_sharpness)
        num = env.p_jk[j][k] * env.H[i][j][k]
        interf = 0.0
        for jj in range(env.J):
            for kk in range(env.K):
                if jj == j and kk == k:
                    continue
                t = bearing(env.gnb_pos[jj][0], env.gnb_pos[jj][1], env.ue_pos[i][0], env.ue_pos[i][1])
                t0 = beam_center(kk, env.K)
                pg_i = pattern_gain(t - t0, env.beam_sharpness)
                interf += env.p_jk[jj][kk] * env.H[i][jj][kk] * pg_i
        sinr = (num * pg) / (interf + env.noise_power_w + 1e-30)
        bps = env.prb_per_user * env.prb_bw_hz * env.dl_fraction * math.log2(1.0 + sinr)
        if bps < env.qos_min_bps:
            feasible = False
        rates.append(max(bps, 0.0))
        if abs(((theta - theta0) + math.pi) % (2 * math.pi) - math.pi) > env.main_lobe_width_rad:
            sll_pen += pg
    total = sum(rates)
    denom = len(rates) * sum(r * r for r in rates)
    jain = 0.0
    if denom > 0:
        jain = (total * total) / denom
    f = (1.0 - env.alpha) * total + env.alpha * jain * total - env.beta_sll * sll_pen
    return {
        "feasible": feasible,
        "rates": rates,
        "total": total,
        "jain": jain,
        "objective": f
    }

def repair_assignment(assignment, env):
    usage = [[0 for _ in range(env.K)] for _ in range(env.J)]
    repaired = list(assignment)
    for i, (j, k) in enumerate(assignment):
        if usage[j][k] + env.prb_per_user <= env.beam_prb_capacity[j][k]:
            usage[j][k] += env.prb_per_user
            continue
        best = None
        best_rate = -1.0
        for jj in range(env.J):
            for kk in range(env.K):
                if usage[jj][kk] + env.prb_per_user > env.beam_prb_capacity[jj][kk]:
                    continue
                def bearing(lat1, lon1, lat2, lon2):
                    dLon = (lon2 - lon1) * math.pi / 180.0
                    y = math.sin(dLon) * math.cos(lat2 * math.pi / 180.0)
                    x = math.cos(lat1 * math.pi / 180.0) * math.sin(lat2 * math.pi / 180.0) - math.sin(lat1 * math.pi / 180.0) * math.cos(lat2 * math.pi / 180.0) * math.cos(dLon)
                    b = math.atan2(y, x)
                    if b < 0:
                        b += 2 * math.pi
                    return b
                def beam_center(k, K):
                    return (2 * math.pi * k) / max(K, 1)
                def pattern_gain(delta, sharp):
                    d = abs((delta + math.pi) % (2 * math.pi) - math.pi)
                    return max(0.0, math.cos(d)) ** max(1, int(sharp))
                theta = bearing(env.gnb_pos[jj][0], env.gnb_pos[jj][1], env.ue_pos[i][0], env.ue_pos[i][1])
                theta0 = beam_center(kk, env.K)
                pg = pattern_gain(theta - theta0, env.beam_sharpness)
                num = env.p_jk[jj][kk] * env.H[i][jj][kk] * pg
                interf = 0.0
                for jjj in range(env.J):
                    for kkk in range(env.K):
                        if jjj == jj and kkk == kk:
                            continue
                        t = bearing(env.gnb_pos[jjj][0], env.gnb_pos[jjj][1], env.ue_pos[i][0], env.ue_pos[i][1])
                        t0 = beam_center(kkk, env.K)
                        pg_i = pattern_gain(t - t0, env.beam_sharpness)
                        interf += env.p_jk[jjj][kkk] * env.H[i][jjj][kkk] * pg_i
                sinr = num / (interf + env.noise_power_w + 1e-30)
                rate = env.prb_per_user * env.prb_bw_hz * env.dl_fraction * math.log2(1.0 + sinr)
                if rate > best_rate:
                    best_rate = rate
                    best = (jj, kk)
        if best is None:
            best = (j, k)
        repaired[i] = best
        usage[best[0]][best[1]] += env.prb_per_user
    return repaired

def compute_metrics_lower(assignment, env, mode="stat"):
    def deg2rad(d):
        return d * math.pi / 180.0
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000.0
        dLat = deg2rad(lat2 - lat1)
        dLon = deg2rad(lon2 - lon1)
        a = math.sin(dLat/2)**2 + math.cos(deg2rad(lat1))*math.cos(deg2rad(lat2))*math.sin(dLon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    def path_gain(d_m):
        fc_ghz = 3.5
        pl_db = 28.0 + 22.0 * math.log10(max(d_m, 1.0)) + 20.0 * math.log10(fc_ghz)
        return 10 ** (-pl_db / 10)
    beams_usage = [[0 for _ in range(env.K)] for _ in range(env.J)]
    for i, (j, k) in enumerate(assignment):
        beams_usage[j][k] += env.prb_per_user
    feasible = True
    for j in range(env.J):
        total_power = sum(env.p_jk[j])
        if total_power > env.p_jmax + 1e-9:
            feasible = False
        for k in range(env.K):
            if beams_usage[j][k] > env.beam_prb_capacity[j][k]:
                feasible = False
    rates = []
    for i, (j, k) in enumerate(assignment):
        d0 = haversine(env.ue_pos[i][0], env.ue_pos[i][1], env.gnb_pos[j][0], env.gnb_pos[j][1])
        g_sig = path_gain(d0)
        num = env.p_jk[j][k] * g_sig
        interf = 0.0
        if mode == "stat":
            interf = 0.0
        elif mode == "ls":
            for jj in range(env.J):
                for kk in range(env.K):
                    if jj == j and kk == k:
                        continue
                    dI = haversine(env.ue_pos[i][0], env.ue_pos[i][1], env.gnb_pos[jj][0], env.gnb_pos[jj][1])
                    interf += env.p_jk[jj][kk] * path_gain(dI)
        sinr = num / (interf + env.noise_power_w + 1e-30)
        bps = env.prb_per_user * env.prb_bw_hz * env.dl_fraction * math.log2(1.0 + sinr)
        if bps < env.qos_min_bps:
            feasible = False
        rates.append(max(bps, 0.0))
    total = sum(rates)
    denom = len(rates) * sum(r * r for r in rates)
    jain = 0.0
    if denom > 0:
        jain = (total * total) / denom
    f = (1.0 - env.alpha) * total + env.alpha * jain * total
    return {
        "feasible": feasible,
        "rates": rates,
        "total": total,
        "jain": jain,
        "objective": f
    }
