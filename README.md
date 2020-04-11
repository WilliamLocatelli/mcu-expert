# mcu-tracker
Program for exploring the watch order of the MCU.
Run MarvelTracker.py to explore the interactive MCU watch-through, which follows strict rules with regards to when you 
are allowed to watch certain movies.
Run RecommenderGUI.py to see what movies you should watch in between other movies.

## Rules for choosing edge weights
Edge weights are chosen based on two criteria: internal references to previous movies, and external definition of 
relationship to previous movies. 

External definition:
 * 10: This movie is explicitly defined as a direct sequel to the previous movie 
   * Example: Iron Man - Iron Man 2
 * 5: This movie is explicitly defined as a sequel to the previous movie, but not a direct sequel.
   * Example: Iron Man - Iron Man 3
 
Internal references:
 * 10: The way the viewer understands most or all of this movie will depend on whether they have seen this previous 
 movie.
   * Example: Captain America: Civil War is not explicitly a sequel to Avengers: Age of Ultron, but many of the actions
  characters take in this film, from the creation of the Sokovia accords to Clint's willingness to break the law and
  come out of retirement to rescue Wanda, directly stem from the events of Age of Ultron.
 * 5: Some scenes or plot points in this movie will be understood very differently by the viewer if they have seen this 
 previous movie.
   * Example: Spider-Man: Far From Home contains a flashback to Iron Man ("Tony Stark was able to build this in a 
   cave!") and several callbacks to Iron Man (such as when Peter designs the suit) which support the perception of 
   Peter as "the new Iron Man". However, the majority of each of these films has little to nothing to do with the other.
 * 5: This previous movie was the most recent appearance of one or more of the characters in this movie.
   * Example: Black Panther was the most recent appearance of Black Panther before Avengers: Infinity War.
 * 1: There are some brief moments which reference events of these previous movies, but understanding the context
 of these moments will not in any way affect your understanding of this movie.
   * Example: In Iron Man 3, Aldrich Killian says "Ever since that big dude with the hammer fell out of the sky, 
   subtlety has kind of had its day." This quote directly references Thor, but it in no way impacts a viewer's 
   understanding or interpretation of the scene.
 
 There is one more criterion that currently only applies to Infinity War/Endgame:
 
 * 20: These 2 movies were conceived of, planned, and written at the same time, and for all intents and purposes can be 
 seen as 2 halves of the same story
 
 The weight of an edge will always be equal to the highest weight criteria in this list that applies.
 
 ## Algorithms
 Each algorithm has 2 steps. The first step involves generating a tree of possible candidates for inclusion in the
 recommended watchlist. The second step involves iterating through all possible combinations of those candidates to 
 determine the optimal selections from this set of candidates.
