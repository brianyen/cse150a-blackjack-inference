import bayesian_agent.bayesian as bayes
mse = 0
guess = -1

def bayesian_agent1(args, value, num_aces):
    # args: (player_choices, choice_list, (card1, card2))

    # always hit when you have less than 12
    if value <= 11:
        return 1
    
    player_choices = args[0]
    choice_list = args[1]
    card1, card2 = args[2]
    
    dealer_probabilities = calculate_dealer_probabilities(choice_list, player_choices)

    prob_dict2 = {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 16, 11: 4}
    num_cards_left = sum(prob_dict2.values())
    prob_dict2 = {key: value / num_cards_left for key, value in prob_dict2.items()}

    bayes.guess = max(dealer_probabilities, key=dealer_probabilities.get)
    choices = calculate_move_dp(bayes.guess, prob_dict2, value)

    if choices[0] > choices[1]:
        return 0
    else:
        return 1
    
def bayesian_agent2(args, value, num_aces):
    # args: (player_choices, choice_list, (card1, card2))

    # always hit when you have less than 12
    if value <= 11:
        return 1
    
    player_choices = args[0]
    choice_list = args[1]
    card1, card2 = args[2]
    
    dealer_probabilities = calculate_dealer_probabilities(choice_list, player_choices)
    prob_dict = {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 16, 11: 4}

    num_cards_left = sum(prob_dict.values())
    prob_dict = {key: value / num_cards_left for key, value in prob_dict.items()}
    choices = [0, 0]
    for key, val in dealer_probabilities.items():
        ret = calculate_move_dp(key, prob_dict, value)
        for i in [0, 1]:
            choices[i] += ret[i] * val

    bayes.guess = max(dealer_probabilities, key=dealer_probabilities.get)

    if choices[0] > choices[1]:
        return 0
    else:
        return 1

def calculate_dealer_probabilities(choice_list, player_choices):
    # returns probability first dealer card is each card
    # P(dealer = X | p1, p2, p3, p4, p5)
    # = P(p1, p2, p3, p4, p5 | dealer = X) P(dealer = X) / P(p1, p2, p3, p4, p5)
    # = P(p1 | dealer = X) ... P(p5 | dealer = X) P(dealer = X) / Sum Across Cards(p1, ..., p5 | card) P(card)
    
    # denominator: Sum Across All Cards P(p1 | card) P(p2 | card) ... P(p5 | card) P(card)

    prob_dict = {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 16, 11: 4}
    prob_dict = {key: value / 52 for key, value in prob_dict.items()}
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