## UPDATES FOR REGRADE REQUEST

### PEAS/Agent Analysis

`Performance Measure`: We measure the performance of our bot by the average amount of money won/lost per dollar it puts into the game. For example, in the table under the conclusion section, you can see that "Agent 2" has an expected return of -0.0484 when playing with 10 other players. This means for every $1 it puts in, it is expected to lose 4.84 cents. For reference, a player using perfect strategy (without splitting or doubling down) has an expected loss of about 2% when they can see all cards and are playing with a standard deck, so we'd like our bot to get as close to that as possible.

We also measure the MSE (mean square error) of our bot's best guess of what the dealer's shown card is versus what it actually is to get a sense of how it's doing relative to how many players there are, but that's not what the bot is ultimately trying to optimize for.

`Environment`: The environment includes: the dealer's two cards (both of which are hidden from our agent), the cards of all other players, the decisions of the other players depending on what they see from the dealer, and the deck. Importantly, the deck is random—every card has a value randomly taken from the 13 possible cards in a standard deck, so playing a standard strategy might not be optimal.

`Actuators`: The agent only has the ability to choose whether to hit or stand (at least in the current iteration). In future iterations, it might also gain the ability to split, double down, etc.

`Sensors`: The agent ONLY senses the decisions the other players make alongside what cards they have. That means it has no clue what card the dealer has, which is typically an essential part of a blackjack player's strategy. The agent also doesn't have a sensor to see what cards are in the random deck.

### Agent Setup

The deck is indeed randomized. What we do is we pick a random card from a standard deck of cards 52 times with replacement and then call that our new deck. This means that we can expect the card frequencies in the deck to be roughly distributed like that of a standard deck, but there might be some cards that have unusually high frequencies.

Although our agent doesn't account for this in its current model, it will for Milestone 3 (we thought this would be a good application for a Hidden Markov Model). In the future, we can use these cards that appear more often to potentially gain the upper hand against the dealer.

In addition to the deck being randomized, the agent also doesn't get to see what cards the dealer has (typically players would get to see one of the dealer's cards). As a human, this would probably mean your best strategy is to play simply based on your own chances of busting when drawing new cards. However, the agent can use the decisions of the other players to gain a vague understanding of what the dealer's shown card is.

### Training

We based our training on a data set of 900,000 hands of blackjack. We used likelihood maximization to determine the CPTs for our Bayesian Network.

During training, we had full visibility of what the dealer's shown card was when players made decisions whether to hit or stand, so we could simply determine the counts of each kind of decision to fill out the probability table.

In particular, we went through `blkjckhands.csv` (which we got from Kaggle) and simulated each game to create a tally of each player's decisions in a given position. Then we summarized that cleaned data in `blkjck_clean.csv`, which we can load quickly into our CPTs by simply dividing the number of hits by the total number of hits and stands for each state.

A simplifying assumption we made was that a player's decision would be approximately the same whenever they had 2 or more aces (that is, we compacted any state with 3 or more aces into the one with only 2 aces). This was to prevent our agent from overfitting to our data; otherwise, we might have a freak event where a player has 5 aces and a total value of 14 and our agent can determine exactly what card the dealer has with 100% certainty.

Another simplifying assumption we made was that in any state that the data set had never reached, a player would simply randomly choose between hitting and standing with 50-50 odds. These states are so rare that they aren't that impactful, but this was better than simply resetting the round.

A final simplifying assumption we made is that the players in our game will continue to play like the players from our data with equal probability as what we saw in the data set. That is, our bot players will follow the CPTs exactly. This might give a slight unfair advantage to our agent since it guarantees our CPTs are accurate, but the other option would have been to only play rounds that actually happened in the data set, which we thought would've been a worse solution.

## PREVIOUS SUBMISSION

### Agent PEAS 

Our agent’s performance measure is the average amount of money won (or lost) in a game. Its environment consists of the randomized deck of cards, the other players at the table (bots in this case), and the dealer. Specifically, the other players at the table also play a round of blackjack prior to our agent’s turn. Each other player has cards that they start with and can hit to gain more cards according to a stochastic algorithm. 

The dealer also starts with two cards, and also can eventually hit to gain more cards while following a strict algorithm. Regarding actuators, our agent can choose whether it wants to stand, or to hit to gain another card. Our agent’s sensors allow it to see the cards and actions of the other players at the table, along with its own cards, and uses that information to make its decision. It can not see any card of the dealer, despite the other players being able to. 

### Data Processing

We process our data [in this notebook](CSE_150A_Project_Clean_Data.ipynb).

In our [raw dataset](blkjckhands.csv), each row describes one player's round of blackjack. We initialize a multi-layered dictionary first indexed by the dealer's possible visible cards. Then, the next layer is indexed by the player's possible hand value up to 22. Then, the next layer is indexed by the number of aces we saw from the player, up to 5. In total, these each represent a possbile state for the player. Finally, the last layer has an integer for number of hits and an integer for the number of stands for each state.

For each row, we figure out how many aces the player received. We then sum up the player's total hand value, treating as many aces as 11 as we can without going over 21 total value. We then iterate through the player's third, fourth, and fifth card, tracking the state of the player's hand before receiving each card. If the player receives a card, we increment the number of hits we saw in the state by 1. If the player does not receive a card, we increment the number of stands we saw by 1 and move on to the next row.

Then, our dictionary is written row-by-row in `dealer_seen,player_value,num_aces,num_hits,num_stands` CSV format in [blkjck_clean.csv](blkjck_clean.csv).

### Agent Setup and Modeling

Our agent is a goal-based agent, particularly using its current expectations of the dealer’s hand to figure out how to win each round of blackjack. In particular, we processed our dataset of blackjack games to organize the number of times players hit versus stand given both their hands and the dealer’s visible card. Then, using the sequence of choices to hit or stand by the bots in the round given their hands as evidence, we then can calculate the probability we see that evidence for each possible dealer card to guess what the dealer’s visible card is. 
![Bayesian Network with Dealer and Bots](img/bayes_net_evidence.png)

We are calculating `P(Dealer_Card=card|evidence)` for each possible `card`, and where `evidence` is the collection of choices the bots made given their state (hand and number of aces). Since we also know the state of each bot's hand as they make their decisions, those states are also in our evidence.

### Implementation

To explore how we benchmarked our agents, click on [this link](CSE_150A_Play_Blackjack.ipynb).

To explore how we implemented our agents, click on [this link](bayesian_agent/bayesian.py).

Specifically, we wrote two agents. They both use the same bayesian method to calculate the probability of each possbile visible dealer card. The first agent, agent1, assumes that the most likely card we calculated is the dealer's card and makes it decision based off of that. The second agent, agent2, weighs the expected return for each choice across the probability the dealer has each card. Effectively, it makes the choice with the highest expected return over all dealer cards.

To make the choice, we use a simplified calculation that calculates the probability that the dealer will end with a certain hand value given they start with a certain card. Then, we use dynamic programming principles to calculate the approximate expected value of hitting and standing in each state to find the best choice in our current state. 

To explore how we ran the blackjack game, click on [this link](blackjack/blackjack.py).

### Conclusion

When benchmarking our two agents, we kept track of the expected return from a single dollar wager for a game of blackjack. We also kept track of the mean squared error between what the agent things the dealer has versus what the dealer actually has. We ran tests with different numbers of bots to see how the agent improves as it gets more data, as well as to compare the agent's performance versus that of the average human. 

We can 100,000 games using a standard deck of cards for both agents, then 100,000 games with a completely randomized deck of cards for both agents. The data is pictured below.

![Data Table](img/conclusion_table.png)

It appears that when we have enough bots running alongside our agent, we are able to beat the performance of the bots. Additionally, having more information from the bots lowers our mean squared error. On average, we are still expected to loose about five cents from the dollar, which is expected since the player loses in blackjack, and we are not allowing splitting and other rules that help give the player a slight edge.

![Graphs](img/conclusion_graphs.png)

It appears that agent 2 has a slightly better expected return than agent 1, which makes sense because it has a more holistic approach that considers all possibilities while still giving more weight to liklier worlds. Both agents have the same mean squared error because they both use the same underlying method to calculate dealer card probabilities.

The agent performs slightly worse with the randomized deck which makes sense because in its current state, it makes the assumption that the deck is a standard deck of cards. 

### Improvements

Particularly in the case of the randomized deck, one way we could improve our agent is by designing a Hidden Markov Model to represent the deck, so that as the rounds pass, we can develop a better picture of which cards are in the deck. This will help the agent to make more educated decisions and win more often.

We could also implement extra blackjack rules such as doubling down, splitting, and surrendering  which help make the game more fair.