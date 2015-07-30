'''

This class defines the API for the application

'''

from __future__ import print_function


from django.db import transaction
from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer
from restless.serializers import JSONSerializer

from rookscore.models import Player, Game, PlayerGameSummary, Bid
from rookscore import utils
from datetime import datetime


import json
import logging

logger = logging.getLogger('rook2_beta')


# A serializer that strips out the object map surrounding lists
class NoWrapSerializer(JSONSerializer):
    
    def serialize(self, data):
        if isinstance(data, dict) and 'objects' in data.keys():
            data = data['objects']

        return JSONSerializer.serialize(self, data)
        
class PlayerResource(DjangoResource):
    serializer = NoWrapSerializer()
    
    # exposed_name : internal_name
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'player_id': 'player_id',
        'first_name': 'first_name',
        'last_name': 'last_name',
    })

    # GET /api2/players/
    def list(self):
        logger.debug('Player List Request...')
        logger.debug(self.data)
        return list(Player.objects.all())

    # GET /api2/posts/<pk>/
    def detail(self, pk):
        return Player.objects.get(id=pk)
        
class GameResource(DjangoResource):
    serializer = NoWrapSerializer()
    
    # exposed_name : internal_name
    preparer = FieldsPreparer(fields={
        'id': 'id',
        #'player_id',
        'played_date': 'played_date',
        'entered_date': 'entered_date',
        'scores': 'scores_loaded',
    })
    
    # Add this (API key)
    #pylint: disable=maybe-no-member
    def is_authenticated(self):
        if 'HTTP_API_KEY' in self.request.META.keys():
            key = self.request.META['HTTP_API_KEY']
            if key == '12345':
               # print 'Secure:', key;
                return True
                
        # TODO: Don't always return true!!
        return True
            
    # GET /api2/games/
    def list(self):
        games = Game.objects.all()
        
        for g in games:
            serialize_game(g)
            
        return list(games)

    # GET /api2/games/<pk>/
    def detail(self, pk):
        g = Game.objects.get(id=pk)
        serialize_game(g)
        return g
        
    # POST /api2/games/
    @transaction.commit_on_success
    def create(self):
        logger.debug('Game Upload...')
        logger.debug(self.data)
        
        try:
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
                #print 'Computing scores...'
    
                for s in scores:
                    p = plyr(s['player']['id'])
                    new_scores.append(PlayerGameSummary(player=p, game=new_game, score=s['score'], made_bid=s['made_bid']))
    
            if bids and len(bids) > 0:
                #print 'Computing bids...'
                for b in bids:
                    #print 'Bid: ', b
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
       
            #print 'Game validated:'
            #print new_game
            
            utils.sortAndRankSummaries(new_scores)
    
            for s in new_scores:
                #print s
                s.game = new_game
                s.save()
            for b in new_bids:
                #print b
                b.game = new_game
                b.save()
                
        except Exception, e:
            print(e)
            logger.error(e)
            raise e

def serialize_game(g):
    g.scores_loaded = len(g.scores.all())

def plyr(player_id):
    return Player.objects.get(pk=int(player_id))