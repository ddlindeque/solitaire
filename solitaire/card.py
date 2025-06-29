import enum
from dataclasses import dataclass


class Suit(enum.Enum):
    """Represents the suit of a card, with a color property."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

    @property
    def color(self) -> str:
        """Returns the color of the suit."""
        return "red" if self in (Suit.HEARTS, Suit.DIAMONDS) else "black"


class Rank(enum.Enum):
    """Represents the rank of a card, with integer values for comparison."""
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


@dataclass(frozen=True, order=True)
class Card:
    """Represents a single playing card with a rank and suit."""
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        """Returns a human-friendly string for the card, e.g., 'A♥' or '10♦'."""
        rank_map = {
            Rank.ACE: "A",
            Rank.TEN: "10",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
        }
        rank_str = rank_map.get(self.rank, str(self.rank.value))
        return f"{rank_str}{self.suit.value}"