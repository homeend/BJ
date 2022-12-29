from player_hand import PlayerCards, Closed, StartHand, Splittable
from shoe import Shoe


def main():
    # for card in Shoe(2, True):
    #     print(card)
    # assert len(list(Shoe(3))) == 156
    # assert len(list(Shoe(3).shuffle())) == 156
    # assert len(list(Shoe(2, True))) == 104
    # assert set(Shoe()) == set(Shoe(shuffle=True))
    # assert len(set(Shoe(shuffle=True))) == 52

    shoe = Shoe(shuffle=True)

    played = []
    in_play = []

    while shoe.reshuffle_count() == 0:
        print("\u2500" * 100)
        player_cards = PlayerCards(shoe.get_card())
        player_cards = player_cards.hit(shoe.get_card())
        print(player_cards, player_cards.value)

        in_play.append(player_cards)

        while in_play:
            player_hand = in_play.pop(0)
            if isinstance(player_hand, Splittable):
                print("splitting", player_hand.cards[0].value.name)
                h1, h2 = player_hand.split(shoe.get_card(), shoe.get_card())
                print("new cards", h1)
                print("new cards", h2)
                in_play.append(h1)
                in_play.append(h2)
                continue

            while not isinstance(player_hand, Closed):
                if (
                    isinstance(player_hand, StartHand)
                    and player_hand.is_hard
                    and player_hand.value < 10
                ):
                    player_hand = player_hand.double_down(shoe.get_card())
                    print(
                        "double down",
                        player_hand,
                        player_hand.value,
                    )
                elif player_hand.value >= 19:
                    player_hand = player_hand.stand()
                else:
                    player_hand = player_hand.hit(shoe.get_card())
                    print(
                        "hit",
                        player_hand,
                        player_hand.value,
                    )
            played.append(player_hand)

    print("\u2500" * 100)
    print("\u2500" * 100)

    for hand in played:
        print("played", hand, hand.value)


if __name__ == "__main__":
    main()
