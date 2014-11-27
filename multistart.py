import csv
import sys


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


def read_collaboration(filename):
    collaboration = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            row = proccess_row(row)
            current = collaboration.get(row['Character 1 ID'], {})
            current[row['Character 2 ID']] = row['Number of Comic Books Where Character 1 and Character 2 Both Appeared']

            collaboration[row['Character 1 ID']] = current
    return collaboration


def read_villains(filename):
    villains = []
    with open(filename) as f:
        for row in f.readlines():
            villains += [int(x) for x in row.split(' ')]
    return villains


def avg_attributes(characters_ids, all_characters):
    sum_power_grid = 0
    sum_popularity = 0
    vt_cost = 0
    keys = ['Intelligence','Strength', 'Speed', 'Durability', 'Energy Projection', 'Fighting Skills']
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


def main(filename):
    villains = read_villains(filename)
    characters = read_characters('characters.csv')
    print budget(villains, characters)
    collaboration = read_collaboration('characters_collaboration.csv')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'You must provide a villains file as parameter'
        exit(1)
    main(sys.argv[1])