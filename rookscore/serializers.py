from django.forms import widgets
from rest_framework import serializers
from rookscore.models import Game, Player, PlayerGameSummary, Bid
from rest_framework import routers, serializers, viewsets

from rookscore import utils

# Serializers define the API representation.
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'player_id', 'first_name', 'last_name')

# ViewSets define the view behavior.
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class ScoreSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = PlayerGameSummary
        fields = ('id', 'player', 'rank', 'score', 'made_bid')
        
class ScoreViewSet(viewsets.ModelViewSet):
    queryset = PlayerGameSummary.objects.all()
    serializer_class = ScoreSerializer

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('caller', 'partners', 'opponents', 'points_bid', 'points_made')

class GameSerializer(serializers.ModelSerializer):
    #    scores = serializers.HyperlinkedRelatedField(many=True, view_name='score-detail')
    #scores = serializers.RelatedField(many=True)
    scores = ScoreSerializer(many=True)
    bids = BidSerializer(many=True)

    def create(self, validated_data):
        #print '***** SERIALIZING GAME ********'

        scores_data = validated_data.pop('scores')
        bids_data = validated_data.pop('bids')
        game = Game.objects.create(**validated_data)
        summaries = []
        
        for bid_data in bids_data:
            Bid.objects.create(game=game, **bid_data)
        for score_data in scores_data:    
            player_data = score_data.pop('player')
            print 'Player Data:', player_data
            player = Player.objects.get(player_id=player_data['player_id'])
            summary = PlayerGameSummary.objects.create(game=game, player=player, **score_data)
            summaries.append(summary)
        # Write a utility to generate ranks and apply them, given a list of summaries - link to the HTML entry
        utils.sortAndRankSummaries(summaries)
        
        for s in summaries:
            s.save()

        return game
    
    class Meta:
        model = Game
        fields = ('id', 'entered_date', 'played_date', 'scores', 'bids')
        
# ViewSets define the view behavior.
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    
