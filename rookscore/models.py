from django.db import models
from datetime import timedelta
from datetime import datetime
from datetime import date

from trueskill import TrueSkill

from rookscore import utils

# Season-related constants
ELO = 'e'
TRUESKILL = 't'

RATING_SYSTEMS = (
    (ELO, 'Elo'),
    (TRUESKILL, 'TrueSkill'),
)


def get_rank(score):
    return score.rank


class Rankings:
    games_count = 0
    player_list = []


class AwardTotalsManager(models.Manager):
    def get_player_id_dict(self, award, season):
        # Load everything for this award/season and populate a player-indexed dict

        matches_dict = {}

        for at in self.filter(season=season, type=award.name):
            matches_dict[at.player_id] = at

        return matches_dict

    def group_by_type(self, season):
        matches = self.filter(season=season)
        matches_dict = {}

        for at in matches:
            if at.type in matches_dict.keys():
                matches_dict[at.type].append(at)
            else:
                matches_dict[at.type] = [at]

        return matches_dict


class GameManager(models.Manager):
    # pylint: disable=maybe-no-member
    def season(self, season):
        return Game.objects.filter(played_date__gte=season.start, played_date__lte=season.end)


class PlayerManager(models.Manager):
    # pylint: disable=maybe-no-member
    # Generate on-the-fly rankings for this season
    def rankings(self, season=None, rating_system=TRUESKILL):
        if season:
            games = Game.objects.season(season)
        else:
            games = Game.objects.all()

        games.prefetch_related('scores')
        all_players = self.all_as_dict()

        # We've got the games - run through them and calculate a ranking
        ratings = {}
        trueskill_ratings = {}

        # For the selected season, create a time/ratings pair for each player
        ratings_history = {}

        game_counts = {}
        win_counts = {}

        env = TrueSkill()

        for g in games:
            scores = g.scores.all()

            utils.update_elo(scores, ratings)
            utils.update_trueskill(scores, trueskill_ratings)

            for s in scores:
                if s.player_id not in game_counts.keys():
                    game_counts[s.player_id] = 1
                    ratings_history[all_players[s.player_id]] = []
                    win_counts[s.player_id] = 0
                else:
                    game_counts[s.player_id] += 1

                if s.rank is 1:
                    win_counts[s.player_id] += 1

                # For every player in this game, log their updated ratings at this point in time
                elo = round(env.expose(trueskill_ratings[s.player_id]), 1)
                ratings_history[all_players[s.player_id]].append({'x': g.played_date.timestamp(), 'y': elo})

            last_game_scores = scores

        ranked_player_ids = ratings.keys()
        ranked_players = []

        for player_id in ranked_player_ids:
            player = all_players[player_id]
            player.rating = round(ratings[player_id])
            player.trueskill = round(env.expose(trueskill_ratings[player_id]), 1)
            player.trueskill_hover = "mu={0:0.1f}, sigma={1:0.2f}".format(trueskill_ratings[player_id].mu,
                                                                          trueskill_ratings[player_id].sigma)
            ranked_players.append(player)

        ranked_players = utils.sortAndRankPlayers(ranked_players, rating_system)

        for p in ranked_players:
            p.rating_change = None
            p.game_count = game_counts[p.id]
            p.win_count = win_counts[p.id]
            for s in last_game_scores:
                if p.id == s.player_id:
                    p.rating_change = round(s.rating_change)
                    p.trueskill_change = round(s.trueskill_change, 2)
                    break

        rankings = Rankings()
        rankings.game_count = len(games)
        rankings.player_list = ranked_players

        return rankings, ratings_history

    def all_as_dict(self):
        player_dict = {}

        for p in self.all():
            player_dict[p.id] = p

        return player_dict


class SeasonManager(models.Manager):
    #
    # Creates a season if necessary, and returns it
    #
    def get_or_create(self, the_date):
        existing = self.get_for_date(the_date)

        if existing:
            return existing

        # Create
        new_season = self.__create_for_date(the_date)
        new_season.save()

        return new_season

    #
    # Returns the current season
    #
    def current(self):
        return self.get_for_date(datetime.today())

    #
    # Gets the season for the given date, returning None if it does not exist
    #
    def get_for_date(self, the_date):
        try:
            return self.get(start__lte=the_date, end__gte=the_date)
        except self.model.DoesNotExist:
            return None

    def __create_for_date(self, the_date):
        # Otherwise, add it
        year = the_date.year
        month = the_date.month

        if month <= 3:
            return Season(name="Winter " + str(year), start=date(year, 1, 1), end=date(year, 4, 1) + timedelta(days=-1))
        elif month <= 6:
            return Season(name="Spring " + str(year), start=date(year, 4, 1), end=date(year, 7, 1) + timedelta(days=-1))
        elif month <= 9:
            return Season(name="Summer " + str(year), start=date(year, 7, 1),
                          end=date(year, 10, 1) + timedelta(days=-1))
        else:
            return Season(name="Fall " + str(year), start=date(year, 10, 1),
                          end=date(year + 1, 1, 1) + timedelta(days=-1))


class CumulativeRound:
    points = []
    description = ''


class Game(models.Model):
    objects = GameManager()

    played_date = models.DateTimeField('date played')

    # Generated Automatically
    entered_date = models.DateTimeField('date entered')

    def rounds(self):
        # Get the order based on the order of the scores, then build the table
        totals = {}
        players = []
        all_players = Player.objects.all_as_dict()

        for score in self.scores.all():
            players.append(all_players[score.player_id])
            totals[all_players[score.player_id]] = 0

        rounds = []

        if len(players) == 0:
            return rounds

        for bid in self.bids.all().prefetch_related('partners', 'opponents'):
            r = CumulativeRound()
            round_total = {}
            r.points = []  # in order by rank

            partners = bid.partners.all()

            # If the bid was made

            if bid.points_made >= bid.points_bid:
                round_total[all_players[bid.caller_id]] = totals[all_players[bid.caller_id]] + bid.points_made

                alone = True
                for p in partners:
                    round_total[p] = totals[p] + bid.points_made
                    if p.id != bid.caller_id:
                        alone = False

                # Bonus for going alone = 10pts for every partner you didn't need
                if alone:
                    if len(players) >= 6:
                        round_total[all_players[bid.caller_id]] += 40
                    else:
                        round_total[all_players[bid.caller_id]] += 20

                for p in bid.opponents.all():
                    round_total[p] = totals[p] + (180 - bid.points_made)

            # If not...
            else:
                round_total[all_players[bid.caller_id]] = totals[all_players[bid.caller_id]] - bid.points_bid

                for p in partners:
                    round_total[p] = totals[p] - bid.points_bid

                for p in bid.opponents.all():
                    round_total[p] = totals[p] + (180 - bid.points_made)

            # Collect it all
            for p in players:
                if p in round_total.keys():
                    r.points.append((p, round_total[p]))
                    totals[p] = round_total[p]
                else:
                    r.points.append((p, totals[p]))

            partner_initials = []
            for p in partners:
                partner_initials.append(p.initials())

            r.description = str(all_players[bid.caller_id].initials()) + ' ' + str(bid.points_bid) + ' ' + ', '.join(
                partner_initials)
            r.made = bid.points_made >= bid.points_bid
            r.bid = bid
            r.players = players
            rounds.append(r)

        return rounds

    def __str__(self):  # __unicode__ on Python 2
        return 'Game played on ' + str(self.played_date)

    class Meta:
        ordering = ('played_date', 'entered_date')


class Player(models.Model):
    player_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    objects = PlayerManager()

    def initials(self):
        return self.first_name[0] + self.last_name[0]

    def __str__(self):  # __unicode__ on Python 2
        return str(self.first_name) + ' ' + str(self.last_name)

    class Meta:
        ordering = ('first_name', 'last_name')


#
# A bid consists of a Caller, and optionally up to two partners
#
class Bid(models.Model):
    game = models.ForeignKey(Game, related_name='bids')
    caller = models.ForeignKey(Player, related_name='caller')
    partners = models.ManyToManyField(Player, related_name='partners')
    opponents = models.ManyToManyField(Player, related_name='opponents')
    points_bid = models.IntegerField(default=False)
    points_made = models.IntegerField()
    hand_number = models.IntegerField(default='0')

    def __str__(self):  # __unicode__ on Python 2
        return str(self.caller) + ' bid ' + str(self.points_bid) + ' and made ' + str(self.points_made)


# class Meta:
#        ordering = ('title',)


#
# How well a given player did in a given game
#
class PlayerGameSummary(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game, related_name='scores')
    score = models.IntegerField()
    made_bid = models.BooleanField()
    rank = models.IntegerField(default='7')
    rating = models.IntegerField(default='0')
    rating_change = models.IntegerField(default='0')

    trueskill = models.FloatField(default='0')  # Mu
    trueskill_confidence = models.FloatField(default='0')  # Sigma
    trueskill_change = models.FloatField(default='0')

    def __str__(self):  # __unicode__ on Python 2
        return str(self.player) + ' ' + str(self.game) + ' ' + str(self.score) + ' Star: ' + str(self.made_bid)

    class Meta:
        ordering = ('rank', 'player')


#
# Used to group season-related stuff together
#
class Season(models.Model):
    objects = SeasonManager()

    # Start and end dates are inclusive
    start = models.DateField()
    end = models.DateField()
    name = models.CharField(max_length=40)
    rating_system = models.CharField(
        max_length=1,
        choices=RATING_SYSTEMS,
        default=ELO)  # Set the default to ELO for historical seasons

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('start',)


#
# A per season summary of a player/award eligibility.  We'll store season x type x player awards, but still way
# cheaper than iterating over every game to recalculate!!
#
class AwardTotals(models.Model):
    objects = AwardTotalsManager()

    season = models.ForeignKey(Season)

    # Maps to the name of the award.  The award itself will contain all of the functions to calculate it
    type = models.CharField(max_length=100)
    player = models.ForeignKey(Player)

    numerator = models.IntegerField()
    denominator = models.IntegerField()

    def __str__(self):
        return self.type + ' ' + str(self.season)
