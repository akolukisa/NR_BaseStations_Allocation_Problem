import random
from model import compute_metrics, repair_assignment

def random_feasible(env):
    usage = [[0 for _ in range(env.K)] for _ in range(env.J)]
    a = []
    for i in range(env.I):
        choices = []
        for j in range(env.J):
            for k in range(env.K):
                if usage[j][k] + env.prb_per_user <= env.beam_prb_capacity[j][k]:
                    choices.append((j, k))
        if not choices:
            j = random.randrange(env.J)
            k = random.randrange(env.K)
            a.append((j, k))
            continue
        sel = random.choice(choices)
        a.append(sel)
        usage[sel[0]][sel[1]] += env.prb_per_user
    return a

def fitness(a, env):
    m = compute_metrics(a, env)
    if not m["feasible"]:
        return m["objective"] * 0.5
    return m["objective"]

def select(pop, fits):
    s = sum(fits)
    if s <= 0:
        return random.choice(pop)
    r = random.random() * s
    acc = 0.0
    for i, f in enumerate(fits):
        acc += f
        if acc >= r:
            return pop[i]
    return pop[-1]

def crossover(p1, p2):
    n = len(p1)
    if n == 0:
        return p1, p2
    cut = random.randrange(n)
    c1 = p1[:cut] + p2[cut:]
    c2 = p2[:cut] + p1[cut:]
    return c1, c2

def mutate(a, env, rate):
    b = list(a)
    for i in range(len(b)):
        if random.random() < rate:
            j = random.randrange(env.J)
            k = random.randrange(env.K)
            b[i] = (j, k)
    return repair_assignment(b, env)

def run(env, generations=50, pop_size=50, cx_prob=0.9, mut_prob=0.1):
    pop = [random_feasible(env) for _ in range(pop_size)]
    best = None
    best_fit = float("-inf")
    for _ in range(generations):
        fits = [fitness(a, env) for a in pop]
        new_pop = []
        for _ in range(pop_size // 2):
            p1 = select(pop, fits)
            p2 = select(pop, fits)
            c1, c2 = (p1, p2)
            if random.random() < cx_prob:
                c1, c2 = crossover(p1, p2)
            c1 = mutate(c1, env, mut_prob)
            c2 = mutate(c2, env, mut_prob)
            new_pop.append(c1)
            new_pop.append(c2)
        pop = new_pop
        for a in pop:
            f = fitness(a, env)
            if f > best_fit:
                best_fit = f
                best = a
    return best
