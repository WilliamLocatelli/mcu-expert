# mcu-tracker
Program for exploring the watch order of the MCU.
Run MarvelTracker.py to explore the interactive MCU watch-through, which follows strict rules with regards to when you 
are allowed to watch certain movies.
Run Recommender.py to see what movies you should watch in between other movies.

## Rules for choosing edge weights
Edge weights are chosen based on two criteria: internal references to previous movies, and external definition of 
relationship to previous movies. 

External definition:
 - 20: These 2 movies were conceived of, planned, and written at the same time, and for all intents and purposes can be 
 seen as 2 halves of the same story (currently only true for Infinity War/Endgame)
 - 10: This movie is explicitly defined as a direct sequel to the previous movie
 - 5: This movie is explicitly defined as a sequel to the previous movie, but not a direct sequel.
 
Internal references:
 - 10: The way that this entire movie is understood by the viewer will be different if they have seen this previous 
 movie
 - 5: Some scenes or plot points in this movie will be understood very differently by the viewer of they have seen this 
 previous movie.
 - 1: There are some lines of dialogue which reference events of these previous movies, but understanding the context
 of these lines of dialogue will not in any way affect your understanding of this movie.
 
 The weight of an edge will always be equal to the highest weight criteria in this list that applies.
 
 ## Algorithms
 Each algorithm has 2 steps. The first step involves generating a tree of possible candidates for inclusion in the
 recommended watchlist. The second step involves iterating through all possible combinations of those candidates to 
 determine the optimal selections from this set of candidates.