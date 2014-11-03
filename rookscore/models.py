from django.db import models

class Game(models.Model):
    played_date = models.DateTimeField('date published')

    # Generated Automatically
    entered_date = models.DateTimeField('date published')

class Player(models.Model):
    player_id = models.IntegerField(default=0)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.first_name) + ' ' + str(self.last_name)

#
# A bid consists of a Caller, and optionally up to two partners
#
class Bid(models.Model):
    caller = models.ForeignKey(Player, related_name='caller')
    partners = models.ManyToManyField(Player, related_name='partners')
    opponents = models.ManyToManyField(Player, related_name='opponents')
    points_bid = models.IntegerField()
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
    game = models.ForeignKey(Game)
    score = models.IntegerField()
    made_bid = models.BooleanField()
    