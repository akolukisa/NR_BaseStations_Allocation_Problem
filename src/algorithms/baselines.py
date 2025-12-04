import random
import math
from model import repair_assignment

def max_sinr(env):
    a = []
    usage = [[0 for _ in range(env.K)] for _ in range(env.J)]
    for i in range(env.I):
        best = None
        best_val = float("-inf")
        for j in range(env.J):
            for k in range(env.K):
                num = env.p_jk[j][k] * env.H[i][j][k]
                interf = 0.0
                for jj in range(env.J):
                    for kk in range(env.K):
                        if jj == j and kk == k:
                            continue
                        interf += env.p_jk[jj][kk] * env.H[i][jj][kk]
                sinr = num / (interf + env.noise_power_w + 1e-30)
                if usage[j][k] + env.prb_per_user > env.beam_prb_capacity[j][k]:
                    continue
                if sinr > best_val:
                    best_val = sinr
                    best = (j, k)
        if best is None:
            j = random.randrange(env.J)
            k = random.randrange(env.K)
            best = (j, k)
        a.append(best)
        usage[best[0]][best[1]] += env.prb_per_user
    return repair_assignment(a, env)

def random_assignment(env):
    a = [(random.randrange(env.J), random.randrange(env.K)) for _ in range(env.I)]
    return repair_assignment(a, env)

def random_assoc_no_repair(env):
    return [(random.randrange(env.J), random.randrange(env.K)) for _ in range(env.I)]
