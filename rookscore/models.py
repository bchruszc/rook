from django.db import models
from datetime import timedelta
from datetime import datetime
from datetime import date

from rookscore import utils

def get_rank(score):
    return score.rank

class Rankings:
    games_count = 0
    player_list = []

class GameManager(models.Manager):
    #pylint: disable=maybe-no-member
    def season(self, season):
        return Game.objects.filter(played_date__gte=season.start_date, played_date__lte=season.end_date)

class PlayerManager(models.Manager):
    #pylint: disable=maybe-no-member
    def rankings(self, season=None):
        games = None
        if season:
            games = Game.objects.season(season)
        else:
            games = Game.objects.all()
        
        # We've got the games - run through them and calculate a ranking
        ratings = {}

        last_game = None
        game_counts = {}
        
        for g in games:
            utils.update_elo(g, ratings)
            
            for s in g.scores.all():
                if not s.player in game_counts.keys():
                    game_counts[s.player] = 1
                else:
                    game_counts[s.player] = game_counts[s.player] + 1
            
            last_game = g
        
        all_players = ratings.keys()
        
        for p in all_players:
            p.rating = int(round(ratings[p]))
            
        all_players = utils.sortAndRankPlayers(all_players)
        
        for p in all_players:
            p.rating_change = None
            p.game_count = game_counts[p]
            for s in last_game.scores.all():
                if p == s.player:
                    p.rating_change = s.rating_change
                    break
        
        rankings = Rankings()
        rankings.game_count = len(games)
        rankings.player_list = all_players
        
        return rankings

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
        
        for score in self.scores.all():
            players.append(score.player)
            totals[score.player] = 0

        rounds = []
        
        for bid in self.bids.all():
            r = CumulativeRound()
            round_total = {}
            r.points = []  #in order by rank
            # If the bid was made
            
            if bid.points_made >= bid.points_bid:
                round_total[bid.caller] = totals[bid.caller] + bid.points_made
                
                for p in bid.partners.all():
                    round_total[p] = totals[p] + bid.points_made

                for p in bid.opponents.all():
                    round_total[p] = totals[p] + (180 - bid.points_made)

            # If not...
            else:
                round_total[bid.caller] = totals[bid.caller] - bid.points_bid
                
                for p in bid.partners.all():
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
            
            partners = []
            for p in bid.partners.all():
                partners.append(p.initials()) 
                
            r.description = str(bid.caller.initials()) + ' ' + str(bid.points_bid) + ' ' + ', '.join(partners)
            r.made = bid.points_made >= bid.points_bid
            r.bid = bid
            r.players = players
            rounds.append(r)
        
        return rounds
        
    
    def __str__(self):              # __unicode__ on Python 2
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
    
    def __str__(self):              # __unicode__ on Python 2
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
    
    def __str__(self):              # __unicode__ on Python 2
        return str(self.caller) + ' bid ' + str(self.points_bid) + ' and made ' + str(self.points_made)

#    class Meta:
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
    
    def __str__(self):              # __unicode__ on Python 2
        return str(self.player) + ' ' + str(self.game) + ' ' + str(self.score) + ' Star: ' + str(self.made_bid)

    class Meta:
        ordering = ('rank', 'player')
      
