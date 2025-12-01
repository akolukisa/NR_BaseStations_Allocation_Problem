import random
from model import compute_metrics, repair_assignment
from algorithms.ga import random_feasible, fitness, select, crossover, mutate

def local_search(a, env, budget=50):
    best = list(a)
    best_fit = fitness(best, env)
    for _ in range(budget):
        i = random.randrange(len(best))
        j = random.randrange(env.J)
        k = random.randrange(env.K)
        cand = list(best)
        cand[i] = (j, k)
        cand = repair_assignment(cand, env)
        f = fitness(cand, env)
        if f > best_fit:
            best = cand
            best_fit = f
    return best

def run(env, generations=50, pop_size=50, cx_prob=0.9, mut_prob=0.1, ls_fraction=0.1):
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
        k = max(1, int(ls_fraction * len(new_pop)))
        idxs = random.sample(range(len(new_pop)), k)
        for idx in idxs:
            new_pop[idx] = local_search(new_pop[idx], env)
        pop = new_pop
        for a in pop:
            f = fitness(a, env)
            if f > best_fit:
                best_fit = f
                best = a
    return best
