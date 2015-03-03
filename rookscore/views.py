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

def index(request):
    player_list = Player.objects.order_by('-first_name')[:5]
    template = loader.get_template('rookscore/index.html')
    context = RequestContext(request, {
        'player_list': player_list,
        'settings': settings,
    })
    return HttpResponse(template.render(context))

def getScore(summary):
    if summary.made_bid:
        return 10000 + summary.score
    return summary.score

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
            
            summaries.sort(reverse=True, key=getScore)
            
            # Need to take in to consideration STAR, and get the rank
            last_score = -100000;
            last_rank = 1;
            last_made_bid = summaries[0].made_bid
            index = 1;
            for s in summaries:
                if s.score == last_score and s.made_bid == last_made_bid:
                    s.rank = last_rank
                else:
                    s.rank = index
                
                last_score = s.score
                last_rank = s.rank
                last_made_bid = s.made_bid
                index = index + 1
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