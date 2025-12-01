import math

def compute_metrics(assignment, env):
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
        num = env.p_jk[j][k] * env.H[i][j][k]
        interf = 0.0
        for jj in range(env.J):
            for kk in range(env.K):
                if jj == j and kk == k:
                    continue
                interf += env.p_jk[jj][kk] * env.H[i][jj][kk]
        sinr = num / (interf + env.noise_power_w + 1e-30)
        bps = env.prb_per_user * 180000 * env.dl_fraction * math.log2(1.0 + sinr)
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
                num = env.p_jk[jj][kk] * env.H[i][jj][kk]
                interf = 0.0
                for jjj in range(env.J):
                    for kkk in range(env.K):
                        if jjj == jj and kkk == kk:
                            continue
                        interf += env.p_jk[jjj][kkk] * env.H[i][jjj][kkk]
                sinr = num / (interf + env.noise_power_w + 1e-30)
                rate = env.prb_per_user * 180000 * env.dl_fraction * math.log2(1.0 + sinr)
                if rate > best_rate:
                    best_rate = rate
                    best = (jj, kk)
        if best is None:
            best = (j, k)
        repaired[i] = best
        usage[best[0]][best[1]] += env.prb_per_user
    return repaired
