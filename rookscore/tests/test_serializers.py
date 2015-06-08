from django.utils import unittest
from django.test import TestCase
from rookscore.models import Game, Player, PlayerGameSummary, Bid
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APIRequestFactory
from django.core.urlresolvers import reverse
from rest_framework import status

class GameSerializerTest(TestCase):
    def setUp(self):
        Player.objects.create(player_id=1001, first_name='Brad', last_name='C')
        Player.objects.create(player_id=1002, first_name='Chris', last_name='P')
        Player.objects.create(player_id=1003, first_name='Sean', last_name='W')
        Player.objects.create(player_id=1004, first_name='Martin', last_name='V')
        User.objects.create(username='testuser', first_name='Brad', last_name='C', password='password')

    def test_game_upload(self):
        client = APIClient()

        client.force_authenticate(user=User.objects.get(id=1))
        
        #login_reponse = client.login(username='testuser', password='password')
        #print login_reponse
        data = {
            "entered_date": "2012-01-05T19:33:37Z", 
            "played_date": "2012-01-03T00:00:00Z", 
            "scores": [
                {
                    "player": 1, 
                    "rank": 1, 
                    "score": 180, 
                    "made_bid": True
                }, 
                {
                    "player": 2, 
                    "rank": 2, 
                    "score": 180, 
                    "made_bid": False
                }, 
                {
                    "player": 3, 
                    "rank": 3, 
                    "score": 0, 
                    "made_bid": False
                }, 
                {
                    "player": 4, 
                    "rank": 4, 
                    "score": 0, 
                    "made_bid": False
                },
            ], 
            
            "bids": [
                {
                    "caller": 4, 
                    "partners": [ 1 ],
                    "opponents": [ 2, 3 ], 
                    "points_bid": 150, 
                    "points_made": 180,
                    "hand_number": 1,
                    "made_bid":True
                }
            ]
        }
        
        response = client.post('/api/games/', data)
        print response.content
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PlayerSerializerTest(TestCase):
    def setUp(self):
        Player.objects.create(player_id=1001, first_name='Brad', last_name='C')
        Player.objects.create(player_id=1002, first_name='Chris', last_name='P')
        Player.objects.create(player_id=1003, first_name='Sean', last_name='W')
        Player.objects.create(player_id=1004, first_name='Martin', last_name='V')
        
    def test_player_list(self):
        client = APIClient()
        
        #url = reverse('api-players')
        #url = reverse('api-player-detail', pk=24)
        
        #data = { 
        #    'players': [] 
        #}
        response = client.get('/api/players/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{'id': 1, 'player_id': 1001, 'first_name': u'Brad', 'last_name': u'C'},
            {'id': 2, 'player_id': 1002, 'first_name': u'Chris', 'last_name': u'P'},
            {'id': 4, 'player_id': 1004, 'first_name': u'Martin', 'last_name': u'V'},
            {'id': 3, 'player_id': 1003, 'first_name': u'Sean', 'last_name': u'W'}])