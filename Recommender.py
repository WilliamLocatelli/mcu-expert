"""
Copyright 2020 William Locatelli.
A program which can perform various analyses on a weighted directed acyclic graph.
It is designed to be used for selecting movies from the Marvel Cinematic Universe,
but could be used for other applications with a few minor tweaks.
"""
import csv

RULE = "Relevant"
COUNT_RULE = "Count"
CURRENT_ANCESTOR_TIER = 0
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
#           watched:    list of films which have already been watched
#           children:   list of films which they want to watch
#           num_extras: the number of additional films to be included
#           rule:       the heuristic to be used to select additional films
# returns: a list of movies - the set of movies which has the highest weight
def find_best_subgraph(watched, children, num_extras):
    nodes = children.copy()
    included_unwatched = children.copy()
    num_to_check = num_extras
    if RULE == "Interconnected":
        #  fill the nodes with all parents of the children, excluding isolated parents of the watched films.
        prev_tree(nodes, watched)
    else:
        #  generate each tier of ancestors one at a time, dequeuing the ancestors into the included_unwatched
        #  if fewer than num_extras ancestors have been discovered. nodes will contain the nodes in
        #  included_unwatched plus the nodes in the final tier.
        num_to_check = limited_prev_tree(nodes, watched, included_unwatched, num_extras)
    # add parents to nodes. they couldn't be added before because we didn't want their parents to also get added.
    for parent in watched:
        nodes.append(parent)
    included = watched + included_unwatched
    excluded = []
    # if there are less extra films than the total requested films, return all the films.
    if len(nodes) <= num_extras + len(children) + len(watched):
        return nodes
    else:
        for movie in nodes:
            if movie not in included:
                excluded.append(movie)
    best_graphs = brute_force_subgraph_helper(excluded, included, num_to_check, included_unwatched)
    result = tie_breaker(best_graphs, excluded, included_unwatched, watched)
    return result


# generates a watch order, excluding movies which have already been watched
# parameters:
#           watched: list of movies which have already been watched
#           subgraph: list of the all the movies in the watch list
# return format: string
def watch_order(watched, subgraph):
    order = []
    for movie in MOVIES:
        if MOVIES[movie] in subgraph and not MOVIES[movie] in watched:
            order.append(movie)
    return order


##############################################  HELPER FUNCTIONS  ##############################################


# Iterates through every possible set of movies containing the movies in included and
# n of the movies in excluded. Sums the edge weights between movies in each set, and
# keeps track of the sets which have the highest total weight.
# Returns a list containing all the sets which are tied for first place.
# parameters:
#           excluded: films which aren't currently in any of the other lists
#           included: films which should be included in every graph
#           children: the films people want to watch - a subset of included
#           n:        the size of each final graph should equal len(included) + n
def brute_force_subgraph_helper(excluded, included, n, children):
    global GRAPHS_CHECKED
    best_graphs = []
    if n == 0:
        GRAPHS_CHECKED += 1
        subgraph = included.copy()
        return [subgraph]
    max_weight = 0
    # best_graph = included
    excluded_copy = excluded.copy()
    included_copy = included.copy()
    while len(excluded_copy) > n - 1:
        movie = excluded_copy[0]
        included_copy.append(movie)
        excluded_copy.remove(movie)
        best_graph_next_level = []
        best_graph_next_level += brute_force_subgraph_helper(excluded_copy, included_copy, n - 1, children)
        if RULE == "Relevant" and CURRENT_ANCESTOR_TIER < 2:
            weight = subgraph_weight(list(set(best_graph_next_level[0]) - set(children)), children)
        else:
            weight = subgraph_weight(best_graph_next_level[0], best_graph_next_level[0])
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
            best_graphs_no_parents.append(list(set(best_graphs[i]) - set(parents)))
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
#       nodes: the nodes whose ancestors we want to find
#       watched: the films we've already watched. use to block the pipe so that those films' ancestors aren't scanned
def prev_tree(nodes, watched):
    for movie in nodes:
        for prev in movie.prevs:
            if prev[1] > 4 and prev[0] not in watched and prev[0] not in nodes:
                nodes.append(prev[0])
                prev_tree(nodes, watched)


# NOTE: THIS FUNCTION MODIFIES THE PARAMETERS NODES AND CHILDREN
# Generates a limited ancestor tree, containing only more recent ancestors
# ancestors are broken up into generations. All ancestors from every generation up to n ancestors
# will be returned in nodes, while all ancestors from every generation except the most ancient will
# be returned in children.
#
# The final tier which reaches or surpasses n will be included; in other words, the final size of nodes
# will always be greater than or equal to n + children, while the final size of children will always be
# less than or equal to n + (the original size of) children.
# Parameters:
#   nodes: all unwatched nodes in the graph
#   watched: films which have already been watched
#   children: films which were requested
#   n: number of ancestors to add to nodes before stopping
# Returns: The number of additional films in nodes which should be added to children using some other algorithm.
def limited_prev_tree(nodes, watched, children, n):
    global CURRENT_ANCESTOR_TIER
    # all of the nodes whose ancestors have been checked, and all of the ancestors. different from nodes in that nodes
    # does not include any watched.
    total_nodes = nodes.copy()
    requested_watchlist_count = len(children) + n
    current_level_nodes = nodes.copy()  # the list of nodes whose parents we are currently finding
    discarded_nodes = []  # used only for Most Recent heuristic
    recently_added_nodes = []  # represents the newest tier (not including any children in the tier)
    while len(nodes) < requested_watchlist_count and (len(current_level_nodes) > 0 or len(discarded_nodes) > 0):
        CURRENT_ANCESTOR_TIER = CURRENT_ANCESTOR_TIER + 1
        children.clear()
        children.extend(nodes)

        # Get the next tier. Split the tier up based on whether the films in it have already been checked.
        prev_nodes, recently_discarded_nodes = next_tier(current_level_nodes)
        recently_added_nodes.clear()
        children_duplicates = []  # handles situation where a tier contains one of the other movies they wanted to watch
        for prev in prev_nodes:
            if prev not in recently_added_nodes and prev not in total_nodes:
                recently_added_nodes.append(prev)
            else:
                children_duplicates.append(prev)

        # Add the new arrivals to the list of total nodes checked.
        total_nodes.extend(recently_added_nodes)  # recently added nodes
        # create a list of the movies whose parents should be checked on the next round. This should be all
        # unwatched movies.
        current_level_nodes = list(set(recently_added_nodes) - set(watched)) + children_duplicates
        # make discarded nodes = all the nodes that have been discarded that weren't put back in
        discarded_nodes = (list((set(discarded_nodes) | set(recently_discarded_nodes)) - set(total_nodes)))
        # Check if any of the discarded movies are a parent of a movie we watched. If so, create a custom movie with
        # those movies as parents, and add that custom movie to the next round of parent lookups
        # (but don't add it into anything permanent). This allows us to include less recent parents of our selected
        # movies without including any other parents of watched movies.
        if len(discarded_nodes) > 0:
            recently_added_watched = set(watched) & set(recently_added_nodes)  # intersection
            for movie in recently_added_watched:
                temp_movie = Movie("Temp Movie")
                for prev in movie.prevs:
                    if prev[0] in discarded_nodes:
                        temp_movie.prevs.append(prev)
                if len(temp_movie.prevs) > 0:
                    current_level_nodes.append(temp_movie)
            # if we traversed the whole tree and somehow missed some nodes, put those nodes back in.
            if len(current_level_nodes) == 0:
                temp_movie = Movie("Temp Movie")
                for discard in discarded_nodes:
                    temp_movie.prevs.append((discard, 0))
                current_level_nodes.append(temp_movie)
                discarded_nodes.clear()
        nodes.clear()
        # nodes now equals every node that has been looked at that wasn't watched
        nodes.extend(list(set(total_nodes) - set(watched)))
        if COUNT_RULE == "Whatever It Takes" and RULE == "Relevant":  # breaks out of loop after first tier
            break
    # set children to the nodes minus the "recently added" nodes
    # children = list(set(nodes) - set(recently_added_nodes))
    # number left to check will be how many they wanted minus how many we already have
    return requested_watchlist_count - len(children)


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


# returns the most recent ancestors of a list of movies. If RULE == Most Recent,
# trims off any ancestors of other ancestors and returns them in discarded_predecessors.
def next_tier(movies):
    # step 1: find all nodes which are immediately relevant
    direct_predecessors = []
    discarded_predecessors = []
    for movie in movies:
        for prev in movie.prevs:
            if prev[0] not in direct_predecessors and prev[1] > 4:
                direct_predecessors.append(prev[0])
    if RULE == "Recent":
        # step 2: generate family tree to discover if there will be missing pieces
        nodes = movies.copy()
        prev_tree(nodes, [])
        nodes = list(set(nodes) - set(movies))
        for film in nodes:
            for prev in film.prevs:
                if prev[0] in direct_predecessors and prev[1] > 4:
                    direct_predecessors.remove(prev[0])
                    if prev[0] not in discarded_predecessors:
                        discarded_predecessors.append(prev[0])
    return direct_predecessors, discarded_predecessors


# Movies have names, series, and lists of previous (and potentially next) films.
class Movie:
    def __init__(self, name, series=""):
        self.prevs = []  # the parents of this movie
        self.seqs = []  # the children of this movie (unused field)
        self.name = name  # the name of the movie
        self.series = series  # the film series this movie belongs to