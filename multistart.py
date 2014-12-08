# encoding=utf-8

import sys
from pyevolve import *
from tabulate import tabulate
from input_reader import *
from problem_utils import *
from multiprocessing import Process
from multiprocessing.queues import SimpleQueue


def genetic_algorithm(villains, characters, avg_villains_attributes, collaboration,
                      budget_enabled, budget_available, max_id, results):
    genome = G1DList.G1DList(len(villains))
    genome.evaluator.set(fitness(villains, characters, avg_villains_attributes, collaboration,
                                 budget_enabled, budget_available))
    genome.setParams(rangemin=0, rangemax=max_id)
    genome.mutator.set(Mutators.G1DListMutatorIntegerRange)

    ga = GSimpleGA.GSimpleGA(genome)
    ga.setGenerations(70 * len(villains))
    ga.setPopulationSize(50 * len(villains))
    ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)
    ga.evolve()
    result = ga.bestIndividual()
    results.put((list(result), result.getRawScore()))


def multistart(filename, results, budget_enabled=False):
    villains = read_villains(filename)
    characters = read_characters('characters.csv')

    collaboration = read_collaboration('characters_collaboration.csv', len(characters))
    heroes = [item for item in characters.values() if item['Hero or Villain'] == 'hero']
    avg_villains_attributes = avg_attributes(villains, characters)

    budget_available = budget(villains, characters) if budget_enabled else 0
    max_id = max([hero['Character ID'] for hero in heroes])

    threads = []
    queue = SimpleQueue()

    args = [villains, characters, avg_villains_attributes, collaboration,
            budget_enabled, budget_available, max_id, queue]

    # Multistart
    for idx in range(0, 10):
        thread = Process(target=genetic_algorithm, args=args)
        threads.append(thread)
        thread.start()

    solutions = [queue.get() for _ in threads]

    for thread in threads:
        thread.join()

    best_genome = solutions[0]
    for genome in solutions[1:]:
        if best_genome[1] < genome[1]:
            best_genome = genome

    instance = filename.split('/')[-1].rsplit('.')[0]

    avg_heroes_attributes = avg_attributes(best_genome[0], characters)
    if best_genome[1] == 0:
        if budget_enabled:
            results.append([instance, 0, 0, 0, 0, "HEROES TEAM NOT FOUND", 0, budget_available])
        else:
            results.append([instance, 0, 0, 0, 0, "HEROES TEAM NOT FOUND"])
    else:
        heroes_ids = sorted(best_genome[0])
        if budget_enabled:
            results.append([instance, avg_heroes_attributes[0], best_genome[1],
                            collaboration_score(heroes_ids, collaboration),
                            fighting_experience(heroes_ids, villains, collaboration),
                            heroes_ids, avg_heroes_attributes[2], budget_available])
        else:
            results.append([instance, avg_heroes_attributes[0], best_genome[1],
                            collaboration_score(heroes_ids, collaboration),
                            fighting_experience(heroes_ids, villains, collaboration), heroes_ids])


def main(args):
    if len(args) < 2:
        print 'You must provide a villains file and whether the budget restriction is enabled as parameter'
        exit(1)

    if args[1].lower() not in ['false', 'true']:
        print 'You must provide either "True" or "False" as the budget restriction parameter'
        exit(1)

    budget_enabled = args[1].lower() == 'true'

    headers = [u'Instância', u'Média Power Grid', u'Valor Solução', u'Colaboração',
               u'Experiência de Luta', u'Time de Heróis']
    if budget_enabled:
        headers += [u'Custo do Time', u'Budget disponível']

    data = []
    multistart(args[0], data, budget_enabled)

    print tabulate(data, headers=headers, tablefmt="pipe")


if __name__ == "__main__":
    main(sys.argv[1:])