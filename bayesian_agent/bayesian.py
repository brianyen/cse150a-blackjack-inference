def bayesian_round(args, value, num_aces):
    # args: (player_choices, choice_list, (card1, card2))
    player_choices = args[0]
    choice_list = args[1]
    card1, card2 = args[2]
    
    dealer_probabilities = calculate_dealer_probabilities(choice_list, player_choices)
    print("dealer probabilities:", dealer_probabilities)
    print("double check", sum([value for key, value in dealer_probabilities.items()]))
    print("highest probability", max(dealer_probabilities, key=dealer_probabilities.get)
)

    # will add decisions later

    """prob_hit = 0
    prob_stand = 0

    for c1, p_c1 in dealer_probabilities():
        if c1 == 11:
            # deal with aces
            return

        # calculate standing probabilty

    # P(win | hit)
    # = sum(card across drawable cards): P(win | card) P(card)
    # = sum(card across drawable cards):  P(v<=21, v>dealer | card) P(card)
    # = sum(card across drawable card)(dealer across drawable cards): P(v<=21, v>dealer| card, dealer) P(card) P(dealer | card)

    # P(win | stand)
    # = sum(card across drawable cards): P(win | card) P(card)
    # = sum(card across drawable cards): (P(v<=21, v>card+dealer | card) + P(card+dealer > 21))P(card)
    """
    return 0 # never gamble

def calculate_dealer_probabilities(choice_list, player_choices):
    # returns probability first dealer card is each card
    # P(dealer = X | p1, p2, p3, p4, p5)
    # = P(p1, p2, p3, p4, p5 | dealer = X) P(dealer = X) / P(p1, p2, p3, p4, p5)
    # = P(p1 | dealer = X) ... P(p5 | dealer = X) P(dealer = X) / Sum Across Cards(p1, ..., p5 | card) P(card)
    
    # denominator: Sum Across All Cards P(p1 | card) P(p2 | card) ... P(p5 | card) P(card)

    prob_dict = {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 16, 11: 4}
    prob_dict = {key: value / 52 for key, value in prob_dict.items()}
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
