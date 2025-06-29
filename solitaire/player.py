from abc import ABC, abstractmethod
from typing import Optional
import time
from .board import Board
from .move import Move

class Player(ABC):
    @abstractmethod
    def select_move(self, board: Board, legal_moves: list[Move]) -> Optional[Move]:
        """Analyzes the board and selects a move from the list of legal moves."""
        pass

    def notify_automatic_move(self, move: Move):
        """
        Handles the case where a move is made automatically.
        Base implementation just prints the move.
        """
        print(f"\nOnly one move available. Automatically executing: {move}")

class AIPlayer(Player):
    """A simple AI that picks the first available legal move."""
    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def select_move(self, board: Board, legal_moves: list[Move]) -> Optional[Move]:
        # A very basic strategy for now: just pick the first move.
        if self.verbose:
            print("AI selects the first available move.")
        return legal_moves[0]

class HumanPlayer(Player):
    """A player that takes input from the console."""
    def select_move(self, board: Board, legal_moves: list[Move]) -> Optional[Move]:
        """
        Displays the list of legal moves to the user and prompts for a selection.
        Returns None if the user chooses to quit.
        """
        print("\nAvailable Moves:")
        for i, move in enumerate(legal_moves):
            print(f"  {i + 1}: {move}")

        if board.waste.top_card and board.has_waste_card_been_seen():
            print("\nHint: A card with this rank and color has been seen in this cycle.")

        while True:
            try:
                prompt = f"\nSelect a move (1-{len(legal_moves)}) or type 'q' to quit: "
                choice_str = input(prompt).lower()

                if choice_str in ('q', 'quit'):
                    return None

                choice_index = int(choice_str) - 1
                if 0 <= choice_index < len(legal_moves):
                    return legal_moves[choice_index]
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")

    def notify_automatic_move(self, move: Move):
        """Human player needs a pause to see the move."""
        super().notify_automatic_move(move)
        time.sleep(0.75)

class SimplePlayer(Player):
    """A non-interactive player that always selects the first available legal move."""
    def select_move(self, board: Board, legal_moves: list[Move]) -> Optional[Move]:
        """
        Always selects the first move from the list of legal moves.
        """
        # This player demonstrates automatic play, so we print the move and pause.
        selected_move = legal_moves[0]
        print(f"\nSimplePlayer selects: {selected_move}")
        return selected_move
