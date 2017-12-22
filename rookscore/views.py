from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.shortcuts import render

from rookscore import models
from rookscore.caches.awards import AwardCache
from rookscore.forms import PlayerForm
from rookscore.models import Player, Game, PlayerGameSummary, Bid, Season, AwardTotals
from rookscore.receivers import game_save_handler
from rookscore.serializers import GameSerializer, RawGameSerializer, PlayerSerializer, RawPlayerSerializer, \
    ScoreSerializer, RawScoreSerializer, BidSerializer, RawBidSerializer
from rookscore import settings

from rest_framework import generics
from rest_framework import permissions

from datetime import datetime, date
from rookscore import utils

import logging
import json

logger = logging.getLogger('rook2_beta')


def index(request):
    s = Season.objects.current()  # CacheManager().seasons().get(datetime.today())
    return render_season(request, s)


# Need to convert the histories in to d3 consumable data.  Simple python dicts converted to a json string
def rankings_history_to_graph_data(history):
    all_series = []

    for k in history.keys():
        series = {'values': history[k], 'key': k.initials()}
        all_series.append(series)

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            serial = obj.timestamp()
            return serial
        raise TypeError("Type %s not serializable" % type(obj))

    return json.dumps(all_series, default=json_serial)


# Render a specific season, or all if season = None
def render_season(request, season):
    if season:
        rating_system = season.rating_system
    else:
        rating_system = models.TRUESKILL

    rankings, ratings_history = Player.objects.rankings(season, rating_system)

    # Show most recent first, if a season limit to that season, and just the last 5
    recent_game_list = Game.objects.order_by('-played_date')
    if season:
        recent_game_list = recent_game_list.filter(played_date__lte=season.end)

    recent_game_list = recent_game_list[:5]
    # recent_game_list.prefetch_related('bids', 'bids')
    recent_game_list.prefetch_related('scores')

    template = loader.get_template('rookscore/index.html')
    context = RequestContext(request, {
        'season': season,
        'rating_system': rating_system,
        'rankings': rankings,
        'recent_game_list': recent_game_list,
        'settings': settings,
        'graph_data': rankings_history_to_graph_data(ratings_history),
    })
    return HttpResponse(template.render(context))


def entry(request):
    if request.method == 'POST':  # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = PlayerForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # Great, a legit game!  Let's save it

            game = Game()
            game.played_date = form.cleaned_data['game_date']
            game.entered_date = datetime.now()
            game.save()

            summaries = []
            scores = []

            for i in range(1, 7):
                player = form.cleaned_data['name' + str(i)]
                if player:
                    # This player was entered
                    summary = PlayerGameSummary()

                    summary.player = player
                    summary.game = game
                    summary.score = form.cleaned_data['score' + str(i)]
                    summary.made_bid = form.cleaned_data['star' + str(i)]

                    summary.save()

                    summaries.append(summary)
                    scores.append(summary.score)

                else:
                    # Left blank, and that's okay.
                    pass

            utils.sortAndRankSummaries(summaries)

            for s in summaries:
                s.save()

            return HttpResponseRedirect('/')  # Redirect after POST
    else:
        form = PlayerForm()

    return render(request, 'rookscore/entry.html', {
        'form': form,
    })


'''
def entry(request):
    player_list = Player.objects.order_by('-first_name')[:5]
    template = loader.get_template('rookscore/entry.html')
    context = RequestContext(request, {
        
    })
    return HttpResponse(template.render(context))    
'''


def games_repair(request):
    # Ensure everyone has the right rank
    for g in Game.objects.all():
        summaries = list(g.scores.all())
        utils.sortAndRankSummaries(summaries)

        # Temp - set opponents to be everyone who's not the caller or partner
        players = []
        for s in g.scores.all():
            players.append(s.player)
        # End temp

        for s in summaries:
            s.save()

        for bid in g.bids.all():
            # Temp
            opponents = []

            for p in players:
                if p != bid.caller and p not in bid.partners.all():
                    opponents.append(p)

            bid.opponents = opponents

            bid.save()

            # End Temp

    # Update all of the Elo scores
    seasons = Season.objects.all()
    for s in seasons:
        Player.objects.rankings(s)

    return HttpResponse("<html><body>Repair complete.</body></html>")


def charts(request):
    games_list = Game.objects.order_by('-entered_date')
    template = loader.get_template('rookscore/charts.html')
    context = RequestContext(request, {
        'games_list': games_list,
    })
    return HttpResponse(template.render(context))


def games(request):
    all_games = Game.objects.order_by('-entered_date')
    paginator = Paginator(all_games, 10)  # Show 10 games per page

    page = request.GET.get('page')

    try:
        games_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        games_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        games_list = paginator.page(paginator.num_pages)

    games_list.object_list.prefetch_related('scores')

    template = loader.get_template('rookscore/games.html')
    context = RequestContext(request, {
        'games_list': games_list,
    })
    return HttpResponse(template.render(context))


def game(request, game_id):
    #    from django.http import Http404
    #    def detail(request, poll_id):
    #    try:
    #        poll = Poll.objects.get(pk=poll_id)
    #    except Poll.DoesNotExist:
    #        raise Http404
    #    return render(request, 'polls/detail.html', {'poll': poll})

    return HttpResponse("You have requested game #" + str(game_id))


def seasons(request):
    seasons = Season.objects.all()
    template = loader.get_template('rookscore/seasons.html')
    context = RequestContext(request, {
        'seasons': seasons,
    })
    return HttpResponse(template.render(context))


def season(request, season_id):
    try:
        season = Season.objects.get(id=season_id)
    except Player.DoesNotExist:
        season = None

    return render_season(request, season)


def season_all(request):
    return render_season(request, None)


def players(request):
    players_list = Player.objects.order_by('first_name')
    template = loader.get_template('rookscore/players.html')
    context = RequestContext(request, {
        'players_list': players_list,
    })
    return HttpResponse(template.render(context))


def player(request, player_id):
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        raise Http404

    all_players = Player.objects.all()
    recent_games = Game.objects.filter()

    finishes = []
    finishes.append(['4 Player', 0, 0, 0, 0, '', '', ])
    finishes.append(['5 Player', 0, 0, 0, 0, 0, '', ])
    finishes.append(['6 Player', 0, 0, 0, 0, 0, 0, ])
    finishes.append(['Total', 0, 0, 0, 0, 0, 0, ])

    for score in PlayerGameSummary.objects.filter(player=player):
        num_players = score.game.scores.count()
        if score.rank < 7:
            finishes[num_players - 4][score.rank] += 1
            finishes[3][score.rank] += 1

    all_awards = []  # TODO Awards: CacheManager().awards().all()
    player_awards = []

    for award in all_awards:
        for season, winners in award.season_winners.items():
            # if season == SeasonCache().get(datetime.today()) and award.full_season_required:
            #     # Exclude seasonal awards that are in progress
            #     continue

            for winner in winners:
                if player in winner.players:
                    player_awards.append({
                        'award': award,
                        'season': season,
                        'winner': winner,
                    })

    player_awards.sort(key=lambda x: x['season'].sort_key if x['season'] else 0, reverse=True)
    current_season = Season.objects.current()

    return render(request, 'rookscore/player.html',
                  {
                      'player': player,
                      'all_players': all_players,
                      'recent_games': recent_games,
                      'finishes': finishes,
                      'player_awards': player_awards,
                      'current_season': current_season
                  })


def data(request):
    template = loader.get_template('rookscore/data.html')
    context = RequestContext(request, {

    })

    return HttpResponse(template.render(context))


# Old render time was on the scale of ~50 seconds...
def awards(request):
    start = datetime.now()

    # A list of "Awards", where an award has an ordered list of players
    current_season = Season.objects.current()

    # A dict of type -> List of AT
    award_totals = AwardTotals.objects.group_by_type(current_season)

    # Prepare by type
    awards_list = AwardCache().all()
    for a in awards_list:
        if a.name in award_totals.keys():
            # Sets the data and sorts
            a.set_data(award_totals[a.name])

    template = loader.get_template('rookscore/awards.html')
    context = RequestContext(request, {
        'awards': awards_list,
        'current_season': current_season,
        'all_players': Player.objects.all_as_dict()
    })

    end = datetime.now()
    print(str(end - start) + ' seconds to generate awards')

    return HttpResponse(template.render(context))


#
# Repairs!
#
def repair_seasons(request):
    for g in Game.objects.all():
        Season.objects.get_or_create(g.played_date)


#
# Repairs!
#
def repair_awards(request):
    # Clear all awards
    for at in AwardTotals.objects.all():
        at.delete()

    # Try with just latest game, for now
    games = Game.objects.all()  # latest('played_date')

    for g in games:
        game_save_handler(instance=g)


#
# Django Rest Framework APIS
#

# GAMES

class GameDetail(generics.RetrieveAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameList(generics.ListCreateAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Game.objects.all()
    serializer_class = GameSerializer


class RawGameList(generics.ListAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Game.objects.all()
    serializer_class = RawGameSerializer


class RawScoreList(generics.ListAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = PlayerGameSummary.objects.all()
    serializer_class = RawScoreSerializer


class RawBidList(generics.ListAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Bid.objects.all()
    serializer_class = RawBidSerializer


class RawPlayerList(generics.ListAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Player.objects.all()
    serializer_class = RawPlayerSerializer


# PLAYERS

class PlayerDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


# SCORES
class ScoreDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = PlayerGameSummary.objects.all()
    serializer_class = ScoreSerializer


class ScoreList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = PlayerGameSummary.objects.all()
    serializer_class = ScoreSerializer


# BIDS
class BidDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Bid.objects.all()
    serializer_class = BidSerializer


class BidList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Bid.objects.all()
    serializer_class = BidSerializer
