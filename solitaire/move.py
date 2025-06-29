"""
Defines the different types of moves that can be made in a game of Solitaire.

This module uses the Command design pattern, where each move is an object
that knows how to execute itself on a game board.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Use a TYPE_CHECKING block to avoid circular imports with 'board'
if TYPE_CHECKING:
    from .board import Board
    from .card import Card


class Move(ABC):
    """Abstract base class for a game move."""

    @abstractmethod
    def execute(self, board: "Board") -> None:
        """Executes the move, modifying the board state."""
        pass

    def __str__(self) -> str:
        """A human-readable representation of the move."""
        return self.__class__.__name__


# --- Specific Move Implementations ---

@dataclass(frozen=True)
class DrawFromStock(Move):
    """Represents drawing a card from the stock to the waste."""

    def execute(self, board: "Board") -> None:
        card = board.stock.pop_card()
        board.waste.add_card(card)

    def __str__(self) -> str:
        return "Draw card from Stock"


@dataclass(frozen=True)
class ResetStock(Move):
    """Represents resetting the stock from the waste pile."""

    def execute(self, board: "Board") -> None:
        # Cards are moved back in reverse order
        while board.waste:
            board.stock.add_card(board.waste.pop_card())

    def __str__(self) -> str:
        return "Reset Stock from Waste"


@dataclass(frozen=True)
class WasteToFoundation(Move):
    """Move the top card of the waste to a foundation."""
    foundation_index: int
    card: "Card"  # Store the card for the __str__ method

    def execute(self, board: "Board") -> None:
        card = board.waste.pop_card()
        board.foundations[self.foundation_index].add_card(card)

    def __str__(self) -> str:
        return f"Move {self.card} to Foundation {self.card.suit.value}"


@dataclass(frozen=True)
class WasteToTableau(Move):
    """Move the top card of the waste to a tableau."""
    tableau_index: int
    card: "Card"  # Store the card for the __str__ method

    def execute(self, board: "Board") -> None:
        card = board.waste.pop_card()
        board.tableau_piles[self.tableau_index].add_card(card)

    def __str__(self) -> str:
        return f"Move {self.card} from Waste to Tableau {self.tableau_index + 1}"


@dataclass(frozen=True)
class TableauToFoundation(Move):
    """Move the top card of a tableau to a foundation."""
    source_tableau_index: int
    foundation_index: int
    card: "Card"

    def execute(self, board: "Board") -> None:
        source_pile = board.tableau_piles[self.source_tableau_index]
        card = source_pile.pop_card()
        board.foundations[self.foundation_index].add_card(card)
        # After moving, try to flip the new top card of the source tableau
        source_pile.flip_top_card()

    def __str__(self) -> str:
        return f"Move {self.card} to Foundation {self.card.suit.value}"


@dataclass(frozen=True)
class TableauToTableau(Move):
    """Move one or more cards from one tableau to another."""
    source_tableau_index: int
    dest_tableau_index: int
    num_cards: int
    card: "Card"  # The top card of the stack being moved

    def execute(self, board: "Board") -> None:
        source_pile = board.tableau_piles[self.source_tableau_index]
        dest_pile = board.tableau_piles[self.dest_tableau_index]

        # Remove the stack from the source and add it to the destination
        cards_to_move = source_pile.pop_stack(self.num_cards)
        for card in cards_to_move:
            dest_pile.add_card(card)

        # After moving, try to flip the new top card of the source tableau
        source_pile.flip_top_card()

    def __str__(self) -> str:
        plural = "s" if self.num_cards > 1 else ""
        return (
            f"Move {self.num_cards} card{plural} (starting with {self.card}) from "
            f"Tableau {self.source_tableau_index + 1} to Tableau {self.dest_tableau_index + 1}"
        )