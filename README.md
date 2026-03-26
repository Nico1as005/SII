# SII_Lab1
# Вариант 10
На языке Python разработайте скрипт, который с помощью генетического алгоритма и полного перебора решает следующую задачу.
Дано N полей для и k культур для посева. Для каждого поля известна характеристика урожайности каждой из k культур, а для каждой культуры – его закупочная стоимость.
Необходимо получить самый лучший урожай за наименьшую стоимость.
# Загружаем необходимые библиотеки
```
import random
import matplotlib.pyplot as plt
from deap import base, creator, tools
```
DEAP - библиотека для работы с генетическим алгоритмом
# Константы, таблица урожая и стоимость
```
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

crop_costs = [100, 130, 150, 110, 90]
```
Константы определяют количество полей и культур.
Таблица отвечает за распределение культур по полям
# Функция оценки
```
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
```
Считает стоимость культур и чистую прибыль от них.
Высчитывает фитнес, показывающий выгоду от полученного урожая.
Чем ниже фитнес, тем больше выгода, чем меньше выгода, тем больше фитнес.
# Создание классов DEAP
```
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)
```
Оптимизация к минимуму
# Toolbox
```
toolbox = base.Toolbox()

toolbox.register("attr_crop", random.randint, 0, K_CROPS - 1)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_crop, n=N_FIELDS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
toolbox.register("select", tools.selTournament, tournsize=3)
```
Отвечает за генерацию и операции с генетическим алгоритмом.
Создается атрибут культура на поле
Индивид состоит из 8 культур
Популяция. Состоит из индивидов
Оцнека и селекция
# Мутации
```
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
```
Мутация в генетическом алгоритме — это оператор,
который случайным образом изменяет часть особи (решения),
создавая новые варианты и обеспечивая генетическое разнообразие популяции.
Представлены в данном коде тремя видами:
1. Обмен культур между двумя полями
2. Сдвиг культур по полям
3. Случайная мутация. С шансом в 20% культура на поле будет заменена
# Скрещивания
```
crossovers = {
    "Одноточечное": tools.cxOnePoint,
    "Двухточечное": tools.cxTwoPoint,
    "Равномерное": lambda ind1, ind2: tools.cxUniform(ind1, ind2, indpb=0.5)
}
```
Скрещивание (кроссовер) в генетическом алгоритме — это оператор, который создаёт новых особей,
комбинируя гены двух родительских решений.
Представлены тремя видами:
1. Одноточечное
2. Двухточечное
3. Равномерное
# Эксперимент
```
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
```
Для каждой итерации (поколения)
Проводится мутация и кроссовер.
Итого представлено 9 вариантов развития генетического алгоритма.
На основе результатов строятся графики.
