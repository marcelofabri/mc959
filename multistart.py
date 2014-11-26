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


def main():
    characters = read_characters('characters.csv')
    print characters

if __name__ == "__main__":
    main()