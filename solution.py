

class Solution:
    def __init__(self, heroes_ids, collaboration_score):
        self.heroes_ids = [h for h in heroes_ids if h > 0]
        self.collaboration_score = collaboration_score

    @staticmethod
    def collaboration_score(heroes_ids, collaboration):
        score = 0
        for i, character_id in enumerate(heroes_ids):
            for j in range(i + 1, len(heroes_ids)):
                score += collaboration[character_id - 1][heroes_ids[j] - 1]
        return score

    @staticmethod
    def fighting_experience(heroes_ids, villains_id, collaboration):
        score = 0
        for character_id in heroes_ids:
            for villain_id in villains_id:
                score += collaboration[villain_id - 1][character_id - 1]
        return score

    @staticmethod
    def total_collaboration_score(heroes_ids, villains_id, collaboration):
        score = Solution.collaboration_score(heroes_ids, collaboration)
        score += Solution.fighting_experience(heroes_ids, villains_id, collaboration)

        return score