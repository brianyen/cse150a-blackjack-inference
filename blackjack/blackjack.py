import random
import numpy as np
import bayesian_agent.bayesian as bayes
import bayesian_agent.markovian as markov
import importlib
import math

def read_data(filename):
  data = np.ndarray([12, 22, 3])

  with open(filename, 'r') as f:
    i = 0
    for row in f:
      i += 1
      if i == 1:
        continue

      items = row.split(",")
      hits = int(items[3])
      stands = int(items[4])

      if hits == 0 and stands == 0:
        # never seen in actual gameplay
        data[int(items[0])][int(items[1])][int(items[2])] = 0.5
      else:
        data[int(items[0])][int(items[1])][int(items[2])] = hits / (hits + stands)

  return data

def random_card():
  cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
  return random.choice(cards)

def bot_choice(args, value, num_aces):
  player_choices = args[0]
  dealer_card = args[1]

  if value == 21:
    return 0

  if random.random() < player_choices[dealer_card][value][num_aces]:
    return 1
  else:
    return 0

def dealer_choice(args, value, num_aces):
  if value < 17:
    return 1
  # elif value == 17 and num_aces > 0:
  #   return 1
  else:
    return 0

def play_round(card1, card2, choice_algorithm, deck, other_args):
  choice_list = []
  card_list = [card1, card2]
  num_aces = 0
  aces_used = 0
  if card1 == 11:
    num_aces += 1
  if card2 == 11:
    num_aces += 1
  value = card1 + card2
  if value > 21:
    value -= 10
    aces_used += 1

  while True:
    choice = choice_algorithm(other_args, value, min(num_aces - aces_used, 2))
    choice_list.append((value, min(num_aces - aces_used, 2), choice, card_list.copy()))
    if choice == 0:
      # stand
      break

    added_card = deck.pop(0)
    card_list.append(added_card)
    if added_card == 11:
      num_aces += 1

    value += added_card
    while value > 21 and num_aces - aces_used > 0:
      value -= 10
      aces_used += 1

    if value > 21:
      # bust
      choice_list.append((value, min(num_aces - aces_used, 2), 2, card_list))
      break

  return choice_list, value

def play_blackjack(agent, player_choices, num_other_players):
  static_deck = []
  for i in range(0, 52):
    static_deck.append(random_card())

  # uncomment to test with regular deck
  # static_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

  num_wins = 0
  num_ties = 0
  num_losses = 0
  num_bot_wins = 0
  num_bot_ties = 0
  num_bot_losses = 0
  for i in range(0, 100):
    deck = static_deck.copy()
    random.shuffle(deck)
    dealer_card = deck.pop(0)
    # print("dealer card:", dealer_card)
    choice_list = []
    # choice_list[i] = (value, aces, outcome, cardlist), outcome maps with {0: stand, 1: hit, 2: bust}
    end_of_round_values = []
    for i in range(0, num_other_players):
      card1 = deck.pop(0)
      card2 = deck.pop(0)
      choices, value = play_round(card1, card2, bot_choice, deck, (player_choices, dealer_card))
      choice_list.extend(choices)
      end_of_round_values.append(value)

    pcard1 = deck.pop(0)
    pcard2 = deck.pop(0)

    markov.has_updated = False
    agent_cards, p_value = play_round(pcard1, pcard2, agent, deck, (player_choices, choice_list, (pcard1, pcard2)))
    bayes.mse += (dealer_card - bayes.guess) ** 2
    markov.mse += (dealer_card - markov.guess) ** 2

    card2 = deck.pop()
    dealer_cards, d_value = play_round(dealer_card, card2, dealer_choice, deck, None)

    for player in end_of_round_values:
      if player > 21:
        num_bot_losses += 1
      elif d_value > 21:
        num_bot_wins += 1
      elif player > d_value:
        num_bot_wins += 1
      elif player == d_value:
        num_bot_ties += 1
      else:
        num_bot_losses += 1

    if p_value > 21:
      num_losses += 1
    elif d_value > 21:
      num_wins += 1
    elif p_value > d_value:
      num_wins += 1
    elif p_value == d_value:
      num_ties += 1
    else:
      num_losses += 1

  # print(num_wins, num_ties, num_losses)
  return num_wins, num_ties, num_losses, num_bot_wins, num_bot_ties, num_bot_losses

def squared_error(belief, actual):
    return sum([(belief[i] - actual[i]) ** 2 for i in range(2, 12)])

def play_blackjack_time_series(agent, player_choices, num_other_players, bucket_size = 1):
  static_deck = []
  for i in range(0, 52):
    static_deck.append(random_card())
  
  true_freqs = {item: 0 for item in range(2, 12)}
  for item in static_deck:
      true_freqs[item] += 1
  true_freqs = {item: value / sum(true_freqs.values()) for item, value in true_freqs.items()}

  # uncomment to test with regular deck
  # static_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

  # uncomment to test with extremely stacked deck
  # static_deck = [5, 6, 7, 8, 10, 10, 10, 10, 10, 10, 10, 10, 10] * 4

  # card counting deck
  static_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10, 10, 10, 10, 11] * 4

  bot_record = []
  agent_record = []
  belief_diff = []
  mse_record = []
  for i in range(0, 100):
    deck = static_deck.copy()
    random.shuffle(deck)
    dealer_card = deck.pop(0)
    # print("dealer card:", dealer_card)
    choice_list = []
    # choice_list[i] = (value, aces, outcome, cardlist), outcome maps with {0: stand, 1: hit, 2: bust}
    end_of_round_values = []
    for _ in range(0, num_other_players):
      card1 = deck.pop(0)
      card2 = deck.pop(0)
      choices, value = play_round(card1, card2, bot_choice, deck, (player_choices, dealer_card))
      choice_list.extend(choices)
      end_of_round_values.append(value)

    pcard1 = deck.pop(0)
    pcard2 = deck.pop(0)
    
    markov.has_updated = False
    markov.true_card = dealer_card
    agent_cards, p_value = play_round(pcard1, pcard2, agent, deck, (player_choices, choice_list, (pcard1, pcard2)))
    bayes.mse += (dealer_card - bayes.guess) ** 2
    markov.mse += (dealer_card - markov.guess) ** 2
    belief_diff.append(squared_error({key: value / sum(markov.belief.values()) for key, value in markov.belief.items()}, true_freqs))
    
    if i % bucket_size == 0:
        mse_record.append((dealer_card - markov.guess) ** 2)
    else:
        mse_record[int(i / bucket_size)] += (dealer_card - markov.guess) ** 2

    card2 = deck.pop()
    dealer_cards, d_value = play_round(dealer_card, card2, dealer_choice, deck, None)

    bot_record.append(0)
    for player in end_of_round_values:
      if player > 21:
        bot_record[i] += -1
      elif d_value > 21:
        bot_record[i] += 1
      elif player > d_value:
        bot_record[i] += 1
      elif player == d_value:
        bot_record[i] += 0
      else:
        bot_record[i] += -1

    if i % bucket_size == 0:
      agent_record.append(0)

    if p_value > 21:
      agent_record[int(i / bucket_size)] += -1
    elif d_value > 21:
      agent_record[int(i / bucket_size)] += 1
    elif p_value > d_value:
      agent_record[int(i / bucket_size)] += 1
    elif p_value == d_value:
      agent_record[int(i / bucket_size)] += 0
    else:
      agent_record[int(i / bucket_size)] += -1

  return bot_record, agent_record, belief_diff, mse_record

def random_play(arg1, arg2, arg3):
  return random.randint(0, 1)