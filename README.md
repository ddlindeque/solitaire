[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ddlindeque/solitaire)

# Solitaire

## Gameplay

## Game state analysys

I belief this game board state forms a category with board state as a node, and moves as edges.

We have the following kinds of moves (morphisms)

*   **`DoNothing`**: Does nothing. We will not actually implement this.
*   **`DrawFromStock`**: Draws a card from the stock to the waste pile.
*   **`ResetStock`**: Resets the stock from the waste pile when the stock is empty.
*   **`WasteToFoundation`**: Moves the top card of the waste to a foundation pile.
*   **`WasteToTableau`**: Moves the top card of the waste to a tableau pile.
*   **`TableauToFoundation`**: Moves the top card of a tableau to a foundation pile.
*   **`FoundationToTableau`**: Moves a card from a foundation pile back to a tableau pile.
*   **`TableauToTableau`**: Moves one or more cards from one tableau pile to another.

### Is this a category?

Yes, it operates like **SET**. Move *morphisms* are exactly like a function operating on a state, which is the state of the board.

### Identifying isomorphisms

An *isomophism* can be *undone* (i.e.: go back to the previous state) by one or more (composition) of other moves (morphisms).

Note that you can never move a card from the tableau or foundation piles to the stock or waste piles, but you can move cards from the waste pile to both the tableau and foundation piles. You can also move cards between the stock and waste piles (under certain rules). This means that the number of cards in the stock plus waste piles, will always only stay the same or decrease.

Also, once a card was revealed, it cannot be 'unrevealed' again. So, no 'undo' can exist after revealing a new card.

*   **`DoNothing`**: Does nothing. We will not actually implement this.
        * Isomorphic with itself. It's the *identity*
*   **`DrawFromStock`**: Draws a card from the stock to the waste pile.
        * We can reach our current state again, by **`DrawFromStock`**, then **`ResetStock`**, and **`DrawFromStock`** until we reach this state.
        * Thus **`DrawFromStock`** ∘ **`DrawFromStock`**^n ∘ **`ResetStock`** ∘ **`DrawFromStock`**^m = **`DrawFromStock`**
        * This means, if B = **`DrawFromStock`**(A), then A and B are isomorphic.
*   **`ResetStock`**: Resets the stock from the waste pile when the stock is empty.
        * We can reset, then draw until we reset again
        * Thus **`ResetStock`** ∘ **`DrawFromStock`**^m ∘ **`ResetStock`** = **`ResetStock`**
        * This means, if B = **`ResetStock`**(A), then A and B are isomorphic.
*   **`WasteToFoundation`**: Moves the top card of the waste to a foundation pile.
        * The waste+stock pile has reduced in size, and can never increase again, so this cannot have an isomorhism
*   **`WasteToTableau`**: Moves the top card of the waste to a tableau pile.
        * The waste+stock pile has reduced in size, and can never increase again, so this cannot have an isomorhism
*   **`TableauToFoundation`**: Moves the top card of a tableau to a foundation pile.
        * This can always be undone when the move doesn't reveal a new card.
*   **`FoundationToTableau`**: Moves a card from a foundation pile back to a tableau pile.
        * This is the inverse of a `TableauToFoundation` move and is always an isomorphism as it never reveals a card.
*   **`TableauToTableau`**: Moves one or more cards from one tableau pile to another.
        * This can always be undone when the move doesn't reveal a new card.

#### Conclusion

* All states with count(stock+waste) = count(stock'+waste'), and count(unrevealed) = count(unrevealed'), are isomorphic.
    * **`DrawFromStock`**
    * **`ResetStock`**
    * **`TableauToFoundation`** when not revealing a new card
    * **`FoundationToTableau`**
    * **`TableauToTableau`** when not revealing a new card
* All states with count(stock+waste) != count(stock'+waste'), or count(unrevealed) != count(unrevealed'), are not isomorphic.
    * **`WasteToFoundation`**
    * **`WasteToTableau`**
    * **`TableauToFoundation`** when revealing a new card
    * **`TableauToTableau`** when revealing a new card

### Vectorising game state

* Given we have a consistent *start condition*:

* A card can be vectorised as a 2 dimensional array, one for the suite and one for the rank. 2 of hearts are close to 2 of clubs, and 2 of hearts are also close to 3 of hearts. A zero in both places indicate `no card`.

* Since all states with the same number of cards stock+waste and same number of unrevealed cards are isomorphic, we can conclude:
    * The cards in the waste and stock piles can be merged into a single set, and the order doesn't matter. We can have a maximum of 52 - 1+2+3+4+5+6+7 = 24 cards in these piles. So, we'll have an input to the network of 24 positions for these cards. They'll be ordered to remove bias. How?
* The number of unrevealed cards are just an integer number. Since all states not revealing a new card are isomorphic, we just need the number of unrevealed cards.

This vectorisation can be used for understanding the state of the game up to isomorphism. This is useful for rating the board.

## Training

### Rate the board

* We get a vectorisation for the board as described above.
* Here we just want to be able to rate the board current state, and give an estimate of how probable it will be to solve the board from here.
* This means we can test moves and get an indication of how good a move is.
* We start by using a board with one unrevealed card. This is easy to find the number of steps to solve this (1).
