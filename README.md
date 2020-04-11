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
   Peter as "the new Iron Man". However, the majority of each of these films has little to do with the other.
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
Each algorithm has 2 steps: 
 1. Generate a tree of possible candidates for inclusion in the recommended watchlist. 
 2. Iterate through all possible combinations of those candidates to determine the optimal selections from this set 
 of candidates. 
 
In step 1, edges of weight 1 are always treated as if they do not exist.
###Tier-based algorithms
2 of the 3 algorithms find candidates in a tier-based manner. All candidates in every tier except the outermost tier
will always be included. For example, if the user asks for 10 recommendations, and there are 5 movies in tier 1 and 4
in tier 2, all 5 movies in tier 1 and all 4 movies in tier 2 will be included, in addition to some 1 movie from tier 3.
#### Most Relevant
The "most relevant" ancestors of a movie are defined as such: the movies which are directly connected to this movie
in some way.

#### Most Recent
The "most recent" ancestors of a movie consist of the movies which are directly connected to this movie AND for which
there are no intermediate movies that also connect to this movie.

Thus, all ancestors in the 1st "most recent" tier of a movie will also be in that movie's 1st "most relevant" tier.
However, some movies in the "most relevant" tier might not be in the "most recent" tier.
 * Example: Age of Ultron's "most relevant" tier would include both _The Winter Soldier_ and _The Avengers_. However,
 since _Winter Soldier_ takes place between _The Avengers_ and _Age of Ultron_, _The Avengers_ would be excluded from
 _Age of Ultron_'s "most recent" tier.
 
#### Second tier
Sometimes, the user may request more movie recommendations than exist in the first tier. In this case, all movies in
the first tier will be recommended. In addition, some movies must be chosen from the second tier. In order to choose 
which movie to recommend, the algorithm reverts to recommending the movies from this tier which provide the most
interconnected experience overall. Note that the tier will still consist of the most recent or most relevant movies 
to all movies in the first tier; the interconnectivity algorithm will merely be used to choose which of these to
recommend. The same applies for third tier, fourth tier, etc.
 
###Most Interconnected
This algorithm simply generates a tree of all ancestors of this movie.