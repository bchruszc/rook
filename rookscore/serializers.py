from django.forms import widgets
from rest_framework import serializers
from rookscore.models import Game, Player, PlayerGameSummary, Bid
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('player_id', 'first_name', 'last_name')

# ViewSets define the view behavior.
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class ScoreSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    
    class Meta:
        model = PlayerGameSummary
        fields = ('player', 'score', 'made_bid')
        
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
        scores_data = validated_data.pop('scores')
        bids_data = validated_data.pop('bids')
        game = Game.objects.create(**validated_data)
        for bid_data in bids_data:
            Bid.objects.create(game=game, **bid_data)
        for score_data in scores_data:    
            player_data = score_data.pop('player')
            player = Player.objects.get(player_id=player_data['player_id'])
            PlayerGameSummary.objects.create(game=game, player=player, **score_data)
        return game
    
    class Meta:
        model = Game
        fields = ('entered_date', 'played_date', 'scores', 'bids')
        
# ViewSets define the view behavior.
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    
