import bayesian_agent.markovian as markov
mse = 0
guess = -1
belief = None
has_updated = False

def markovian_agent1(args, value, num_aces):
    # args: (player_choices, choice_list, (card1, card2))

    # always hit when you have less than 12
    if value <= 11:
        return 1
    
    if markov.belief is None:
        markov.belief = {2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 12, 11: 3}

    player_choices = args[0]
    choice_list = args[1]
    card1, card2 = args[2]

    if not markov.has_updated:
        parse_player_choices(choice_list)
        markov.belief[card1] += 1
        markov.belief[card2] += 1
        markov.has_updated = True

    prob_dict = {key: value / sum(markov.belief.values()) for key, value in markov.belief.items()}
    print(prob_dict)
    dealer_probabilities = calculate_dealer_probabilities(choice_list, player_choices, prob_dict)
    print(dealer_probabilities)

    choices = [0, 0]
    for key, val in dealer_probabilities.items():
        ret = calculate_move_dp(key, prob_dict, value)
        for i in [0, 1]:
            choices[i] += ret[i] * val

    markov.guess = max(dealer_probabilities, key=dealer_probabilities.get)

    if choices[0] > choices[1]:
        return 0
    else:
        return 1
    
def markovian_agent2(args, value, num_aces):
    # args: (player_choices, choice_list, (card1, card2))

    # always hit when you have less than 12
    if value <= 11:
        return 1
    
    if markov.belief is None:
        markov.belief = {2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 12, 11: 3}

    player_choices = args[0]
    choice_list = args[1]
    card1, card2 = args[2]

    if not markov.has_updated:
        parse_player_choices(choice_list)
        markov.belief[card1] += 1
        markov.belief[card2] += 1
        markov.has_updated = True

    expected_cards = {key: value * 52 / sum(markov.belief.values()) for key, value in markov.belief.items()}
    expected_cards[card1] = max(expected_cards[card1]-1, 0)
    expected_cards[card2] = max(expected_cards[card2]-1, 0)
    for p in choice_list:
        # not a hit
        if p[2] != 1:
            for card in p[3]:
                expected_cards[card] = max(expected_cards[card]-1, 0)
    
    prob_dict = {key: value / sum(expected_cards.values()) for key, value in expected_cards.items()}
    print(prob_dict)
    dealer_probabilities = calculate_dealer_probabilities(choice_list, player_choices, prob_dict)
    print(dealer_probabilities)

    choices = [0, 0]
    for key, val in dealer_probabilities.items():
        ret = calculate_move_dp(key, prob_dict, value)
        for i in [0, 1]:
            choices[i] += ret[i] * val

    markov.guess = max(dealer_probabilities, key=dealer_probabilities.get)

    if choices[0] > choices[1]:
        return 0
    else:
        return 1

true_card = -1
def markovian_agent3(args, value, num_aces):
    # args: (player_choices, choice_list, (card1, card2))

    # always hit when you have less than 12
    if value <= 11:
        return 1
    
    if markov.belief is None:
        markov.belief = {2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 12, 11: 3}

    player_choices = args[0]
    choice_list = args[1]
    card1, card2 = args[2]

    if not markov.has_updated:
        parse_player_choices(choice_list)
        markov.belief[card1] += 1
        markov.belief[card2] += 1
        markov.has_updated = True

    expected_cards = {key: value * 52 / sum(markov.belief.values()) for key, value in markov.belief.items()}
    cards_left = 50
    expected_cards[card1] = max(expected_cards[card1]-1, 0)
    expected_cards[card2] = max(expected_cards[card2]-1, 0)
    for p in choice_list:
        # not a hit
        if p[2] != 1:
            for card in p[3]:
                expected_cards[card] = max(expected_cards[card]-1, 0)
                cards_left -= 1
    
    prob_dict = {key: value / sum(expected_cards.values()) for key, value in expected_cards.items()}
    dealer_probabilities = calculate_dealer_probabilities(choice_list, player_choices, prob_dict)

    ret = calculate_move_dp2(dealer_probabilities, prob_dict, value)
    markov.guess = max(dealer_probabilities, key=dealer_probabilities.get)

    if ret[0] > ret[1]:
        return 0
    else:
        return 1

def calculate_dealer_probabilities(choice_list, player_choices, prob_dict):
    # returns probability first dealer card is each card
    # P(dealer = X | p1, p2, p3, p4, p5)
    # = P(p1, p2, p3, p4, p5 | dealer = X) P(dealer = X) / P(p1, p2, p3, p4, p5)
    # = P(p1 | dealer = X) ... P(p5 | dealer = X) P(dealer = X) / Sum Across Cards(p1, ..., p5 | card) P(card)
    
    # denominator: Sum Across All Cards P(p1 | card) P(p2 | card) ... P(p5 | card) P(card)

    if len(choice_list) == 0:
        return prob_dict

    return_dict = {}

    prob_observations = 0

    for dcard in prob_dict:
        prob_step = prob_dict[dcard]
        for choice in choice_list:
            if choice[2] == 2:
                continue
            choice_prob = player_choices[dcard][choice[0]][choice[1]]
            if choice[2] == 0:
                #if (1 - choice_prob) == 0:
                    #print("ZERO STAND", dcard, choice[0], choice[1])
                prob_step *= (1 - choice_prob)
            elif choice[2] == 1:
                #if choice_prob == 0:
                    #print("ZERO HIT", dcard, choice[0], choice[1])
                prob_step *= choice_prob

        return_dict[dcard] = prob_step
        prob_observations += prob_step

    return_dict = {key: value / prob_observations for key, value in return_dict.items()}

    return return_dict

def calculate_move_dp(dealer_card, prob_dict, value):
    prob_dealer_ends_with = {dealer_card: 1.0}
    for i in range(dealer_card + 1, 23):
        prob_dealer_ends_with[i] = 0.0
    
    for cur in range(dealer_card, 17):
        for key, val in prob_dict.items():
            if key == 11:
                if cur > 10:
                    prob_dealer_ends_with[min(cur + 1, 22)] += prob_dealer_ends_with[cur] * val
                else:
                    prob_dealer_ends_with[min(cur + 11, 22)] += prob_dealer_ends_with[cur] * val
            else:
                prob_dealer_ends_with[min(cur + key, 22)] += prob_dealer_ends_with[cur] * val

    dp = {i: [0, 0] for i in range(value, 22)}
    dp[21][0] = 1 - prob_dealer_ends_with[21]
    dp[21][1] = -1
    for card in range(20, value-1, -1):
        if card > 16:
            # standing is as good as standing on the card above, except the dealer can now beat you/tie you more often
            dp[card][0] = dp[card+1][0] - prob_dealer_ends_with[card] - prob_dealer_ends_with[card+1]
        elif card == 16:
            # the dealer will never stand on a 16
            dp[card][0] = dp[card+1][0] - prob_dealer_ends_with[card+1]
        else:
            # you will do as well as the card above you since the dealer won't stand on a 16 or below
            dp[card][0] = dp[card+1][0]
        
        for key, val in prob_dict.items():
            if key == 11:
                if card <= 10:
                    dp[card][1] += max(dp[card+11][0], dp[card+11][1]) * val
                else:
                    dp[card][1] += max(dp[card+1][0], dp[card+1][1]) * val
            elif card + key > 21:
                dp[card][1] -= val
            else:
                dp[card][1] += max(dp[card+key][0], dp[card+key][1]) * val

    return dp[value]

def calculate_move_dp2(dealer_probs, prob_dict, value):
    prob_dealer_ends_with = {}
    for i in range(0, 23):
        for j in [0, 1, 2]:
            for k in [0, 1, 2]:
                prob_dealer_ends_with[(i, j, k)] = 0.0

    for dealer_card, prob in dealer_probs.items():
        prob_dealer_ends_with[(dealer_card, dealer_card == 11, 0)] = prob
    
    for num_aces in [0, 1, 2]:
        nx_aces = min(num_aces+1, 2)
        for aces_used in [0, 1, 2]:
            nx_used = min(aces_used+1, 2)
            for cur in range(0, 17):
                for key, val in prob_dict.items():
                    if key == 11:
                        if cur > 10:
                            prob_dealer_ends_with[(cur+1, nx_aces, nx_used)] += prob_dealer_ends_with[(cur, num_aces, aces_used)] * val
                        else:
                            prob_dealer_ends_with[(cur+1, nx_aces, aces_used)] += prob_dealer_ends_with[(cur, num_aces, aces_used)] * val
                    elif cur + key > 21 and num_aces > aces_used:
                        prob_dealer_ends_with[(cur+key-10, num_aces, aces_used+1)] += prob_dealer_ends_with[(cur, num_aces, aces_used)] * val
                    elif cur + key <= 21:
                        prob_dealer_ends_with[(cur+key, num_aces, aces_used)] += prob_dealer_ends_with[(cur, num_aces, aces_used)] * val

    compact = {}
    for i in range(dealer_card, 23):
        compact[i] = 0
        for j in [0, 1, 2]:
            for k in [0, 1, 2]:
                compact[i] += prob_dealer_ends_with[(i, j, k)]
    prob_dealer_ends_with = compact

    dp = {(i,j,k): [0, 0] for k in range(3) for j in range(3) for i in range(0, 22)}
    for j in range(3):
        for k in range(3):
            dp[(21,j,k)][0] = 1 - prob_dealer_ends_with[21]
            dp[(21,j,k)][1] = -1

    for num_aces in [2, 1, 0]:
        nx_aces = min(num_aces+1, 2)
        for aces_used in [2, 1, 0]:
            nx_used = min(aces_used+1, 2)
            for card in range(20, value-1, -1):
                if card > 16:
                    # standing is as good as standing on the card above, except the dealer can now beat you/tie you more often
                    dp[(card, num_aces, aces_used)][0] = dp[(card+1, num_aces, aces_used)][0] - prob_dealer_ends_with[card] - prob_dealer_ends_with[card+1]
                elif card == 16:
                    # the dealer will never stand on a 16
                    dp[(card, num_aces, aces_used)][0] = dp[(card+1, num_aces, aces_used)][0] - prob_dealer_ends_with[card+1]
                else:
                    # you will do as well as the card above you since the dealer won't stand on a 16 or below
                    dp[(card, num_aces, aces_used)][0] = dp[(card+1, num_aces, aces_used)][0]
                
                for key, val in prob_dict.items():
                    if key == 11:
                        if card <= 10:
                            nx = dp[(card+11, nx_aces, aces_used)]
                            dp[(card, num_aces, aces_used)][1] += max(nx[0], nx[1]) * val
                        else:
                            nx = dp[(card+1, nx_aces, nx_used)]
                            dp[(card, num_aces, aces_used)][1] += max(nx[0], nx[1]) * val
                    elif card + key > 21:
                        if aces_used < num_aces:
                            nx = dp[(card+key-10, num_aces, nx_used)]
                            dp[(card, num_aces, aces_used)][1] += max(nx[0], nx[1]) * val
                        else:
                            dp[(card, num_aces, aces_used)][1] -= val
                    else:
                        nx = dp[(card+key, num_aces, aces_used)]
                        dp[(card, num_aces, aces_used)][1] += max(nx[0], nx[1]) * val

    return dp[(value, value==11, 0)]

def parse_player_choices(choice_list):
    for p in choice_list:
        # not a hit, so we can add the cards to the pile
        if p[2] != 1:
            for card in p[3]:
                markov.belief[card] += 1