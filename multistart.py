# encoding=utf-8

import sys
from pyevolve import *
from tabulate import tabulate
from input_reader import *
from problem_utils import *


def multistart(filename, results, budget_enabled=False):
    villains = read_villains(filename)
    characters = read_characters('characters.csv')

    collaboration = read_collaboration('characters_collaboration.csv', len(characters))
    heroes = [item for item in characters.values() if item['Hero or Villain'] == 'hero']
    avg_villains_attributes = avg_attributes(villains, characters)

    budget_available = budget(villains, characters) if budget_enabled else 0
    max_id = max([hero['Character ID'] for hero in heroes])

    best_genome = None

    # Multistart
    for idx in range(0, 10):
        genome = G1DList.G1DList(len(villains))
        genome.evaluator.set(fitness(villains, characters, avg_villains_attributes, collaboration,
                                     budget_enabled, budget_available))
        genome.setParams(rangemin=0, rangemax=max_id)
        genome.mutator.set(Mutators.G1DListMutatorIntegerRange)

        ga = GSimpleGA.GSimpleGA(genome)
        ga.setGenerations(50 * len(villains))
        ga.setPopulationSize(50 * len(villains))
        ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)
        ga.evolve()
        genome = ga.bestIndividual()

        if best_genome is None or best_genome.getRawScore() < genome.getRawScore():
            best_genome = genome

    instance = filename.split('/')[-1].rsplit('.')[0]

    avg_heroes_attributes = avg_attributes(list(best_genome), characters)
    if best_genome.getFitnessScore() == 0 or len(results) > 0:
        if budget_enabled:
            results.append([instance, 0, 0, 0, 0, "HEROES TEAM NOT FOUND", 0, budget_available])
        else:
            results.append([instance, 0, 0, 0, 0, "HEROES TEAM NOT FOUND"])
    else:
        heroes_ids = list(best_genome)
        if budget_enabled:
            results.append([instance, avg_heroes_attributes[0], best_genome.getRawScore(),
                            collaboration_score(heroes_ids, collaboration),
                            fighting_experience(heroes_ids, villains, collaboration),
                            heroes_ids, avg_heroes_attributes[2], budget_available])
        else:
            results.append([instance, avg_heroes_attributes[0], best_genome.getRawScore(),
                            collaboration_score(heroes_ids, collaboration),
                            fighting_experience(heroes_ids, villains, collaboration), heroes_ids])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'You must provide a villains file and whether the budget restriction is enabled as parameter'
        exit(1)

    if sys.argv[2].lower() not in ['false', 'true']:
        print 'You must provide either "True" or "False" as the budget restriction parameter'
        exit(1)

    budget_enabled = sys.argv[2].lower() == 'true'

    if budget_enabled:
        headers = [u'Instância', u'Média Power Grid', u'Valor Solução', u'Colaboração', u'Experiência de Luta',
                   u'Time de Heróis', u'Custo do Time', u'Budget disponível']
    else:
        headers = [u'Instância', u'Média Power Grid', u'Valor Solução', u'Colaboração',
                   u'Experiência de Luta', u'Time de Heróis']

    data = []
    multistart(sys.argv[1], data, budget_enabled)

    print tabulate(data, headers=headers, tablefmt="pipe")