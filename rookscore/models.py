from django.db import models
from datetime import timedelta
from datetime import datetime
from datetime import date

import utils

def get_rank(score):
    return score.rank

class Rankings:
    games_count = 0
    player_list = []

class PlayerManager(models.Manager):
    def rankings(self, month=None, year=None):
        games = None
        if month:
            if not year:
                year = datetime.now().year
            month_start = date(year, month, 1)
            next_month_start = month_start + timedelta(days=32)
            next_month_start.replace(day=1)
            games = Game.objects.filter(played_date__gte=month_start, played_date__lt=next_month_start)
        else:
            games = Game.objects.all()
        
        # We've got the games - run through them and calculate a ranking
        # I don't know how it works - let's just say you get a point for every player you beat!
        
        ratings = {}
        for g in games:
            utils.update_elo(g, ratings)
        
        all_players = ratings.keys()
        
        for p in all_players:
            p.rating = int(round(ratings[p]))
            
        utils.sortAndRankPlayers(all_players)
        
        rankings = Rankings()
        rankings.game_count = len(games)
        rankings.player_list = all_players
        
        return rankings

class Game(models.Model):
    played_date = models.DateTimeField('date played')

    # Generated Automatically
    entered_date = models.DateTimeField('date entered')
    
    def __str__(self):              # __unicode__ on Python 2
        return 'Game played on ' + str(self.played_date)

    class Meta:
        ordering = ('played_date', 'entered_date')

class Player(models.Model):
    player_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    objects = PlayerManager()
    
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
    
    def __str__(self):              # __unicode__ on Python 2
        return str(self.player) + ' ' + str(self.game) + ' ' + str(self.score) + ' Star: ' + str(self.made_bid)

    class Meta:
        ordering = ('rank', 'player')