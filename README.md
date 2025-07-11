[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ddlindeque/solitaire)

# Solitaire

## Game state analysys

I belief this game board state forms a category with board state as *objects*, and moves as *morphisms*. We do not have a *terminal* object, since we can terminate in *win* (1 object) or *lost* (many objects). We also do not have an *initial* object, since we start with a random state of cards (unless we introdue a *shuffle* move).

We have the following kinds of moves (morphisms)

*   **`DoNothing`**: Does nothing. We will not actually implement this. This will be the *identity*.
*   **`DrawFromStock`**: Draws a card from the stock to the waste pile.
*   **`ResetStock`**: Resets the stock from the waste pile when the stock is empty.
*   **`WasteToFoundation`**: Moves the top card of the waste to a foundation pile. This move is not reversable.
*   **`WasteToTableau`**: Moves the top card of the waste to a tableau pile. This move is not reversable.
*   **`TableauToFoundation`**: Moves the top card of a tableau to a foundation pile without revealing a new card, or leaving an empty tableau, unless the card was a King.
*   **`TableauToFoundationAndReveal`**: Moves the top card of a tableau to a foundation pile, revealing a new card, or an empty tableau when the card was not a King. This move is not reversable.
*   **`FoundationToTableau`**: Moves a card from a foundation pile back to a tableau pile.
*   **`TableauToTableau`**: Moves one or more cards from one tableau pile to another without revealing a new card, or leaving an empty tableau, unless the card was a King.
*   **`TableauToTableauAndReveal`**: Moves one or more cards from one tableau pile to another, revealing a new card, or an empty tableau when the card was not a King. This move is not reversable.

### Is this a category?

Yes, it operates like **SET**. Move *morphisms* are exactly like a functions operating on a state, which is the state of the board.
* **Identity**: The *DoNothing* move. For now, we will ignore this morphism going forward, since it does nothing.
* **Composition**: A legal move can always be followed by another legal move (for that state/object), unless we reached a state with no valid moves (like win or loose), thus we can *compose* two legal moves.
* **Associativity**: This is like **SET**, so associativity holds (homework excercise). A legal move can always follow another legal move, which can then always follow another legal move. Whether I do the first two moves as a 'unit', and then the third, or the first, then the second and third as a 'unit', doesn't matter. The concept of a 'unit' doesn't really exist.

What is an object?
* The top cards in the foundation stacks
* The revealed cards for each pile in the tableau piles
* The number of hidden cards in each tableau pile
* The cards in the waste and stock piles. It is true that we do not know the cards in the stock pile when the game starts, but the player can always cycle through the whole stock pile without playing any other moves until the whole stock pile has been moved to the waste pile, followed by a `reset` to get back to the initial state, but now the play (with a good memory) will know the cards in both piles.
* The current top card in the waste pile.
* Flag indicating whether the stock pile is empty.

Let's call this category **SOL**.

### Identifying isomorphisms

An *isomophism* can be *undone* (i.e.: go back to the previous state/object) by one or more (composition) of other moves/morphisms.

Note that you can never move a card from the tableau or foundation piles to the stock or waste piles, but you can move cards from the waste pile to both the tableau and foundation piles. You can also move cards between the stock and waste piles (under certain rules). This means that the number of cards in the stock plus waste piles, will always only stay the same or decrease. Also, once a card was revealed, it cannot be 'unrevealed' again. So, no 'undo' can exist after revealing a new card, so the number of unrevealed tableau cards will always stay the same or decrease.

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
*   **`TableauToFoundation`**: Moves the top card of a tableau to a foundation pile without revealing a new card.
    * This is an isomorphism as it can be undone by a **`FoundationToTableau`** move.
*   **`TableauToFoundationAndReveal`**: Moves the top card of a tableau to a foundation pile, revealing a new card.
    * The number of reveal cards in the tableau's has been reduced, and never be increased, so we cannot reach this state/object again by any legal move/morphish, so this cannot have an isomorhism.
*   **`FoundationToTableau`**: Moves a card from a foundation pile back to a tableau pile.
    * This is the inverse of a **`TableauToFoundation`** move and is always an isomorphism as it never reveals a card.
*   **`TableauToTableau`**: Moves one or more cards from one tableau pile to another without revealing a new card.
    * This is an isomorphism as it can be undone by moving the same stack back.
*   **`TableauToTableauAndReveal`**: Moves one or more cards from one tableau pile to another, revealing a new card.
    * This is not an isomorphism as a card is revealed, which can never be 'unrevealed', or .

#### Conclusion

* The following morphisms are all isomorphic.
    * **`DrawFromStock`**
    * **`ResetStock`**
    * **`TableauToFoundation`**
    * **`FoundationToTableau`**
    * **`TableauToTableau`**
* The following are never isomorphic.
    * **`WasteToFoundation`**
    * **`WasteToTableau`**
    * **`TableauToFoundationAndReveal`**
    * **`TableauToTableauAndReveal`**

#### Functor

We can define a functor that maps from the game state (objects) to this new category where all isompohic objects are one object, and only morphisms which 'makes progress', exist in the category. We can define it as follows:

`F(DrawFromStock) = id`
`F(ResetStock) = id`
`F(TableauToFoundation) = id`
`F(FoundationToTableau) = id`
`F(TableauToTableau) = id`

`F(WasteToFoundation) = wf`
`F(WasteToTableau) = wt`

`F(TableauToFoundationAndReveal) = tf`
`F(TableauToTableauAndReveal) = tt`

Let's call this category **SOL2**.

The challange is to find this category, i.e.: from a board state, find the different morphisms legal on this state. Note that **SOL2** doesn't contain any isomorphisms.

#### Proofs for solvability

##### 1 or 2 cards unrevealed

*Hypothesis*:
In **SOL2**, with only 1 or 2 cards unrevealed, we can always play **F(WasteToFoundation)** and/or **F(WasteToTableau)** until the waste and stock piles are empty.

*Proof*:
* Let's call the top of the waste pile *W*.
* Let's use the notation `(X,a)` to denote a card with suite `X` and face value `a`.
* Let's say *W* is `(Y,b)`
* The requirement for **F(WasteToFoundation)** to be a valid morphism is for the foundation pile to have `(Y,b-1)` as the top.
* The requirement for **F(WasteToTableau)** is for the tableau set of cards to contain a top card `(C1,b+1)` or `(C2,b+1)` where `C1<>C2` but have the same colour, different to the colour of `Y`.
* `(Y,b-1) <> (C1,b+1)` since `b-1<b+1`.
* `(Y,b-1) <> (C2,b+1)` for the same reason.
* `(C1,b+1) <> (C2,b+1)` from above.
* This means we have three different cards in `(Y,b-1)`, `(C1,b+1)` and `(C2,b+1)`. Even if the two unrevealed cards are two of those, there's still a third one left, so we can play that move.
* The edge cases are when `b=1`, i.e.: it is an ACE card. In this case, the ACE can always be moved to the Foundation pile. It'll ALWAYS be possible.
* The only other edge case is when `b=13`, i.e.: the KING card. In this case the KING can be placed on an empty tableau location. At this point in the game, we will always be able to have an empty tableau, since we have 4 suites, and 7 locations.

*Hypothesis*:
In **SOL2**, with only 1 or 2 cards unrevealed, and both the waste and stock piles empty, the **F(TableauToFoundationAndReveal)** or **F(TableauToTableauAndReveal)** moves are always available.

*Proof*:
* The requirements for **F(TablauToFoundationAndReveal)** are:
  * The tableau pile with the unrevealed card must have only a single revealed card left `(R,a)`.
  * The foundation pile for suite `R` must have `(R,a-1)` as top card.
* The requirements for **F(TableauToTableauAndReveal)** are:
  * The tableau pile with the unrevealed card must have only a single revealed card left `(R,a)`.
  * There must be another tableau pile with `(C1,a+1)` or `(C2,a+1)` with `C1<>C2` and colour different to `R`.
* This means we have 3 unique options, and only 1 or 2 hidden cards. There will always be at least a third option avialable.

##### 3 or more

For the proofs above, if we have three hidden cards, we can always end up with a state where all three cards are hidden. As an example:
We have a tableau pile with 3 hearts, 3 diamonds, and ace of clubs hidden, covered by 2 of clubs. In this case we can never move the 2 of clubs to the foundation for clubs, since the ace of clubs are hidden by the same card. We will also never be able to move the 2 of clubs to another tableau pile, since both the red 3's are hidden by this card. In general, if we have `(Y,b-1)`, `(C1,b+1)` and `(C2,b+1)` hidden by `(Y,b)`, this will be unsolvable, even when we have more than just these three cards hidden.

## Training

### Rate the board

* We rate boards based on **SOL2**. All isomophic boards are rated the same.
* All 1 or 2 hidden card boards are 100% solvable (probability of `1`).
* A 3 hidden card board are either solvable or not (probability of `0` or `1`).
* An x hidden card board has a likelyhood of being solvable (given we select random moves). Each **SOL2** morphism (`m1, m2, ..., mk`) will lead to a board that's got a probability of being solvable, let's call that `p1, p2, ..., pk`. So the total probability is `(p1 + p2 + ... + pk)/k`.
* So, the probability of a board being solvable at move `i`, is the sum of the probabilities of all the boards reachable by **SOL2** morphisms, devided by the number of those morphisms.
* We train a network for every step, i.e.: one for 4 hidden cards, one for 5 hidden cards, etc., etc.




### Select a move

