'''

This class defines the API for the application

'''

from django.db import transaction
from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from rookscore.models import Player, Game, PlayerGameSummary, Bid
from rookscore import utils
from datetime import datetime
import json

class PlayerResource(DjangoResource):
    # exposed_name : internal_name
    preparer = FieldsPreparer(fields={
        'id': 'id',
        #'player_id',
        'first_name': 'first_name',
        'last_name': 'last_name',
    })

    # GET /api2/players/
    def list(self):
        return Player.objects.all()

    # GET /api2/posts/<pk>/
    def detail(self, pk):
        return Player.objects.get(id=pk)
        
class GameResource(DjangoResource):
    # exposed_name : internal_name
    preparer = FieldsPreparer(fields={
        'id': 'id',
        #'player_id',
        'played_date': 'played_date',
        'entered_date': 'entered_date',
        'scores': 'scores_loaded',
    })
    
        # Add this!
    def is_authenticated(self):
        # Alternatively, if the user is logged into the site...
        return self.request.user.is_authenticated()

        # Alternatively, you could check an API key. (Need a model for this...)
        # from myapp.models import ApiKey
        # try:
        #     key = ApiKey.objects.get(key=self.request.GET.get('api_key'))
        #     return True
        # except ApiKey.DoesNotExist:
        #     return False

    # GET /api2/games/
    def list(self):
        games = Game.objects.all()
        
        for g in games:
            serialize_game(g)
            
        return games

    # GET /api2/games/<pk>/
    def detail(self, pk):
        g = Game.objects.get(id=pk)
        serialize_game(g)
        return g
        
    # POST /api2/games/
    @transaction.commit_on_success
    def create(self):
        print self.data        

        # Validate this game
        played_date = self.data['played_date']
        
        if not played_date:
            raise Exception('"played_date" not set')
            
        # If bids are present, use them.  Otherise scores
        bids = self.data['bids']
        scores = self.data['scores']

        # Create the base game
        new_game = Game(played_date=played_date, entered_date=datetime.now())
        new_game.save()

        new_scores = []
        new_bids = []

        if (not bids or len(bids) == 0) and (not scores or len(scores) == 0):
            raise Exception('either "bids" or "scores" must be specified')

        if scores and len(scores) > 0:
            print 'Computing scores...'

            for s in scores:
                p = plyr(s['player']['player_id'])
                new_scores.append(PlayerGameSummary(player=p, game=new_game, score=s['score'], made_bid=s['made_bid']))

        if bids and len(bids) > 0:
            print 'Computing bids...'
            for b in bids:
                print 'Bid: ', b
                new_bid = Bid()
                new_bid.game = new_game
                new_bid.points_bid = b['points_bid']
                new_bid.points_made = b['points_made']
                new_bid.caller = plyr(b['caller'])
                new_bid.hand_number = b['hand_number']

                # Need to save before we can link to partners and opponents
                new_bid.save()
                
                for p in b['partners']:
                    new_bid.partners.add(plyr(p))

                for o in b['opponents']:
                    new_bid.opponents.add(plyr(o))
                
                new_bids.append(new_bid)
                
            if len(new_scores) > 0:
                # Both bids and scores were provided - make sure they jive
                # TODO!
                pass
   
        print 'Game validated:'
        print new_game
        
        utils.sortAndRankSummaries(new_scores)

        for s in new_scores:
            print s
            s.game = new_game
            s.save()
        for b in new_bids:
            print b
            b.game = new_game
            b.save()

def serialize_game(g):
    g.scores_loaded = len(g.scores.all())

def plyr(player_id):
    return Player.objects.get(pk=int(player_id))