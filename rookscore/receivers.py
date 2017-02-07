
#
# Need to do a few things with every save - create a season if it doesn't exist, and update awards
#
from django.db.models.signals import post_save
from django.dispatch import receiver

from rookscore.caches.awards import AwardCache
from rookscore.models import Game, Season, Player, AwardTotals


@receiver(post_save, sender=Game)
def game_save_handler(instance, **kwargs):
    # Find the season that we're in
    season = Season.objects.get_or_create(instance.played_date)

    # Preload all of the players so that they're available without hitting the database
    all_players = Player.objects.all_as_dict()

    # Load the awards
    awards = AwardCache().all()

    # For each award and player, crunch the numbers
    for award in awards:
        # A list of award totals for the provided players
        award_totals = AwardTotals.objects.filter(type=award.name, season=season)

        # Update the award total with this game
        award.set_data(award_totals)
        award.add_game(instance, all_players)

        # Save - Likely more efficient to batch update, but meh for now
        for at in award.award_totals:
            # Ensure that all award totals have a season (new ones don't know)
            at.season = season
            at.save()
