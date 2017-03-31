from trueskill import Rating, rate, TrueSkill

from rookscore import models


def _getScore(summary):
    if summary.made_bid:
        return 10000 + summary.score
    return summary.score


# Given a list of things and a key function to derive the value key, give things a rank
def rank(sorted_list, key):
    last_value = None
    last_rank = None
    count = 0

    for item in sorted_list:
        count = count + 1

        value = key(item)
        if value == last_value:
            # It's a tie, give the last rank
            item.rank = last_rank
            continue

        item.rank = count

        last_rank = count
        last_value = value


def sortAndRankSummaries(summaries):
    summaries.sort(reverse=True, key=_getScore)

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
        index += 1


def _getTrueskill(player):
    return player.trueskill


def _getRating(player):
    return player.rating


def sortAndRankPlayers(players, rating_system):
    if (rating_system == models.ELO):
        players = sorted(players, reverse=True, key=_getRating)
    else:
        players = sorted(players, reverse=True, key=_getTrueskill)

    index = 1
    last_rating = -10000
    last_rank = 1
    for p in players:
        if p.rating == last_rating:
            p.rank = last_rank
        else:
            p.rank = index

        last_rating = p.rating
        last_rank = p.rank
        index += 1

    return players


def _win_func(value):
    # Currently inverse log
    return 10.0 ** (value / 600.0)


def update_trueskill(scores, ratings):
    env = TrueSkill()

    # Parallel arrays!  All of these are for the given game
    players = []
    teams = []
    ranks = []
    expose_before = {}

    # Sanity check, some bad data in test systems
    if len(scores) < 4:
        return

    for s in scores:
        if s.player_id not in ratings.keys():
            ratings[s.player_id] = Rating()  # Default mu=25, sigma=8.333

        r = ratings[s.player_id]
        expose_before[s.player_id] = env.expose(r)
        players.append(s.player_id)
        teams.append([r])
        ranks.append(s.rank)

    # Crunch the numbers
    new_ratings = rate(teams, ranks)

    for i in range(0, len(new_ratings)):
        ratings[players[i]] = new_ratings[i][0]

    for s in scores:
        s.trueskill = ratings[s.player_id].mu
        s.trueskill_confidence = ratings[s.player_id].sigma
        s.trueskill_change = env.expose(ratings[s.player_id]) - expose_before[s.player_id]
        s.save()
        # for s in scores:
        #     # Determine if this is the first time that the score has been calculated - if so, save
        #
        #     rating_change = 0
        #     new_rating = ratings[s.player_id] + rating_change
        #
        #     if (s.rating != round(new_rating) or s.rating_change != round(rating_change)):
        #         s.rating = round(new_rating)
        #         s.rating_change = round(rating_change)
        #         s.save()
        #
        #     ratings[s.player_id] = new_rating


def update_elo(scores, ratings):
    # Some ELO constants
    exp = {}
    exp[3] = [0.79, 0.21, 0.0]
    exp[4] = [0.68, 0.24, 0.08, 0.0]
    exp[5] = [0.6, 0.25, 0.11, 0.04, 0.0]
    exp[6] = [0.55, 0.24, 0.12, 0.06, 0.03, 0.0]
    exp[7] = [0.51, 0.23, 0.13, 0.07, 0.04, 0.02, 0.0]

    player_count = len(scores)

    default_weights = {}
    rank_weights = {}

    for r in range(0, player_count):
        default_weights[r + 1] = exp[player_count][r]

    min = 999.9
    tot = 0.0

    for s in scores:
        if s.player_id not in ratings.keys():
            ratings[s.player_id] = 1200

    # Loop over each rank
    for r in range(1, 9):
        scores_at_rank = []
        for s in scores:
            if s.rank == r:
                scores_at_rank.append(s)
        count = len(scores_at_rank)

        if count == 0:
            # Nobody at this rank
            continue

        tot_weight = 0.0

        # Compare to everyone below you
        for r2 in range(r, r + count):
            tot_weight = tot_weight + default_weights[r2]

        avg_weight = tot_weight / (count * 1.0)
        rank_weights[r] = avg_weight
        if avg_weight < min:
            min = avg_weight
        tot += avg_weight * count

    tot -= min * scores.count()

    bot = 0
    for s in scores:
        bot += _win_func(ratings[s.player_id])

    K = len(scores) * 10

    for s in scores:
        top = _win_func(ratings[s.player_id])
        expected = top / bot
        actual = (rank_weights[s.rank] - min) / tot
        # actual = 0.0
        # if pig.rank == 1:
        #    actual = 1.0

        # Determine if this is the first time that the score has been calculated - if so, save
        precalc_rating = s.rating
        precalc_rating_change = s.rating_change

        rating_change = (K * (actual - expected))
        new_rating = ratings[s.player_id] + rating_change

        if (s.rating != round(new_rating) or s.rating_change != round(rating_change)):
            s.rating = round(new_rating)
            s.rating_change = round(rating_change)
            s.save()

        ratings[s.player_id] = new_rating

    '''
    for s in game.scores.all():
        # These should be in order by rank
        if s.player not in ratings.keys():
            ratings[s.player] = player_count - s.rank
        else:
            ratings[s.player] = ratings[s.player] + player_count - s.rank
    '''


'''
    def calculate_ratings(self):
#        if players > 0:
#            games = Game.objects.order_by('date').filter(num_players=players)
#        else:
#            games = Game.objects.order_by('date')
#        if date_end:
#            games = games.filter(date__lte=date_end)
        
        games = Game.objects.order_by('date')
        
        rat = {}
        exp = {}
        exp[3] = [0.79, 0.21, 0.0]
        exp[4] = [0.68, 0.24, 0.08, 0.0]
        exp[5] = [0.6, 0.25, 0.11, 0.04, 0.0]
        exp[6] = [0.55, 0.24, 0.12, 0.06, 0.03, 0.0]
        exp[7] = [0.51, 0.23, 0.13, 0.07, 0.04, 0.02, 0.0]
        
        for p in Player.objects.all():
            rat[p] = 1200.0
            
        for g in games:
            bot = 0
            pigs = g.get_records() # pigs
            
            default_weights = {}
            rank_weights = {}

            for r in range(0, g.num_players):
                default_weights[r+1] = exp[g.num_players][r]
            
            min = 999.9
            tot = 0.0
  
            for r in range(1, 9):
                pigs_at_rank = []
                for pig in pigs:
                    if pig.rank == r:
                        pigs_at_rank.append(pig)
                count = len(pigs_at_rank)
                if count == 0:
                    continue
                
                tot_weight = 0.0
                
                for r2 in range(r, r+count):
                    tot_weight = tot_weight + default_weights[r2]
                    
                avg_weight = tot_weight / (count * 1.0)
                rank_weights[r] = avg_weight
                if avg_weight < min:
                    min = avg_weight
                tot = tot + (avg_weight * count)
                
            tot = tot - (min * pigs.count())
                
            for pig in pigs:
                bot = bot + RatingManager.win_func(self, rat[pig.player])
            
            K = pigs.count() * 10
                            
            for pig in pigs:
                top = RatingManager.win_func(self, rat[pig.player])
                expected = top / bot
                actual = (rank_weights[pig.rank] - min)/tot
                #actual = 0.0
                #if pig.rank == 1:
                #    actual = 1.0

                new_rating = rat[pig.player] + (K * (actual - expected))

                pig.rating_change = new_rating - rat[pig.player]
                pig.rating = new_rating
                pig.save()
                
                rat[pig.player] = new_rating

                #rat[pig.player] = get_rating    return rat
            

'''
