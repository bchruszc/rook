from django.contrib import admin
from rookscore.models import Game, Player, Bid, Season, AwardTotals

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Bid)
admin.site.register(Season)
admin.site.register(AwardTotals)