import random
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
