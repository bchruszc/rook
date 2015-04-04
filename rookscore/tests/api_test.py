# /usr/bin/python

#
#  An attempt to test the REST API.  Don't invoke anything natively - this should simulate and external application
#

import sys
import getopt
import requests
import json

root_url = 'http://beta.rook2.chruszcz.ca/api/'

def test_player_list():
    print 'Testing player list...'
    print '* Test Not Implemented'
    headers = {'content-type': 'application/json'}
    r = requests.get(root_url + 'players/', headers=headers) #), data) #, auth=('user', '*****'))    
    print r.headers
    print r.cookies
    print r.json()
    print '--'
    
def test_player_detail():
    print 'Testing player detail...'
    print '* Test Not Implemented'
    
def test_game_list():
    print 'Testing game list...'
    print '* Test Not Implemented'
    
def test_game_detail():
    print 'Testing game detail...'
    print '* Test Not Implemented'

def test_player_put():
    print 'Testing player put...'
    print '* Test Not Implemented'
    
def test_game_put():
    print 'Testing game put...'
    headers = {'content-type': 'application/json'}

    r = requests.get('http://beta.rook2.chruszcz.ca/api-auth/login/', headers=headers, auth=('bchruszc', 'leafs321'))    
    print r.text
    print r.headers
    print r.cookies
    print 'csrftoken: ' + r.cookies['csrftoken']
    print '---'
    cookies = r.cookies
    
    headers = {'content-type': 'application/json'}
    
    # data = json.dumps({
    #     "entered_date": "2015-03-05T19:33:37Z", 
    #     "played_date": "2015-03-03T00:00:00Z", 
    # })
    
    data = json.dumps({
        "entered_date": "2015-03-05T19:33:37Z", 
        "played_date": "2015-03-03T00:00:00Z", 
        "scores": [
            {
                "player": {
                    "player_id": 31312, 
                    "first_name": "Martin", 
                    "last_name": "Varady"
                }, 
                "rank": 1, 
                "score": 1210, 
                "made_bid": True
            }, 
            {
                "player": {
                    "player_id": 1234, 
                    "first_name": "Chris", 
                    "last_name": "Pope"
                }, 
                "rank": 2, 
                "score": 1100, 
                "made_bid": True
            }, 
            {
                "player": {
                    "player_id": 132421, 
                    "first_name": "Jeremy", 
                    "last_name": "van der Munnik"
                }, 
                "rank": 3, 
                "score": 705, 
                "made_bid": True
            }, 
            {
                "id": 4, 
                "player": {
                    "player_id": 1234, 
                    "first_name": "Bradley", 
                    "last_name": "Chruszcz"
                }, 
                "rank": 4, 
                "score": 365, 
                "made_bid": True
            }, 
            {
                "id": 5, 
                "player": {
                    "player_id": 9988, 
                    "first_name": "Ray", 
                    "last_name": "Fung"
                }, 
                "rank": 5, 
                "score": 485, 
                "made_bid": False
            }, 
            {
                "player": {
                    "player_id": 1230, 
                    "first_name": "John", 
                    "last_name": "Kooistra"
                }, 
                "rank": 6, 
                "score": 345, 
                "made_bid": False
            }
        ], 
        "bids": []
    }) 
    r = requests.post(root_url + 'games/', auth=('bchruszc', 'leafs321'), data=data, cookies=cookies, headers=headers)
    print r.text

def run_tests():
    print 'Starting tests'
    
    #test_need_credentials_to_post_game()
    
    test_player_list()
    '''
    test_player_detail()
    test_game_list()
    test_game_detail()
    
    test_player_put()
    '''
    test_game_put()

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
    # process arguments
    #for arg in args:
    #    run_tests(arg) # process() is defined elsewhere
    run_tests()

if __name__ == "__main__":
    main()
    
