import random
import math
from model import compute_metrics, repair_assignment

def greedy_assign(u_idx, a, env):
    best = None
    best_obj = float("-inf")
    for j in range(env.J):
        for k in range(env.K):
            cand = list(a)
            cand[u_idx] = (j, k)
            cand = repair_assignment(cand, env)
            m = compute_metrics(cand, env)
            if m["objective"] > best_obj:
                best_obj = m["objective"]
                best = cand
    return best

def run(env, iterations=100, pop_size=20, destruction_ratio=0.2):
    pop = []
    for _ in range(pop_size):
        a = [(random.randrange(env.J), random.randrange(env.K)) for _ in range(env.I)]
        a = repair_assignment(a, env)
        pop.append(a)
    for _ in range(iterations):
        idx = random.randrange(len(pop))
        base = list(pop[idx])
        m = int(max(1, destruction_ratio * len(base)))
        remove_idxs = random.sample(range(len(base)), m)
        for i in remove_idxs:
            base[i] = (random.randrange(env.J), random.randrange(env.K))
        base = repair_assignment(base, env)
        for i in remove_idxs:
            base = greedy_assign(i, base, env)
        old = pop[idx]
        m_new = compute_metrics(base, env)
        m_old = compute_metrics(old, env)
        if m_new["objective"] > m_old["objective"]:
            pop[idx] = base
    best = None
    best_obj = float("-inf")
    for a in pop:
        m = compute_metrics(a, env)
        if m["objective"] > best_obj:
            best_obj = m["objective"]
            best = a
    return best

def _deg2rad(d):
    return d * math.pi / 180.0
def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    dLat = _deg2rad(lat2 - lat1)
    dLon = _deg2rad(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(_deg2rad(lat1))*math.cos(_deg2rad(lat2))*math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
def _path_gain(d_m):
    fc_ghz = 3.5
    pl_db = 28.0 + 22.0 * math.log10(max(d_m, 1.0)) + 20.0 * math.log10(fc_ghz)
    return 10 ** (-pl_db / 10)
def _bearing(lat1, lon1, lat2, lon2):
    dLon = _deg2rad(lon2 - lon1)
    y = math.sin(dLon) * math.cos(_deg2rad(lat2))
    x = math.cos(_deg2rad(lat1)) * math.sin(_deg2rad(lat2)) - math.sin(_deg2rad(lat1)) * math.cos(_deg2rad(lat2)) * math.cos(dLon)
    b = math.atan2(y, x)
    if b < 0:
        b += 2 * math.pi
    return b
def _nearest_beam_index(theta, K):
    w = (2 * math.pi) / max(K, 1)
    k = int((theta + w / 2) // w) % K
    return k

def run_det(env):
    usage = [[0 for _ in range(env.K)] for _ in range(env.J)]
    a = []
    for i in range(env.I):
        ranks = []
        for j in range(env.J):
            d = _haversine(env.ue_pos[i][0], env.ue_pos[i][1], env.gnb_pos[j][0], env.gnb_pos[j][1])
            ranks.append((j, _path_gain(d)))
        ranks.sort(key=lambda x: x[1], reverse=True)
        placed = False
        for j, _ in ranks:
            theta = _bearing(env.gnb_pos[j][0], env.gnb_pos[j][1], env.ue_pos[i][0], env.ue_pos[i][1])
            k0 = _nearest_beam_index(theta, env.K)
            for dk in [0,1,-1,2,-2,3,-3]:
                k = (k0 + dk) % env.K
                if usage[j][k] + env.prb_per_user <= env.beam_prb_capacity[j][k]:
                    a.append((j, k))
                    usage[j][k] += env.prb_per_user
                    placed = True
                    break
            if placed:
                break
        if not placed:
            for j in range(env.J):
                for k in range(env.K):
                    if usage[j][k] + env.prb_per_user <= env.beam_prb_capacity[j][k]:
                        a.append((j, k))
                        usage[j][k] += env.prb_per_user
                        placed = True
                        break
                if placed:
                    break
        if not placed:
            j = 0
            k = 0
            a.append((j, k))
    return a

def run_hybrid(env, ls_budget=30, los_gain_thr=1e-9):
    base = run_det(env)
    improved = list(base)
    for i in range(env.I):
        j = improved[i][0]
        d = _haversine(env.ue_pos[i][0], env.ue_pos[i][1], env.gnb_pos[j][0], env.gnb_pos[j][1])
        if _path_gain(d) >= los_gain_thr:
            continue
        best = list(improved)
        best_m = compute_metrics(best, env)
        best_obj = best_m["objective"]
        for _ in range(ls_budget):
            jj = random.randrange(env.J)
            theta = _bearing(env.gnb_pos[jj][0], env.gnb_pos[jj][1], env.ue_pos[i][0], env.ue_pos[i][1])
            kk = _nearest_beam_index(theta, env.K)
            cand = list(improved)
            cand[i] = (jj, kk)
            cand = repair_assignment(cand, env)
            m = compute_metrics(cand, env)
            if m["objective"] > best_obj:
                best = cand
                best_obj = m["objective"]
        improved = best
    return improved
