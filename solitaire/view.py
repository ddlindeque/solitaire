from typing import Optional
import re

from .board import Board, Tableau
from .board import MAX_MOVES
from .card import Card, Rank, Suit

class TextView:
    """Renders the game board in a text format to the console."""

    # ANSI color codes for terminal output
    COLOR_RED = "\033[91m"
    COLOR_BLUE = "\033[94m"
    COLOR_RESET = "\033[0m"

    def _strip_ansi(self, text: str) -> str:
        """Removes ANSI escape codes from a string to calculate visible length."""
        # This regex is for SGR (Select Graphic Rendition) codes.
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        return ansi_escape.sub("", text)

    def _center_ansi(self, text: str, width: int) -> str:
        """Centers a string that may contain ANSI codes."""
        visible_len = len(self._strip_ansi(text))
        padding = width - visible_len
        if padding <= 0:
            return text
        left_pad = padding // 2
        right_pad = padding - left_pad
        return " " * left_pad + text + " " * right_pad

    def _format_card(self, card: Optional[Card]) -> Optional[str]:
        """Formats a card for display. Returns None if card is None."""
        if not card:
            return None
        
        rank_map = {
            Rank.ACE: "A",
            Rank.TEN: "10",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
        }
        rank_str = rank_map.get(card.rank, str(card.rank.value))
        card_str = f"{rank_str:>2}{card.suit.value}"

        if card.suit.color == "red":
            return f"{self.COLOR_RED}{card_str}{self.COLOR_RESET}"
        return card_str  # Use default terminal color for black cards

    def display(self, board: Board):
        """Prints the entire game board to the console."""
        lines = []

        # --- Header: Stock, Waste, Foundations ---
        stock_str = (
            f"{self.COLOR_BLUE}[#]{self.COLOR_RESET}"
            if len(board.stock) > 0
            else "[ ]"
        )
        waste_str = self._format_card(board.waste.top_card) or "   "

        foundation_displays = []
        for f in board.foundations:
            display = self._format_card(f.top_card)
            if display is None:
                # No card, show a colored placeholder for the suit (e.g., "[♥]")
                suit_char = f.suit.value
                if f.suit.color == "red":
                    display = f"[{self.COLOR_RED}{suit_char}{self.COLOR_RESET}]"
                else:
                    display = f"[{suit_char}]"
            foundation_displays.append(display)

        foundations_str = " ".join(foundation_displays)

        moves_str = f"Moves: {board.move_count}/{MAX_MOVES}"
        lines.append(f"Stock: {stock_str}   Waste: {waste_str}   Foundations: {foundations_str}   {moves_str}")
        lines.append("")
        
        # --- Tableau Piles ---
        COL_WIDTH = 5
        header = [str(i).center(COL_WIDTH) for i in range(1, 8)]
        lines.append(" ".join(header))
        lines.append(" ".join(['---'.center(COL_WIDTH)] * 7))
        
        max_len = max(
            (p.face_down_count + len(p.face_up_cards)) for p in board.tableau_piles
        ) if board.tableau_piles else 0
        
        for i in range(max_len):
            row_list = []
            for j in range(7):
                cell_content = ""
                if j < len(board.tableau_piles):
                    pile: Tableau = board.tableau_piles[j]
                    
                    if i < pile.face_down_count:
                        # It's a face-down card
                        cell_content = f"{self.COLOR_BLUE}[#]{self.COLOR_RESET}"
                    elif i < pile.face_down_count + len(pile.face_up_cards):
                        # It's a face-up card
                        card_index = i - pile.face_down_count
                        card = pile.face_up_cards[card_index]
                        cell_content = self._format_card(card) or ""
                
                # Center the content within the column width
                row_list.append(self._center_ansi(cell_content, COL_WIDTH))
                
            lines.append(" ".join(row_list))

        # Clear the console and print the new board state
        # (The "clear" command works on Linux/macOS, "cls" on Windows)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n".join(lines))