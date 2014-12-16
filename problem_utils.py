from solution import Solution


class Attributes:

    def __init__(self, avg_powergrid, avg_popularity, cost, skills):
        self.avg_powergrid = avg_powergrid
        self.avg_popularity = avg_popularity
        self.cost = cost
        self.skills = skills

    @staticmethod
    def powergrid_keys():
        return ['Intelligence', 'Strength', 'Speed', 'Durability', 'Energy Projection', 'Fighting Skills']

    @staticmethod
    def attributes_from_characters(characters_ids, all_characters):
        sum_popularity = 0
        cost = 0
        keys = Attributes.powergrid_keys()
        powergrid = [0 for _ in keys]
        for characters_id in characters_ids:
            character = all_characters[characters_id]
            local_sum = 0
            for idx, key in enumerate(keys):
                powergrid[idx] += character[key]
                local_sum += character[key]
            sum_popularity += character['Number of Comic Books Where Character Appeared']
            cost += character['Number of Comic Books Where Character Appeared'] * float(local_sum) / len(keys)

        qtd = float(len(characters_ids))

        for idx in range(0, len(keys)):
            powergrid[idx] /= qtd

        avg_powergrid = sum(powergrid) / float(len(powergrid))
        avg_popularity = sum_popularity / qtd

        attributes = Attributes(avg_powergrid, avg_popularity, cost, powergrid)
        return attributes


def is_hero(character):
    return character['Hero or Villain'] == 'hero'


def budget(villains_ids, all_characters):
    all_heroes_ids = []
    all_villains_ids = []
    for character in all_characters.values():
        if is_hero(character):
            all_heroes_ids.append(character['Character ID'])
        else:
            all_villains_ids.append(character['Character ID'])

    villains_attributes = Attributes.attributes_from_characters(villains_ids, all_characters)
    all_villains_attributes = Attributes.attributes_from_characters(all_villains_ids, all_characters)
    all_heroes_attributes = Attributes.attributes_from_characters(all_heroes_ids, all_characters)

    ratio_pg = all_heroes_attributes.avg_powergrid / villains_attributes.avg_powergrid
    ratio_pop = all_heroes_attributes.avg_popularity / villains_attributes.avg_popularity
    vt_cost = villains_attributes.cost

    expr1 = ratio_pg * ratio_pop * vt_cost

    factor = villains_attributes.avg_powergrid / all_villains_attributes.avg_powergrid
    avg_pg = all_heroes_attributes.avg_powergrid
    avg_pop = all_heroes_attributes.avg_popularity
    vt_size = len(villains_ids)

    expr2 = factor * avg_pg * avg_pop * vt_size

    return max(expr1, expr2)


def fitness(villains, characters, villains_attributes, collaboration, budget_enabled=False, budget_available=None):
    def eval_func(chromosome):
        heroes_ids = [h for h in list(chromosome) if h > 0]
        
        if len(heroes_ids) < 2:
            return 0

        if len(heroes_ids) > len(villains):
            return 0

        if len(heroes_ids) != len(set(heroes_ids)):
            return 0

        heroes_attributes = Attributes.attributes_from_characters(heroes_ids, characters)
        for idx in range(0, len(Attributes.powergrid_keys())):
            if heroes_attributes.skills[idx] < villains_attributes.skills[idx]:
                return 0

        if budget_enabled and heroes_attributes.cost > budget_available:
            return 0

        score = Solution.total_collaboration_score(heroes_ids, villains, collaboration)

        return score

    return eval_func