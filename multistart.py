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


def main():
    characters = read_characters('characters.csv')
    print characters
    collaboration = read_collaboration('characters_collaboration.csv')
    print collaboration

if __name__ == "__main__":
    main()