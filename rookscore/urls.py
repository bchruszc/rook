from django.conf.urls import include, url
from django.contrib import admin

from django.conf.urls.static import static
from rest_framework import routers, serializers, viewsets

from django.contrib import admin
from rookscore import views
from rookscore import settings
from rookscore.models import Player, Game

#from rookscore.rest import PlayerResource, GameResource

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
#router = routers.DefaultRouter()
#router.register(r'games', GameViewSet)
#router.register(r'players', PlayerViewSet)

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
    
    url(r'^awards/', views.awards, name='awards'),

    url(r'^repair_seasons/', views.repair_seasons, name='repair_seasons'),
    url(r'^repair_awards/', views.repair_awards, name='repair_awards'),

    url(r'^api/games/$', views.GameList.as_view(), name='api-games'),
    url(r'^api/games/(?P<pk>[0-9]+)/$', views.GameDetail.as_view(), name='api-game-detail'),
    
    url(r'^api/scores/$', views.ScoreList.as_view(), name='api-scores'),
    url(r'^api/scores/(?P<pk>[0-9]+)/$', views.ScoreDetail.as_view(), name='api-score-detail'),
    
    url(r'^api/bid/$', views.BidList.as_view(), name='api-bid'),
    url(r'^api/bid/(?P<pk>[0-9]+)/$', views.BidDetail.as_view(), name='api-bid-detail'),

    url(r'^api/players/$', views.PlayerList.as_view(), name='api-players'),
    url(r'^api/players/(?P<pk>[0-9]+)/$', views.PlayerDetail.as_view(), name='api-player-detail'),

    # url(r'^api/', router.urls)),
    #url(r'^api-auth/', 'rest_framework.urls', namespace='rest_framework')),
    
    #url(r'^api/players/', PlayerResource.urls()),
    #url(r'^api/games/', GameResource.urls()),
    
    # url(r'^silk/', 'silk.urls', namespace='silk'),
]

import debug_toolbar
urlpatterns += [

        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
