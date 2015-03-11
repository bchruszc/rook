from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render
from django.forms.formsets import formset_factory

from rookscore.forms import PlayerForm
from rookscore.models import Player, Game, PlayerGameSummary, Bid
from rookscore.serializers import GameSerializer, PlayerSerializer, ScoreSerializer, BidSerializer
from rookscore import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions

import datetime
from rookscore import utils

def index(request):
    rankings = Player.objects.rankings(month=3, year=2015)
    recent_game_list = Game.objects.order_by('-played_date')[:5]
    template = loader.get_template('rookscore/index.html')
    context = RequestContext(request, {
        'rankings': rankings,
        'recent_game_list':recent_game_list,
        'settings': settings,
    })
    return HttpResponse(template.render(context))



def entry(request):
    if request.method == 'POST': # If the form has been submitted...
        # ContactForm was defined in the previous section
        form = PlayerForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # Great, a legit game!  Let's save it
            
            game = Game()
            game.played_date = form.cleaned_data['game_date']
            game.entered_date = datetime.datetime.now()
            game.save()
            
            summaries = []
            scores = []
            
            for i in range (1,7):
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
            
            return HttpResponseRedirect('/') # Redirect after POST
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
    for g in Game.objects.all():
        summaries = list(g.scores.all())
        utils.sortAndRankSummaries(summaries)

        for s in summaries:
            s.save() 
    return HttpResponse("<html><body>Repair complete.</body></html>")


def games(request):
    games_list = Game.objects.order_by('-entered_date')[:5]
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

def players(request):
    players_list = Player.objects.order_by('first_name')
    template = loader.get_template('rookscore/players.html')
    context = RequestContext(request, {
        'players_list': players_list,
    })
    return HttpResponse(template.render(context))

def player(request, player_id):
    return HttpResponse("You have requested player #" + str(player_id))

def awards(request):
    award_list = []
    template = loader.get_template('rookscore/awards.html')
    context = RequestContext(request, {
        'award_list': award_list,
    })
    return HttpResponse(template.render(context))


#
# APIS
#

# GAMES

class GameDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    
class GameList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    queryset = Game.objects.all()
    serializer_class = GameSerializer

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