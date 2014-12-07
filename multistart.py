import csv
import sys
from pyevolve import *


def proccess_row(row):
    result = {}
    for key, value in row.iteritems():
        try:
            result[key] = int(value)
        except ValueError:
            result[key] = value
    return result


def read_characters(filename):
    characters = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            character = proccess_row(row)
            characters[character['Character ID']] = character
    return characters


def read_collaboration(filename, size):
    collaboration = [[0 for x in range(size)] for x in range(size)]
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            row = proccess_row(row)
            value = row['Number of Comic Books Where Character 1 and Character 2 Both Appeared']
            collaboration[row['Character 1 ID'] - 1][row['Character 2 ID'] - 1] = value
    return collaboration


def read_villains(filename):
    villains = []
    with open(filename) as f:
        for row in f.readlines():
            villains += [int(x) for x in row.split(' ')]
    return villains


def powergrid_keys():
    return ['Intelligence','Strength', 'Speed', 'Durability', 'Energy Projection', 'Fighting Skills']


def avg_attributes(characters_ids, all_characters):
    sum_power_grid = 0
    sum_popularity = 0
    vt_cost = 0
    keys = powergrid_keys()
    for characters_id in characters_ids:
        character = all_characters[characters_id]
        local_sum = 0
        for key in keys:
            local_sum += character[key]
        sum_popularity += character['Number of Comic Books Where Character Appeared']
        sum_power_grid += local_sum
        vt_cost += character['Number of Comic Books Where Character Appeared'] * float(local_sum) / len(keys)

    qtd = len(characters_ids)
    avg_power_grid = float(sum_power_grid) / len(keys) / qtd
    avg_popularity = float(sum_popularity) / qtd
    return avg_power_grid, avg_popularity, vt_cost


def budget(villains_ids, all_characters):
    heroes_ids = []
    all_villains_ids = []
    for character in all_characters.values():
        if character['Hero or Villain'] == 'hero':
            heroes_ids.append(character['Character ID'])
        else:
            all_villains_ids.append(character['Character ID'])

    avg_villains_attributes = avg_attributes(villains_ids, all_characters)
    avg_all_villains_attributes = avg_attributes(all_villains_ids, all_characters)
    avg_heroes_attributes = avg_attributes(heroes_ids, all_characters)
    ratio_pg = avg_heroes_attributes[0] / avg_villains_attributes[0]
    ratio_pop = avg_heroes_attributes[1] / avg_villains_attributes[1]
    vt_cost = avg_villains_attributes[2]

    expr1 = ratio_pg * ratio_pop * vt_cost

    factor = avg_villains_attributes[0] / avg_all_villains_attributes[0]
    avg_pg = avg_heroes_attributes[0]
    avg_pop = avg_heroes_attributes[1]
    vt_size = len(villains_ids)

    expr2 = factor * avg_pg * avg_pop * vt_size

    return max(expr1, expr2)


def collaboration_score(heroes_ids, villains_id, collaboration):
    score = 0
    for i, character_id in enumerate(heroes_ids):
        for j in range(i+1, len(heroes_ids)):
            score += collaboration[character_id - 1][heroes_ids[j] - 1]

    for character_id in heroes_ids:
        for villain_id in villains_id:
            score += collaboration[villain_id - 1][character_id - 1]

    return score


def main(filename):
    villains = read_villains(filename)
    characters = read_characters('characters.csv')

    collaboration = read_collaboration('characters_collaboration.csv', len(characters))
    heroes = [item for item in characters.values() if item['Hero or Villain'] == 'hero']
    avg_villains_attributes = avg_attributes(villains, characters)

    def eval_func(chromosome):
        heroes_ids = []
        for value in chromosome:
            if value > 0:
                heroes_ids.append(value)

        if len(heroes_ids) < 2:
            return 0

        if len(heroes_ids) > len(villains):
            return 0

        if len(heroes_ids) != len(set(heroes_ids)):
            return 0

        avg_heroes_attributes = avg_attributes(heroes_ids, characters)
        if avg_heroes_attributes[0] < avg_villains_attributes[0]:
            return 0

        score = collaboration_score(heroes_ids, villains, collaboration)

        return score

    max_id = max([hero['Character ID'] for hero in heroes])

    best_genome = None

    for idx in range(0, 10):
        genome = G1DList.G1DList(len(villains))
        genome.evaluator.set(eval_func)
        genome.setParams(rangemin=0, rangemax=max_id)
        genome.mutator.set(Mutators.G1DListMutatorIntegerRange)

        ga = GSimpleGA.GSimpleGA(genome)
        ga.setGenerations(50 * len(villains))
        ga.setPopulationSize(50 * len(villains))
        ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)
        # ga.selector.set(Selectors.GTournamentSelector)
        ga.evolve()
        genome = ga.bestIndividual()

        if best_genome is None or best_genome.getFitnessScore() < genome.getFitnessScore():
            best_genome = genome

        # print genome
        # print genome.getFitnessScore()

    # print "-----------------------------"
    if best_genome.getFitnessScore() == 0:
        print "HEROES TEAM NOT FOUND"
    else:
        print list(best_genome)
        print best_genome.getFitnessScore()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'You must provide a villains file as parameter'
        exit(1)

    # main(sys.argv[1])

    import glob
    import time
    # files = glob.glob("Villan Teams with 763/*.txt")

    for i in range(2, 21, 2):
        f = "Villan Teams with 763/V{0}_763.txt".format(i)
        print f
        print '=================='
        start = time.clock()
        main(f)
        print "Demorou {0}s".format(time.clock() - start)
        print '\n\n\n'