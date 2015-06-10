from rookscore import utils

import operator

class AwardWinner(object):
    def __init__(self, players, values, display_value, linked_games=None):
        # self.award = award
        self.players = players
        self.values = values
        self.linked_games = linked_games
        self.rank = None
        self.trophy_url = None
        self.display_value = display_value
        
    def display(self):
        return self.display_value(self.values)

class Award(object):
    def __init__(self, display_value=lambda values : str(values[0])):
        self.icon_url = '/static/img/goldmetal.png'
        self.name = "Empty Award"
        self.season_winners = {} # Tuple of season -> list of winners
        self.full_season_required = False
        self.display_value = display_value

    def sorted_season_winners(self):
        sorted_keys = sorted(self.season_winners.keys(), key=lambda x: x.sort_key, reverse=True)
        
        results = []
        for k in sorted_keys:
            results.append((k, self.season_winners[k]))
            
        return results

    def add(self, game):
        pass
    
    def __str__(self):
        return self.name

class GameCountAward(Award):
    def __init__(self, should_count, calc_value=lambda count, games : count, get_url=lambda rank, values : None, reverse=True, display_value=lambda values : values[0]):
        #super(GameCountAward, self).__init__()
        super(GameCountAward, self).__init__(display_value=display_value)
        
        self.should_count = should_count
        self.calc_value = calc_value
        self.get_url = get_url
        self.season_counts = {}
        self.season_game_counts = {}
    
    def add(self, game, seasons):
        # Assume that the ratings are current
        for season in seasons:
            if season and (season.start_date > game.played_date.date() or season.end_date < game.played_date.date()):
                continue
            
            self.add_to_season(game, season)
    
    def add_to_season(self, game, season):
        counts = self.season_counts.get(season, {})
        game_counts = self.season_game_counts.get(season, {})
        
        # Add the contents of this game to the counts
        for s in game.scores.all():
            # Get the counts for this player, defaulting to zero
            p_count = counts.get(s.player, 0)
            g_count = game_counts.get(s.player, 0)

            g_count = g_count + 1
            if self.should_count(s, game):
                p_count = p_count + 1

            counts[s.player] = p_count
            game_counts[s.player] = g_count
                
        # Convert the counts to the winners format
        winners = []
        
        for player, count in counts.items():
            winners.append(AwardWinner([player], [self.calc_value(count, game_counts[player])], self.display_value ))
        
        winners.sort(key=lambda x: x.values[0], reverse=True)
        utils.rank(winners, key=lambda x: x.values[0])
        
        # Assign icons based on rank
        for winner in winners:
            winner.trophy_url = self.get_url(winner.rank, winner.values)

        # Set the main award types
        self.season_winners[season] = winners
        self.season_counts[season] = counts
        self.season_game_counts[season] = game_counts

class SeasonChampionAward(Award):
    def __init__(self):
        super(SeasonChampionAward, self).__init__()
        self.icon_url = '/static/img/goldtrophy.png'
        self.name = "Season Champion"
        self.full_season_required = True
    
    def add(self, game, seasons):
        # Assume that the ratings are current
        for season in seasons:
            if season and (season.start_date > game.played_date.date() or season.end_date < game.played_date.date()):
                continue
            
            self.add_to_season(game, season)
    
    def add_to_season(self, game, season):
        # Check if it belongs in this season
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
                winners.append(AwardWinner(players=[score.player], values=[score.rating], display_value=self.display_value))
        
        self.season_winners[season] = sorted(winners, key=lambda x: x.values[0], reverse=True)
        utils.rank(self.season_winners[season], key=lambda x: x.values[0])
        
        for winner in self.season_winners[season]:
            if winner.rank == 1:
                winner.trophy_url = '/static/img/goldtrophy.png'
            elif winner.rank == 2:
                winner.trophy_url = '/static/img/silvertrophy.png'
            elif winner.rank == 3:
                winner.trophy_url = '/static/img/bronzetrophy.png'
            else:
                winner.trophy_url = None


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
        
        award = GameCountAward(should_count=lambda score, game : score.rank == 2, get_url=url_first_only)
        award.name = 'Always a Bridesmaid'
        self.all_awards.append(award)

        award = GameCountAward(should_count=lambda score, game : score.rank == 2, calc_value=calc_percent, get_url=url_first_only)
        award.name = 'Always a Bridesmaid Percentage'
        self.all_awards.append(award)
        
        award = GameCountAward(should_count=lambda score, game : score.rank != 1 and score.score > game.scores.all()[0].score - 180, get_url=url_first_only)
        award.name = 'Hypothetical Winner'
        self.all_awards.append(award)

        award = GameCountAward(should_count=lambda score, game : not score.made_bid and score.score > game.scores.all()[0].score, get_url=url_first_only)
        award.name = 'Star Stuck'
        self.all_awards.append(award)

        award = GameCountAward(should_count=lambda score, game : score.rank == 1, calc_value=calc_percent, get_url=url_first_only, display_value=lambda values : str(values[0]) + '%')
        award.name = 'Win Percentage'
        self.all_awards.append(award)
        
    def all(self):
        return self.all_awards
        
def url_first_only(rank, values):
    if rank == 1 and values[0] > 0:
        return '/static/img/goldmetal.png'
    else:
        return None
        
def calc_percent(count, game_count):
    return 100 * count / game_count