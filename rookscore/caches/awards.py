from rookscore import utils

from rookscore.models import AwardTotals


class LoadedGame(object):
    def __init__(self, game, loaded_bids, scores):
        self.game = game
        self.loaded_bids = loaded_bids
        self.scores = scores


# A class to store a fully loaded bid
class LoadedBid(object):
    def __init__(self, bid, partners):
        self.bid = bid
        self.partners = partners


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
    def __init__(self, display_value=lambda values: str(values[0])):
        self.icon_url = '/static/img/goldmetal.png'
        self.name = "Empty Award"
        self.description = None
        self.season_winners = []
        self.full_season_required = False
        self.display_value = display_value

    # Given a list of award totals containing the previous state for this season, append this game
    def add_game(self, award_totals, game, all_players):
        return award_totals

    # def add(self, loaded_game):
    #     pass

    def __str__(self):
        return self.name


# This type of award considers every game as a potential counter
class GameCountAward(Award):
    def __init__(self, should_count, calc_value=lambda count, games: count, get_url=lambda rank, values: None,
                 reverse=True, display_value=lambda values: values[0]):
        # super(GameCountAward, self).__init__()
        super(GameCountAward, self).__init__(display_value=display_value)

        self.should_count = should_count
        self.calc_value = calc_value
        self.get_url = get_url
        # self.season_counts = {}
        # self.season_game_counts = {}
        self.season = None
        self.award_totals = None  # Dict player_id -> AwardTotals

    # Given a list of award totals containing the previous state for this season, append this game
    def add_game(self, game, all_players):
        matches_dict = {}
        for at in self.award_totals:
            matches_dict[at.player_id] = at

        # Ensure that an award_totals exists for every player in this game
        for s in game.scores.all():
            if s.player_id not in matches_dict.keys():
                at = AwardTotals()
                at.player_id = s.player_id
                at.numerator = 0
                at.denominator = 0
                at.type = self.name

                matches_dict[s.player_id] = at

            at = matches_dict[s.player_id]

            # Every game counts
            at.denominator += 1

            if self.should_count(s, game, all_players):
                at.numerator += 1

        self.award_totals = []
        for at in matches_dict.values():
            self.award_totals.append(at)

    def set_data(self, ats):
        self.award_totals = ats

        # Convert the counts to the winners format
        winners = []

        for at in self.award_totals:
            winners.append(
                AwardWinner([at.player_id], [self.calc_value(at.numerator, at.denominator)], self.display_value))

        winners.sort(key=lambda x: x.values[0], reverse=True)
        utils.rank(winners, key=lambda x: x.values[0])

        # Assign icons based on rank
        for winner in winners:
            winner.trophy_url = self.get_url(winner.rank, winner.values)

        self.season_winners = winners

        #
        #
        # def add_to_season(self, loaded_game, season):
        #     counts = self.season_counts.get(season, {})
        #     game_counts = self.season_game_counts.get(season, {})
        #
        #     # Add the contents of this game to the counts
        #     for s in loaded_game.scores:
        #         # Get the counts for this player, defaulting to zero
        #         p_count = counts.get(s.player_id, 0)
        #         g_count = game_counts.get(s.player_id, 0)
        #
        #         g_count += 1
        #         if self.should_count(s, loaded_game):
        #             p_count += 1
        #
        #         counts[s.player_id] = p_count
        #         game_counts[s.player_id] = g_count
        #
        #     # Convert the counts to the winners format
        #     winners = []
        #
        #     for player, count in counts.items():
        #         winners.append(AwardWinner([player], [self.calc_value(count, game_counts[player])], self.display_value))
        #
        #     winners.sort(key=lambda x: x.values[0], reverse=True)
        #     utils.rank(winners, key=lambda x: x.values[0])
        #
        #     # Assign icons based on rank
        #     for winner in winners:
        #         winner.trophy_url = self.get_url(winner.rank, winner.values)
        #
        #     # Set the main award types
        #     self.season_winners[season] = winners
        #     self.season_counts[season] = counts
        #     self.season_game_counts[season] = game_counts


# An award based on round-by-round accumulation.  Works for counts and percentages.  Must supply one method to
# determine if a round could count, and another if it does count
class RoundCountAward(Award):
    def __init__(self, should_count, could_count, calc_value=lambda count, games: count,
                 get_url=lambda rank, values: None, reverse=True, display_value=lambda values: values[0]):
        # super(GameCountAward, self).__init__()
        super(RoundCountAward, self).__init__(display_value=display_value)

        self.should_count = should_count  # Determine if this bid does count towards this award
        self.could_count = could_count  # Determine if a given bid could have counted towards this award

        self.calc_value = calc_value
        self.get_url = get_url
        # self.season_counts = {}
        # self.season_round_totals = {}
        self.season = None
        self.award_totals = None  # Dict player_id -> AwardTotals

    # def add(self, loaded_game, seasons):
    #     # Assume that the ratings are current
    #     for season in seasons:
    #         if season and (
    #                         season.start_date > loaded_game.game.played_date.date() or season.end_date < loaded_game.game.played_date.date()):
    #             continue
    #
    #         self.add_to_season(loaded_game, season)

    # Given a list of award totals containing the previous state for this season, append this game
    def add_game(self, game, all_players):
        # Load everything in to this dict
        matches_dict = {}
        for at in self.award_totals:
            matches_dict[at.player_id] = at

        # Ensure that an award_totals exists for every player in this game
        for s in game.scores.all():
            if s.player_id not in matches_dict.keys():
                at = AwardTotals()
                at.player_id = s.player_id
                at.numerator = 0
                at.denominator = 0
                at.type = self.name

                matches_dict[s.player_id] = at

            at = matches_dict[s.player_id]

            for b in game.bids.all():
                # Get the counts for this player, defaulting to zero
                if self.could_count(s, b, b.partners.all()):
                    at.denominator += 1

                    if self.should_count(s, b, b.partners.all()):
                        at.numerator += 1

        # Reset from the modified dict
        self.award_totals = []
        for at in matches_dict.values():
            self.award_totals.append(at)

    def set_data(self, ats):
        self.award_totals = ats

        # Convert the counts to the winners format
        winners = []

        for at in self.award_totals:
            # Filter out anyone who didn't have any rounds that were eligible for the award
            if at.denominator > 0:
                winners.append(
                    AwardWinner([at.player_id], [self.calc_value(at.numerator, at.denominator)], self.display_value))

        winners.sort(key=lambda x: x.values[0], reverse=True)
        utils.rank(winners, key=lambda x: x.values[0])

        # Assign icons based on rank
        for winner in winners:
            winner.trophy_url = self.get_url(winner.rank, winner.values)

        self.season_winners = winners


# Basic award which just keeps track of the most recent rating encountered
# We'll just use the numerator
class SeasonChampionAward(Award):
    def __init__(self):
        super(SeasonChampionAward, self).__init__()
        self.icon_url = '/static/img/goldtrophy.png'
        self.name = "Season Champion"
        self.full_season_required = True
        self.award_totals = []

    # Given a list of award totals containing the previous state for this season, append this game
    def add_game(self, game, all_players):
        # Load everything in to this dict
        matches_dict = {}
        for at in self.award_totals:
            matches_dict[at.player_id] = at

        # Ensure that an award_totals exists for every player in this game
        for s in game.scores.all():
            if s.player_id not in matches_dict.keys():
                at = AwardTotals()
                at.player_id = s.player_id
                at.numerator = 0
                at.denominator = 0
                at.type = self.name

                matches_dict[s.player_id] = at

            at = matches_dict[s.player_id]

            at.numerator = s.rating

        # Reset from the modified dict
        self.award_totals = []
        for at in matches_dict.values():
            self.award_totals.append(at)

    def set_data(self, ats):
        self.award_totals = ats

        # Convert the counts to the winners format
        winners = []

        for at in self.award_totals:
            # Filter out anyone who didn't have any rounds that were eligible for the award
            winners.append(
                AwardWinner([at.player_id], [at.numerator], self.display_value))

        winners.sort(key=lambda x: x.values[0], reverse=True)
        utils.rank(winners, key=lambda x: x.values[0])

        for winner in winners:
            if winner.rank == 1:
                winner.trophy_url = '/static/img/goldtrophy.png'
            elif winner.rank == 2:
                winner.trophy_url = '/static/img/silvertrophy.png'
            elif winner.rank == 3:
                winner.trophy_url = '/static/img/bronzetrophy.png'
            else:
                winner.trophy_url = None

        self.season_winners = winners


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

        award = GameCountAward(
            should_count=lambda score, game, all_players: score.rank == 2,
            get_url=url_first_only
        )
        award.name = 'Always a Bridesmaid'
        award.description = 'Number of second place finishes'
        self.all_awards.append(award)

        award = GameCountAward(
            should_count=lambda score, game, all_players: score.rank == 2,
            calc_value=calc_percent,
            get_url=url_first_only,
            display_value=lambda values: str(round(values[0], 1)) + '%'
        )
        award.name = 'Always a Bridesmaid Percentage'
        self.all_awards.append(award)

        award = GameCountAward(
            should_count=lambda score, game,
                                all_players: score.rank != 1 and score.score > game.scores.first().score - 180,
            get_url=url_first_only
        )
        award.name = 'Hypothetical Winner'
        award.description = 'Number of games where the player was within 180 points of winning, which would have allowed Martin to win if one thing just went a little differently'
        self.all_awards.append(award)

        award = GameCountAward(
            should_count=lambda score, game,
                                all_players: not score.made_bid and score.score > game.scores.first().score,
            get_url=url_first_only
        )
        award.name = 'Star Stuck'
        award.description = 'Number of games where the player would have` won if they had a star'
        self.all_awards.append(award)

        award = GameCountAward(
            should_count=lambda score, game, all_players: score.rank == 1,
            calc_value=calc_percent,
            get_url=url_first_only,
            display_value=lambda values: str(round(values[0], 1)) + '%'
        )
        award.name = 'Win Percentage'
        self.all_awards.append(award)

        # TODO:  Confirm that "add" actually works when a new game is saved and data exists
        #
        # Percentage of time this player calls a bid
        award = RoundCountAward(
            could_count=lambda score, bid, partners: True,
            should_count=lambda score, bid, partners: score.player_id == bid.caller_id,  #
            calc_value=calc_percent,
            get_url=url_first_only,
            display_value=lambda values: str(round(values[0], 1)) + '%'
        )

        award.name = 'Schoolyard Bully'
        award.description = 'Percentage of all bids called by this player'
        self.all_awards.append(award)

        # Success percentage when bidding
        award = RoundCountAward(
            could_count=lambda score, bid, partners: score.player_id == bid.caller_id,  #
            should_count=lambda score, bid, partners: bid.points_made >= bid.points_bid,
            calc_value=calc_percent,
            get_url=url_first_only,
            display_value=lambda values: str(round(values[0], 1)) + '%'
        )
        award.name = 'Fearless Leader'
        award.description = 'Percentage of bids made with this player as the caller'
        self.all_awards.append(award)

        # Success percentage when partner
        award = RoundCountAward(
            could_count=lambda score, bid, partners: score.player in partners,  #
            should_count=lambda score, bid, partners: bid.points_made >= bid.points_bid,
            calc_value=calc_percent,
            get_url=url_first_only,
            display_value=lambda values: str(round(values[0], 1)) + '%'
        )
        award.name = 'Partner in Crime'
        award.description = 'Percentage of bids made with this player as a partner'
        self.all_awards.append(award)

        # Percentage of time this player calls a bid
        award = RoundCountAward(
            could_count=lambda score, bid, partners: True,
            should_count=lambda score, bid, partners: bid.points_made < 100,
            calc_value=calc_percent,
            get_url=url_first_only,
            display_value=lambda values: str(round(values[0], 1)) + '%'
        )
        award.name = 'Enabler'
        award.description = 'Number of bids with over 100 points lost'
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
