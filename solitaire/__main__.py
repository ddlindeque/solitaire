import argparse
import copy
import time

from solitaire.board import Board, MAX_MOVES
from solitaire.player import AIPlayer, HumanPlayer, Player, SimplePlayer
from solitaire.view import TextView


def play_game(board: Board, player: Player, view: TextView, interactive: bool = True) -> bool:
    """
    Runs a single game of Solitaire.

    Args:
        board: The game board instance.
        player: The player instance (Human or AI).
        view: The view instance for display.
        interactive: If False, suppresses console output for faster execution (e.g., training).

    Returns:
        True if the game was won, False otherwise (loss or quit).
    """
    while not board.is_win():
        # Check for move limit at the start of the turn.
        if board.move_count >= MAX_MOVES:
            if interactive:
                view.display(board)
                print(f"\nMaximum move limit of {MAX_MOVES} reached. Game over!")
            return False  # Game lost

        if interactive:
            view.display(board)

        all_legal_moves = board.get_legal_moves()

        # Filter out moves that would result in a previously seen game state
        productive_moves = []
        for move in all_legal_moves:
            temp_board = copy.deepcopy(board)
            temp_board.execute_move(move)
            new_state_hash = temp_board._get_state_hash()
            if new_state_hash not in board._state_history:
                productive_moves.append(move)

        moves_to_consider = productive_moves if productive_moves else all_legal_moves

        if not moves_to_consider:
            if interactive:
                print("No legal moves available. Game over!")
            return False  # Game lost

        if len(moves_to_consider) == 1 and interactive:
            selected_move = moves_to_consider[0]
            player.notify_automatic_move(selected_move)
        else:
            # For non-interactive AI, just pick the move without asking
            selected_move = player.select_move(board, moves_to_consider)

        if selected_move is None:
            if interactive:
                print("Quitting game. Goodbye!")
            return False  # Game quit by player

        board.execute_move(selected_move)
        new_state_hash = board._get_state_hash()
        board._state_history.add(new_state_hash)

    if board.is_win():
        if interactive:
            view.display(board)
            print("Congratulations, you won!")
        return True
    return False  # Should be unreachable, but as a fallback


def run_human_game(args):
    """Sets up and runs a standard game for a human player."""
    board = Board()
    board.setup()
    #player = HumanPlayer()
    player = SimplePlayer()
    view = TextView()
    play_game(board, player, view, interactive=True)


def run_training_session(args):
    """Runs the AI against increasingly difficult random scenarios."""
    print("Starting AI Training Session...")
    if args.params:
        print(f"Note: Loading parameters from '{args.params}' is not yet implemented.")

    max_cards = args.max_cards
    num_trials = args.trials

    for num_cards in range(1, max_cards + 1):
        wins = 0
        start_time = time.time()
        for i in range(num_trials):
            board = Board()
            board.setup_random_scenario(number_of_cards=num_cards)
            # Use a non-verbose AI for speed
            player = AIPlayer(verbose=False)
            if play_game(board, player, view, interactive=False):
                wins += 1

        end_time = time.time()
        duration = end_time - start_time
        win_rate = (wins / num_trials) * 100
        print(
            f"Level {num_cards} ({num_cards} face-down cards): "
            f"Win rate: {win_rate:.1f}% ({wins}/{num_trials} wins) "
            f"in {duration:.2f} seconds."
        )


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="A command-line Solitaire game with an AI training mode."
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # --- 'play' command ---
    play_parser = subparsers.add_parser(
        "play", help="Play an interactive game of Solitaire."
    )
    play_parser.set_defaults(func=run_human_game)

    # --- 'train' command ---
    train_parser = subparsers.add_parser(
        "train", help="Run an AI training session."
    )
    train_parser.add_argument(
        "--max-cards", type=int, default=5, help="Maximum number of face-down cards to test (difficulty)."
    )
    train_parser.add_argument(
        "--trials", type=int, default=5000, help="Number of games to run for each difficulty level."
    )
    train_parser.add_argument(
        "--params", type=str, help="Path to a file with AI parameters (not yet implemented)."
    )
    train_parser.set_defaults(func=run_training_session)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
