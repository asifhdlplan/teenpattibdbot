import random

suits = ["♠", "♥", "♦", "♣"]

ranks = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}

deck = []

for suit in suits:
    for rank in ranks:
        deck.append(f"{rank}{suit}")


def deal_cards():
    random.shuffle(deck)
    return random.sample(deck, 3)


def hand_score(cards):

    values = []

    for card in cards:
        rank = card[:-1]
        values.append(ranks[rank])

    values.sort()

    # Trail
    if len(set(values)) == 1:
        return 100

    # Pair
    if len(set(values)) == 2:
        return 50

    # High Card
    return sum(values)


def compare(player, bot):

    player_score = hand_score(player)
    bot_score = hand_score(bot)

    if player_score > bot_score:
        return "player"

    elif bot_score > player_score:
        return "bot"

    return "draw"