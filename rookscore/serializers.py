from django.forms import widgets
from rest_framework import serializers
from rookscore.models import Game, Player, PlayerGameSummary, Bid, Season
from rest_framework import routers, serializers, viewsets

from rookscore import utils

import logging

# Get an instance of a logger
from rookscore.receivers import game_save_handler

logger = logging.getLogger('rook2_beta')


# Serializers define the API representation.
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'player_id', 'first_name', 'last_name')

    # # We really just need the ID
    # def validate(self, data):
    #     logger.debug(data)
    #     return data['id']

# ViewSets define the view behavior.
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

#
# For whatever reason I made it so that the "Scores" player sends extra data - I assume so that on-demand adding of
# players was possible
#
# Handling that requires a special lookup, since we really only care about the ID.  Maybe in a future version of the
# app this can be cleaned up, and making this method sopport either type may help the transition...
#
class PlayerDetailedLookupField(serializers.RelatedField):
    # The only time we return this field is in a 201 after a successful create.  Returning None should have no
    # practical impact.
    def to_representation(self, value):
        return None

    def to_internal_value(self, data):
        logger.debug('Converting player to internal value')
        logger.debug(data)
        return Player.objects.get(pk=data['id'])


class ScoreSerializer(serializers.ModelSerializer):
    player = PlayerDetailedLookupField(queryset=Player.objects.all())

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
    scores = ScoreSerializer(many=True)
    bids = BidSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'entered_date', 'played_date', 'scores', 'bids')

    def create(self, validated_data):
        # print(validated_data)

        scores_data = validated_data.pop('scores')
        bids_data = validated_data.pop('bids')
        game = Game.objects.create(**validated_data)
        logger.debug("Created game: " + str(game))

        summaries = []

        for bid_data in bids_data:
            logger.debug("Creating bid: " + str(bid_data))
            # Bid.objects.create(game=game, **bid_data)
            b = Bid()
            b.game = game
            b.caller = bid_data['caller']
            b.points_bid = bid_data['points_bid']
            b.points_made = bid_data['points_made']
            b.save()

            # Apparently you need to save the bid before creating the many-to-many fields
            # Makes some sense, but the errors were pretty useless...
            b.partners = bid_data['partners']
            b.opponents = bid_data['opponents']
            b.save()
            # Bid.objects.create(game=game, 
            #     caller=bid_data['caller'], 
            #     partners=bid_data['partners'],
            #     opponents=bid_data['opponents'],
            #     points_bid=bid_data['points_bid'],
            #     points_made=bid_data['points_made'],
            #     bid=10
            # )


            pass
        for score_data in scores_data:
            logger.debug(str(score_data))

            summary = PlayerGameSummary.objects.create(game=game, **score_data)
            summaries.append(summary)

        # Write a utility to generate ranks and apply them, given a list of summaries - link to the HTML entry
        utils.sortAndRankSummaries(summaries)

        for s in summaries:
            s.save()

        # Calculate the new ELO

        # Load the "old ratings" from the ratings award - a bit hacky, but it results in the updating of the summaries
        Player.objects.rankings(Season.objects.get_or_create(game.played_date))

        # Reload
        game_save_handler(Game.objects.get(id=game.id))

        return game


# ViewSets define the view behavior.
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
