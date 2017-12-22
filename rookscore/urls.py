from django.conf.urls import url

from django.contrib import admin
from rookscore import views

admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'rookscore.views.home', name='home'),
    # url(r'^blog/', 'blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),

    url(r'^entry/', views.entry, name='entry'),

    url(r'^games/repair/', views.games_repair, name='games_repair'),

    url(r'^games/', views.games, name='games'),
    url(r'^game/(?P<game_id>\d+)/$', views.game, name='game'),

    url(r'^charts/', views.charts, name='charts'),

    url(r'^players/', views.players, name='players'),
    url(r'^player/(?P<player_id>\d+)/$', views.player, name='player'),

    url(r'^seasons/', views.seasons, name='seasons'),
    url(r'^season/(?P<season_id>\d+)/$', views.season, name='season'),
    url(r'^season/all/$', views.season_all, name='season_all'),

    url(r'^awards/', views.awards, name='awards'),
    url(r'^data/', views.data, name='data'),

    url(r'^repair_seasons/', views.repair_seasons, name='repair_seasons'),
    url(r'^repair_awards/', views.repair_awards, name='repair_awards'),

    url(r'^api/games/$', views.GameList.as_view(), name='api-games'),
    url(r'^api/games/(?P<pk>[0-9]+)/$', views.GameDetail.as_view(), name='api-game-detail'),
    url(r'^raw/games/$', views.RawGameList.as_view(), name='raw-games'),

    url(r'^api/scores/$', views.ScoreList.as_view(), name='api-scores'),
    url(r'^api/scores/(?P<pk>[0-9]+)/$', views.ScoreDetail.as_view(), name='api-score-detail'),
    url(r'^raw/scores/$', views.RawScoreList.as_view(), name='raw-scores'),

    url(r'^api/bid/$', views.BidList.as_view(), name='api-bid'),
    url(r'^api/bid/(?P<pk>[0-9]+)/$', views.BidDetail.as_view(), name='api-bid-detail'),
    url(r'^raw/bids/$', views.RawBidList.as_view(), name='raw-bid'),

    url(r'^api/players/$', views.PlayerList.as_view(), name='api-players'),
    url(r'^api/players/(?P<pk>[0-9]+)/$', views.PlayerDetail.as_view(), name='api-player-detail'),
    url(r'^raw/players/$', views.RawPlayerList.as_view(), name='raw-players'),

]

# import debug_toolbar
# urlpatterns += [
#
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
