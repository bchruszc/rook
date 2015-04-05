from rookscore import utils

class AwardWinner:
    # award = None
    players = []
    values = []
    linked_games = []
    
    def __init__(self, players, values, linked_games=None):
        # self.award = award
        self.players = players
        self.values = values
        self.linked_games = linked_games

class Award:
    icon_url = None
    name = "Empty Award"
    season_winners = {} # Tuple of season -> list of winners

    def sorted_season_winners(self):
        sorted_keys = sorted(self.season_winners.keys(), cmp=utils.season_compare_desc)
        
        results = []
        for k in sorted_keys:
            results.append((k, self.season_winners[k]))
            
        return results

    def add(self, game):
        pass
    
    def __str__(self):
        return self.name

class SeasonChampionAward(Award):
    def __init__(self):
        self.icon_url = None
        self.name = "Season Champion Award"
    
    def add(self, game, seasons):
        # Assume that the ratings are current
        for season in seasons:
            self.add_to_season(game, season)
    
    def add_to_season(self, game, season):
        # Check if it belongs in this season
        if season and (season.start_date > game.played_date.date() or season.end_date < game.played_date.date()):
            return
        
        winners = self.season_winners.get(season, [])
        
        if not winners:
            winners = []
        
        for score in game.scores.all():
            found = False
            for w in winners:
                if w.players[0] == score.player:
                    # Good!  Updated with the latest
                    w.values[0] = score.rating
                    found = True

            if not found:
                winners.append(AwardWinner(players=[score.player], values=[score.rating]))
        
        self.season_winners[season] = sorted(winners, cmp=compare_winners_desc)

def compare_winners_desc(w1, w2):
    # Sort within values
    w1val = None
    w2val = None
    
    for v in w1.values:
        if not w1val:
            w1val = v
        if v > w1val:
            w1val = v

    for v in w2.values:
        if not w2val:
            w2val = v
        if v > w2val:
            w2val = v

    return w2val - w1val

class AwardCache:
    all_awards = []
    
    def __init__(self):
        self.all_awards = []
        self.all_awards.append(SeasonChampionAward())
        
    def all(self):
        return self.all_awards