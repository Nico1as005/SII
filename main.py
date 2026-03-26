import random
import matplotlib.pyplot as plt
from deap import base, creator, tools

N_FIELDS = 8
K_CROPS = 5

# урожай поле культура
yield_table = [
    [3, 5, 2, 6, 4],
    [4, 3, 5, 2, 6],
    [5, 4, 3, 6, 2],
    [2, 6, 4, 5, 3],
    [6, 2, 3, 4, 5],
    [3, 4, 6, 2, 5],
    [5, 3, 6, 4, 2],
    [4, 2, 5, 6, 3]
]

# стоимость каждой культуры
crop_costs = [100, 130, 150, 110, 90]

def evaluate(individual):
    total_yield = 0
    total_cost = 0

    for field_index, crop_index in enumerate(individual):
        total_yield += yield_table[field_index][crop_index]
        total_cost += crop_costs[crop_index]

    W_yield = 1.0
    W_cost = 0.3

    fitness = -W_yield * total_yield + W_cost * total_cost
    return (fitness,)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

toolbox.register("attr_crop", random.randint, 0, K_CROPS - 1)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_crop, n=N_FIELDS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
toolbox.register("select", tools.selTournament, tournsize=3)

def mut_swap(ind):
    #Меняет местами культуры двух случайных полей
    i, j = random.sample(range(len(ind)), 2)
    ind[i], ind[j] = ind[j], ind[i]
    return (ind,)


def mut_shift(ind):
    #Сдвигает культуру на +1 по модулю K_CROPS
    for i in range(len(ind)):
        if random.random() < 0.1:
            ind[i] = (ind[i] + 1) % K_CROPS
    return (ind,)


mutations = {
    "MutRandom 20%": lambda ind: tools.mutUniformInt(
        ind, 0, K_CROPS - 1, indpb=0.2
    ),
    "MutSwap": mut_swap,
    "MutShift": mut_shift,
}

crossovers = {
    "Одноточечное": tools.cxOnePoint,
    "Двухточечное": tools.cxTwoPoint,
    "Равномерное": lambda ind1, ind2: tools.cxUniform(ind1, ind2, indpb=0.5)
}

POP_SIZE = 60
GENERATIONS = 80
CXPB = 0.8
MUTPB = 0.2

results = {}

for cx_name, cx_op in crossovers.items():
    for mut_name, mut_op in mutations.items():

        toolbox.register("mate", cx_op)
        toolbox.register("mutate", mut_op)

        population = toolbox.population(n=POP_SIZE)

        for ind in population:
            ind.fitness.values = toolbox.evaluate(ind)

        best_history = []

        for gen in range(GENERATIONS):
            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))

            # скрещивание
            for c1, c2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < CXPB:
                    toolbox.mate(c1, c2)
                    del c1.fitness.values
                    del c2.fitness.values

            # мутация
            for mutant in offspring:
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid = [ind for ind in offspring if not ind.fitness.valid]
            for ind in invalid:
                ind.fitness.values = toolbox.evaluate(ind)

            population[:] = offspring
            best = min(ind.fitness.values[0] for ind in population)
            best_history.append(best)

        results[f"{cx_name} + {mut_name}"] = best_history

plt.figure(figsize=(13, 8))
for label, history in results.items():
    plt.plot(history, label=label)

plt.xlabel("Поколение")
plt.ylabel("Fitness")
plt.title("Сравнение")
plt.legend(fontsize=8)
plt.grid()
plt.show()