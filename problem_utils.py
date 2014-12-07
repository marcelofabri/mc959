def powergrid_keys():
    return ['Intelligence', 'Strength', 'Speed', 'Durability', 'Energy Projection', 'Fighting Skills']


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


def total_collaboration_score(heroes_ids, villains_id, collaboration):
    score = collaboration_score(heroes_ids, collaboration)
    score += fighting_experience(heroes_ids, villains_id, collaboration)

    return score


def collaboration_score(heroes_ids, collaboration):
    score = 0
    for i, character_id in enumerate(heroes_ids):
        for j in range(i + 1, len(heroes_ids)):
            score += collaboration[character_id - 1][heroes_ids[j] - 1]
    return score


def fighting_experience(heroes_ids, villains_id, collaboration):
    score = 0
    for character_id in heroes_ids:
        for villain_id in villains_id:
            score += collaboration[villain_id - 1][character_id - 1]
    return score


def fitness(villains, characters, avg_villains_attributes, collaboration, budget_enabled=False, budget_available=None):
    def eval_func(chromosome):
        heroes_ids = [h for h in list(chromosome) if h > 0]
        
        if len(heroes_ids) < 2:
            return 0

        if len(heroes_ids) > len(villains):
            return 0

        if len(heroes_ids) != len(set(heroes_ids)):
            return 0

        avg_heroes_attributes = avg_attributes(heroes_ids, characters)
        if avg_heroes_attributes[0] < avg_villains_attributes[0]:
            return 0

        if budget_enabled and avg_heroes_attributes[2] > budget_available:
            return 0

        score = total_collaboration_score(heroes_ids, villains, collaboration)

        return score

    return eval_func