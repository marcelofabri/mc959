import csv


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
    collaboration = [[0 for _ in range(size)] for _ in range(size)]
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
