def bayesian_round(args, value, num_aces):
    # args: (player_choices, choice_list, dealer_card, (card1, card2))
    player_choices = args[0]
    choice_list = args[1]
    dealer_card = args[2]
    card1, card2 = args[3]

    # 1. calculate P(dealer_second | )
    known_cards = [dealer_card, card1, card2]
    for choice in choice_list:
        known_cards.extend(choice[3])
    
    first_draw_prob = calculate_drawing_probabilities(known_cards)

    prob_hit = 0
    prob_stand = 0

    for c1, p_c1 in first_draw_prob.items():
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




    return 1

def calculate_drawing_probabilities(knowns):
    # returns probability hidden dealer card is each card assuming deck is ordinary
    # knowns - array of known card draws

    prob_dict = {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 16, 11: 4}
    sum = 52
    for card in knowns:
        if prob_dict[card] > 0:
            prob_dict[card] -= 1
            sum -= 1

    prob_dict = {key: value / sum for key, value in prob_dict.items()}

    return prob_dict
