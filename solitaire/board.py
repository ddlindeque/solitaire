import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from solitaire.card import Card, Rank, Suit
from solitaire.move import (
    DrawFromStock,
    FoundationToTableau,
    Move,
    ResetStock,
    TableauToFoundationAndReveal,
    TableauToFoundation,
    TableauToTableauAndReveal,
    TableauToTableau,
    WasteToFoundation,
    WasteToTableau,
)

if TYPE_CHECKING:
    pass

# The maximum number of moves allowed in a game before it's considered a loss.
MAX_MOVES = 999

# --- Base Pile Class ---

class Pile(ABC):
    """Abstract base class for a pile of cards."""

    def __init__(self):
        self._cards: List[Card] = []

    def __len__(self) -> int:
        return len(self._cards)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._cards!r})"

    @property
    def top_card(self) -> Optional[Card]:
        """Returns the top card of the pile without removing it, or None if empty."""
        return self._cards[-1] if self._cards else None

    def add_card(self, card: Card):
        """Adds a card to the top of the pile."""
        self._cards.append(card)

    def pop_card(self) -> Card:
        """Removes and returns the top card of the pile."""
        return self._cards.pop()

    @abstractmethod
    def can_add_card(self, card: Card) -> bool:
        """Checks if a card can be legally added to this pile."""
        pass

# --- Specific Pile Implementations ---

class Stock(Pile):
    """The stock pile, where cards are drawn from."""
    def can_add_card(self, card: Card) -> bool:
        # You generally don't add cards back to the stock during play.
        return False

class Waste(Pile):
    """The waste pile, where cards from the stock are placed face-up."""
    def can_add_card(self, card: Card) -> bool:
        # The waste pile can always have a card added to it from the stock.
        return True

class Foundation(Pile):
    """A foundation pile, where cards are built up from Ace to King by suit."""
    def __init__(self, suit: Suit):
        super().__init__()
        self.suit = suit

    def can_add_card(self, card: Card) -> bool:
        # Must be the correct suit for this foundation.
        if card.suit != self.suit:
            return False

        top = self.top_card
        if top is None:
            # Can only start a foundation with an Ace.
            return card.rank == Rank.ACE
        else:
            # Must be the next rank up.
            return card.rank.value == top.rank.value + 1

class Tableau(Pile):
    """A tableau pile, one of the seven main piles on the game board."""
    def __init__(self, face_down_cards: Optional[List[Card]] = None, face_up_cards: Optional[List[Card]] = None):
        super().__init__()
        self._face_down_cards = face_down_cards if face_down_cards is not None else []
        if face_up_cards:
            self._cards.extend(face_up_cards)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"down={len(self._face_down_cards)}, "
            f"up={self._cards!r})"
        )

    @property
    def face_up_cards(self) -> List[Card]:
        """Returns the list of face-up cards."""
        return self._cards

    @property
    def face_down_count(self) -> int:
        """Returns the number of face-down cards."""
        return len(self._face_down_cards)

    def can_add_card(self, card: Card) -> bool:
        top = self.top_card
        if top is None:
            # Can only start an empty tableau with a King.
            return card.rank == Rank.KING
        else:
            # Must be the opposite color and the next rank down.
            return card.suit.color != top.suit.color and card.rank.value == top.rank.value - 1

    def pop_stack(self, num_cards: int) -> List[Card]:
        """Removes and returns a stack of N cards from the face-up pile."""
        stack = self._cards[-num_cards:]
        self._cards = self._cards[:-num_cards]
        return stack

    def flip_top_card(self) -> bool:
        """
        If there are no face-up cards but there are face-down cards,
        flips the top face-down card to be face-up. Returns True if a flip occurred.
        """
        if not self._cards and self._face_down_cards:
            self.add_card(self._face_down_cards.pop())
            return True
        return False

# --- The Main Board Class ---

class Board:
    """Manages the entire state of the Solitaire game."""

    def __init__(self):
        self.stock = Stock()
        self.waste = Waste()
        # The order of suits for foundations will be consistent.
        self.foundation_suits = list(Suit)
        self.foundations: List[Foundation] = [Foundation(suit) for suit in self.foundation_suits]
        self.tableau_piles: List[Tableau] = []
        self.move_count = 0
        self._state_history = set()

    def _get_state_hash(self) -> tuple:
        """Creates a hashable representation of the current board state."""
        # Using tuples to make the state hashable
        stock_state = tuple(self.stock._cards)
        waste_state = tuple(self.waste._cards)
        foundations_state = tuple(f.top_card for f in self.foundations)
        
        tableau_states = []
        for p in self.tableau_piles:
            tableau_state = (p.face_down_count, tuple(p.face_up_cards))
            tableau_states.append(tableau_state)
        
        return (stock_state, waste_state, foundations_state, tuple(tableau_states))

    def setup(self):
        """Creates a deck, shuffles it, and deals the cards."""
        # 1. Create a standard 52-card deck
        deck = [Card(rank, suit) for suit in Suit for rank in Rank]

        # 2. Shuffle the deck
        random.shuffle(deck)

        # 3. Deal to the seven tableau piles
        self.tableau_piles = []
        for i in range(7):
            num_face_down = i
            face_down_cards = [deck.pop() for _ in range(num_face_down)]
            face_up_card = deck.pop()
            self.tableau_piles.append(Tableau(face_down_cards, [face_up_card]))

        # 4. Place the rest of the deck in the stock
        for card in deck:
            self.stock.add_card(card)
        self.move_count = 0
        self._state_history = {self._get_state_hash()}

    def setup_random_scenario(self, number_of_cards: int):
        """
        Sets up a random game state with a specific number of face-down cards.
        The rest of the deck is distributed logically onto the board.
        """
        self.__init__() # Reset the board to a clean state

        if not (0 <= number_of_cards <= 45):
            raise ValueError("Number of face-down cards must be between 0 and 45.")

        # 1. Create and shuffle a deck
        deck = [Card(rank, suit) for suit in Suit for rank in Rank]
        random.shuffle(deck)

        # 2. Distribute the specified number of face-down cards
        face_down_for_piles = [[] for _ in range(7)]
        for _ in range(number_of_cards):
            card = deck.pop()
            random.choice(face_down_for_piles).append(card)
        
        self.tableau_piles = [Tableau(p) for p in face_down_for_piles]

        # 3. Distribute the rest of the cards logically
        for card in deck:
            placed = False
            # 3a. Try to place on a foundation
            target_foundation_index = self.foundation_suits.index(card.suit)
            foundation = self.foundations[target_foundation_index]
            if foundation.can_add_card(card):
                foundation.add_card(card)
                placed = True
            
            # 3b. If not, try to place on a tableau
            if not placed:
                for tableau in self.tableau_piles:
                    if tableau.can_add_card(card):
                        tableau.add_card(card)
                        placed = True
                        break
            
            # 3c. If it couldn't be placed, add to stock
            if not placed:
                self.stock.add_card(card)

        # 4. Ensure all non-empty tableaus have a face-up card
        for pile in self.tableau_piles:
            pile.flip_top_card()
        
        self._state_history = {self._get_state_hash()}

    def get_legal_moves(self) -> List[Move]:
        """
        Scans the entire board state and returns a list of all valid moves.
        """
        legal_moves: List[Move] = []

        # 1. Moves from Stock/Waste
        if self.stock:
            legal_moves.append(DrawFromStock())
        elif self.waste:
            legal_moves.append(ResetStock())

        # 2. Moves from Waste pile
        top_waste_card = self.waste.top_card
        if top_waste_card:
            # Waste to Foundation
            target_foundation_index = self.foundation_suits.index(top_waste_card.suit)
            foundation = self.foundations[target_foundation_index]
            if foundation.can_add_card(top_waste_card):
                legal_moves.append(
                    # from and to states are not isomorphic
                    WasteToFoundation(foundation_index=target_foundation_index, card=top_waste_card)
                )
            # Waste to Tableau
            for i, tableau in enumerate(self.tableau_piles):
                if tableau.can_add_card(top_waste_card):
                    legal_moves.append(
                        # from and to states are not isomorphic
                        WasteToTableau(tableau_index=i, card=top_waste_card)
                    )

        # 3. Moves from Tableau piles
        for i, source_pile in enumerate(self.tableau_piles):
            # 3a. Tableau to Foundation (only top card can move)
            top_tableau_card = source_pile.top_card
            if top_tableau_card:
                target_foundation_index = self.foundation_suits.index(top_tableau_card.suit)
                foundation = self.foundations[target_foundation_index]
                if foundation.can_add_card(top_tableau_card):
                    # Check if this move will reveal a new card. This happens if the
                    # source pile has face-down cards and only one face-up card.
                    will_reveal_card = (
                        len(source_pile.face_up_cards) == 1
                        and source_pile.face_down_count > 0
                    )
                    if will_reveal_card:
                        legal_moves.append(
                            TableauToFoundationAndReveal(
                                source_tableau_index=i,
                                foundation_index=target_foundation_index,
                                card=top_tableau_card,
                            )
                        )
                    else:
                        legal_moves.append(
                            TableauToFoundation(
                                source_tableau_index=i,
                                foundation_index=target_foundation_index,
                                card=top_tableau_card,
                            )
                        )

            # 3b. Tableau to Tableau (stacks of cards can move)
            for k, card_in_stack in enumerate(source_pile.face_up_cards):
                num_cards = len(source_pile.face_up_cards) - k
                # A move reveals a card if we move all face-up cards and there are face-down cards underneath.
                will_reveal_card = (k == 0) and (source_pile.face_down_count > 0)

                # Optimization: Only generate one move for a given King stack to any empty pile.
                # This prevents creating many pointless, equivalent moves.
                king_to_empty_move_generated = False

                for j, dest_pile in enumerate(self.tableau_piles):
                    if i == j: continue # Cannot move to the same pile

                    if dest_pile.can_add_card(card_in_stack):
                        # Further optimization: Prevent moving a King stack to an empty tableau
                        # if it doesn't reveal a new card. This is a common type of
                        # pointless, easily reversible move that clutters the search space.
                        is_king_to_empty = card_in_stack.rank == Rank.KING and not dest_pile
                        if is_king_to_empty:
                            if not will_reveal_card:
                                continue # Pointless move.
                            if king_to_empty_move_generated:
                                continue # Already made a move for this King to an empty pile.
                            king_to_empty_move_generated = True

                        if will_reveal_card:
                            legal_moves.append(
                                TableauToTableauAndReveal(
                                    source_tableau_index=i, dest_tableau_index=j, num_cards=num_cards, card=card_in_stack
                                )
                            )
                        else:
                            legal_moves.append(
                                TableauToTableau(
                                    source_tableau_index=i, dest_tableau_index=j, num_cards=num_cards, card=card_in_stack
                                )
                            )

        # 4. Moves from Foundation piles
        for i, source_pile in enumerate(self.foundations):
            card_to_move = source_pile.top_card
            if not card_to_move:
                continue

            # Foundation to Tableau
            for j, dest_pile in enumerate(self.tableau_piles):
                if dest_pile.can_add_card(card_to_move):
                    legal_moves.append(
                        FoundationToTableau(
                            source_foundation_index=i, dest_tableau_index=j, card=card_to_move
                        )
                    )
        return legal_moves

    def execute_move(self, move: Move) -> None:
        """Executes a given move by calling its own execute method."""
        move.execute(self)
        self.move_count += 1

    def has_waste_card_been_seen(self) -> bool:
        """
        Checks if a card with the same rank and color as the current waste
        card exists elsewhere in the waste pile.
        """
        top_card = self.waste.top_card
        # If there's no top card or only one card, it can't be a repeat.
        if not top_card or len(self.waste) <= 1:
            return False

        # Check all cards in the waste pile *except* the top one.
        for card in self.waste._cards[:-1]:
            if card.rank == top_card.rank and card.suit.color == top_card.suit.color:
                return True
        
        return False

    def is_win(self) -> bool:
        """
        Checks if the game is solved.
        Based on the analysis in README.md, the game is considered won if there are
        2 or fewer hidden cards remaining, as it's assumed to be solvable from that point.
        """
        if not self.tableau_piles:
            return False
        total_hidden_cards = sum(t.face_down_count for t in self.tableau_piles)
        return total_hidden_cards <= 2