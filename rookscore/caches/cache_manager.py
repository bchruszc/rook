#
# A manager to wrap the creation of caches
#

#from django.core.c#che import caches
# from rookscore.models import Game, Player
# from rookscore.caches.seasons import SeasonCache
# from rookscore.caches.awards import AwardCache, LoadedGame, LoadedBid
#

# class CacheManager:
#     # Build or create the seasons cache
#     _seasons = None
#     _awards = None
#
#     def seasons(self):
#         # Only available in Django 1.7 - no caching for now
#         # cached_seasons = caches.get('seasons')
#
#         # if cached_seasons:
#         #     return cached_seasons
#
#         sc = SeasonCacheBuilder().build()
#
#         # caches.put('seasons', sc)
#         return sc
#
#     def awards(self):
#         a = AwardCacheBuilder().build()
#         return a
#
# class SeasonCacheBuilder:
#     def build(self, games=Game.objects.all()):
#         sc = SeasonCache()
#         for g in games:
#             sc.add(g.played_date)
#
#         return sc
#
# class AwardCacheBuilder:
#     def build(self, games=Game.objects.prefetch_related().all()):
#         all_seasons = CacheManager().seasons().all()
#         all_seasons.append(None)
#
#         ac = AwardCache()
#
#         players = Player.objects.all()
#
#         for g in games.order_by('-played_date'):#[0:10]:
#             bids_queryset = g.bids.all()
#             loaded_bids = []
#             for b in bids_queryset:
#                 loaded_bids.append(LoadedBid(b, b.partners.values()))
#
#             lg = LoadedGame(g, loaded_bids, g.scores.all())
#             for a in ac.all_awards:
#                 a.add(lg, all_seasons)
#
#         return ac