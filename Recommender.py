"""
Copyright 2020 William Locatelli.
A program which can perform various analyses on a weighted directed acyclic graph.
It is designed to be used for selecting movies from the Marvel Cinematic Universe,
but could be used for other applications with a few minor tweaks.
"""
import csv
import math
RULE = "Recent"
COUNT_RULE = "Count"
MOVIES = {}
GRAPHS_CHECKED = 0
NUM_TIES = 0


# takes in a CSV file, sets global variables for movies
# CSV must be formatted as adjacency matrix with weights in a cel representing the weight of the edge
# from parent column to child row
def import_weighted_from_csv(file="Data/MCUphase1to3-weighted.csv"):
    # put all the rows of the csv file into a list
    csv_rows = []
    with open(file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            csv_rows.append(row)
    title_list = csv_rows[0]
    # create movie objects
    all_movies = {}
    i = 1  # skip the title row
    movie_count = len(csv_rows)
    while i < movie_count:
        row = csv_rows[i]
        this_movie = Movie(row[0], series=row[1])
        all_movies[row[0]] = this_movie
        i += 1
    i = 1  # skip the title row
    while i < movie_count:
        prevs = []
        row = csv_rows[i]
        i2 = 2  # skip the series column
        while i2 < len(row):
            weight = row[i2]
            if len(weight) > 0 and weight != "0":
                # csv_rows[i] tells you what movies i comes from, so the prevs need to be found in the title list[i2]
                prevs.append((all_movies[title_list[i2]], float(weight)))
            i2 += 1
        all_movies[row[0]].prevs = prevs
        i += 1
    global MOVIES
    MOVIES = all_movies


# imports additional data from file
def import_data_from_csv(file="Data/data.csv"):
    csv_rows = []
    with open(file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            csv_rows.append(row)
    i = 1  # skip the title row
    movie_count = len(csv_rows)
    while i < movie_count:
        row = csv_rows[i]
        this_movie = MOVIES[row[0]]
        this_movie.rt_score = row[1]
        this_movie.date = row[2]
        i += 1


# returns global list of movies
def get_movies():
    return MOVIES


# sets global rule
def set_rule(rule):
    global RULE
    RULE = rule


# sets global count rule
def set_count_rule(count_rule):
    global COUNT_RULE
    COUNT_RULE = count_rule


# returns the number of graphs considered by the algorithm
def get_graphs_checked():
    return GRAPHS_CHECKED


# find the n best other movies to watch if you've watched the watched and want to watch the children
# parameters:
#           watched:    set of films which have already been watched
#           children:   set of films which they want to watch
#           num_extras: the number of additional films to be included
# returns: a list of movies, including all the movies in watched and children plus the up to n recommended films
def find_best_subgraph(watched, children, num_extras):
    nodes = children.copy()
    included_unwatched = children.copy()
    num_to_check = num_extras
    use_relevant = False
    if RULE != "Relevant":
        #  fill the nodes with all parents of the children, excluding isolated parents of the watched films.
        prev_tree(nodes, watched)
    else:
        #  generate each tier of ancestors one at a time, dequeuing the ancestors into the included_unwatched
        #  if fewer than num_extras ancestors have been discovered. nodes will contain the nodes in
        #  included_unwatched plus the nodes in the final tier.
        num_to_check, use_relevant = limited_prev_tree(nodes, watched, children, num_extras, included_unwatched)

    # add parents to nodes. they couldn't be added before because we didn't want their parents to also get added.
    for parent in watched:
        nodes.add(parent)
    # included is all the movies we know we are going to include
    included = list(watched | included_unwatched)
    # excluded is the candidate movies we are considering for inclusion
    excluded = []
    # if there are less extra films than the total requested films, return all the films.
    if len(nodes) <= num_extras + len(children) + len(watched):
        return list(nodes)
    else:
        for movie in nodes:
            if movie not in included:
                excluded.append(movie)
    if RULE == "Recent":
        best_graphs = [most_recent_movies(excluded, included, num_to_check)]
    else:
        if use_relevant:
            initial_weight = subgraph_weight(watched, children)
        else:
            initial_weight = subgraph_weight(included, included)
        num_to_check = ensure_small(excluded, included, num_to_check)
        graphs_and_weights = brute_force_subgraph_helper(excluded, included, num_to_check, included_unwatched, initial_weight, relevant=use_relevant)
        best_graphs = []
        for graph, weight in graphs_and_weights:
            best_graphs.append(graph)

    #print(best_graphs)
    result = tie_breaker(best_graphs, excluded, included_unwatched, watched)
    return result


# generates a watch order, excluding movies which have already been watched
# parameters:
#           watched: set of movies which have already been watched
#           subgraph: list of the all the movies in the watch list
# return format: string
def watch_order(watched, subgraph):
    order = []
    for movie in MOVIES:
        if MOVIES[movie] in subgraph and not MOVIES[movie] in watched:
            order.append(movie)
    return order


##############################################  HELPER FUNCTIONS  ##############################################

# ensures there are no more than 500,000 possible combinations of the given films
# modifies excluded, included, and n, adding Avengers movies from excluded to included if there are too many
# combinations
def ensure_small(excluded, included, n):
    excluded_copy = excluded.copy()
    f = math.factorial
    size = f(len(excluded)) // f(n) // f(len(excluded)-n)
    if size > 500000:
        for movie in excluded_copy:
            if "Avengers" in movie.name:
                excluded.remove(movie)
                included.append(movie)
                n = n-1
    return n


# Returns a list containing included plus the num most recent movies in excluded.
def most_recent_movies(excluded, included, num):
    excluded_sorted = sorted(excluded, key=lambda x: x.date, reverse=True)
    i = 0
    result = included.copy()
    while i < num:
        result.append(excluded_sorted[i])
        i += 1
    return result


# Iterates through every possible set of movies containing the movies in included and
# n of the movies in excluded. Sums the edge weights between movies in each set, and
# keeps track of the sets which have the highest total weight.
# Returns a list containing all the sets which are tied for first place.
# parameters:
#           excluded: films which aren't currently in any of the other lists
#           included: films which should be included in every graph
#           children: the films people want to watch - a subset of included
#           n:        the size of each final graph should equal len(included) + n
#           relevant: if True, compute subgraph weight based on edges from parents to children
def brute_force_subgraph_helper(excluded, included, n, children, parent_weight, relevant=False):
    global GRAPHS_CHECKED
    best_graphs = []
    if n == 0:
        GRAPHS_CHECKED += 1
        subgraph = included.copy()
        return [(subgraph, parent_weight)]
    max_weight = 0
    # best_graph = included
    excluded_copy = excluded.copy()
    included_copy = included.copy()
    while len(excluded_copy) > n - 1:
        movie = excluded_copy[0]
        if relevant:
            current_weight = subgraph_weight([movie], children) + parent_weight
        else:
            current_weight = subgraph_weight([movie], included_copy) + subgraph_weight(included_copy, [movie]) + parent_weight
        included_copy.append(movie)
        excluded_copy.remove(movie)
        best_graph_next_level = brute_force_subgraph_helper(excluded_copy, included_copy, n - 1, children, current_weight, relevant)
        graph, weight = best_graph_next_level[0]
        if weight > max_weight:
            max_weight = weight
            best_graphs = best_graph_next_level.copy()
        elif weight == max_weight:
            best_graphs += best_graph_next_level
        included_copy.remove(movie)
    return best_graphs


# Breaks ties based on a series of 3 criteria:
#       1. Which graph has highest weight if parents are removed?
#       2. Which graph has highest weight if edges are ignored and
#               nodes are weighted by RottenTomatoes scores?
#       3. Which graph has highest weight if we add up the weights of all the
#               connections its films have to other movies?
# parameters:
#       best_graphs - a list of graphs which all have equal weight
#       excluded    - movies which aren't currently included in any of the graphs
#       children    - the movies people want to watch
#       parents     - the movies people have already watched
#
# returns: the best graph
def tie_breaker(best_graphs, excluded, children, parents):
    if len(best_graphs) == 1:
        return best_graphs[0]
    else:
        best_graph = None
        max_score = 0
        best_graphs_2 = []
        # choose subgraph of highest weight when parents are removed
        i = 0
        best_graphs_no_parents = []
        while i < len(best_graphs):
            best_graphs_no_parents.append(list(set(best_graphs[i]) - parents))
            i += 1
        i = 0
        while i < len(best_graphs):
            score = subgraph_weight(best_graphs_no_parents[i], best_graphs_no_parents[i])
            if score > max_score:
                best_graphs_2 = [best_graphs[i]]
                best_graph = best_graphs[i]
                max_score = score
            elif score == max_score:
                best_graphs_2.append(best_graphs[i])
            i += 1
        # if not enough, choose subgraph of highest cumulative RT score
        if len(best_graphs_2) > 1:
            max_score = 0
            for graph in best_graphs:
                score = sum(int(movie.rt_score) for movie in graph)
                if score > max_score:
                    best_graphs_2 = [graph]
                    best_graph = graph
                    max_score = score
                elif score == max_score:
                    best_graphs_2.append(graph)
        # if that wasn't enough, choose subgraph of highest cumulative weight of ancestors
        if len(best_graphs_2) > 1:
            max_score = 0
            for graph in best_graphs_2:
                score = 0
                for movie in graph:
                    score += sum(int(prev[1]) for prev in movie.prevs)
                if score > max_score:
                    best_graph = graph
                    max_score = score
                elif score == max_score:
                    print("not rigorous enough")
        return best_graph


# NOTE: THIS FUNCTION MODIFIES THE PARAMETER NODES
# generates subgraph containing all ancestors of every node in nodes
# parameters:
#       nodes: set of nodes whose ancestors we want to find
#       watched: the films we've already watched. use to block the pipe so that those films' ancestors aren't scanned
def prev_tree(nodes, watched):
    nodes_copy = nodes.copy()
    for movie in nodes_copy:
        for prev in movie.prevs:
            if prev[1] > 4 and prev[0] not in watched and prev[0] not in nodes:
                nodes.add(prev[0])
                prev_tree(nodes, watched)


# NOTE: THIS FUNCTION MODIFIES THE PARAMETERS NODES AND INCLUDED_UNWATCHED
# Generates a limited ancestor tree, containing only more recent ancestors.
# Ancestors are broken up into generations. All ancestors from every generation up to n ancestors
# will be returned in nodes, while all ancestors from every generation except the most ancient will
# be returned in included_unwatched.
# The final tier which reaches or surpasses n will be included; in other words, the final size of nodes
# will always be greater than or equal to n + children, while the final size of included_unwatched will
# always be less than or equal to n + children.
# Parameters:
#   nodes: set of all unwatched nodes in the graph
#   watched: set of films which have already been watched
#   children: set of films which were requested
#   included_unwatched: set of every unwatched film which is guaranteed to be included in output
#   num_extras: number of ancestors to add to nodes before stopping
# Returns a tuple containing:
#   The number of additional films in nodes which should be added to children using some other algorithm.
#   True iff the subgraph weight should be calculated based on most_relevant
def limited_prev_tree(nodes, watched, children, num_extras, included_unwatched):
    use_relevant = False
    # Get ancestors of these nodes
    ancestors = next_tier(nodes)
    unwatched_ancestors = ancestors - watched
    nodes.update(unwatched_ancestors)  # put unwatched ancestors into nodes
    n = len(nodes) - len(children)  # n is the number of additional movies we have added so far
    if n > num_extras:
        use_relevant = True
    else:
        while len(ancestors) > 0 and n < num_extras:  # if n == num_extras, we won't enter the loop
            # Dump unwatched ancestors into included unwatched
            included_unwatched.update(unwatched_ancestors)
            ancestors = next_tier(unwatched_ancestors) - children  # get new ancestors
            unwatched_ancestors = ancestors - watched
            nodes.update(unwatched_ancestors)  # Dump unwatched ancestors into nodes
            n = len(nodes) - len(children)
    # put sets back into lists
    return num_extras - (len(included_unwatched) - len(children)), use_relevant


# computes and returns the weight of all links between set parents and set children
# if the same set is passed for parents and children, it will compute the weight of
# all links between all elements in the set
def subgraph_weight(parents, children):
    weight = 0
    for movie in children:
        for prev in movie.prevs:
            if prev[0] in parents:
                weight += prev[1]
    return weight


# returns the most recent ancestors of a set of movies. If RULE == Most Recent,
# trims off any ancestors of other ancestors and returns them in discarded_predecessors.
def next_tier(movies):
    # step 1: find all nodes which are immediately relevant
    direct_predecessors = set()
    for movie in movies:
        for prev in movie.prevs:
            if prev[0] not in direct_predecessors and prev[1] > 4:
                direct_predecessors.add(prev[0])
    return direct_predecessors


# Movies have names, series, release dates,and lists of previous (and potentially next) films.
class Movie:
    def __init__(self, name, series="", date=""):
        self.prevs = []  # the parents of this movie
        self.seqs = []  # the children of this movie (unused field)
        self.name = name  # the name of the movie
        self.series = series  # the film series this movie belongs to
        self.date = date
