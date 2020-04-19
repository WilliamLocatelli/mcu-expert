""" Main code for the recommendation algorithm.
"""
from MarvelTracker import Movie
import csv

RULE = "Recent"
CURRENT_ANCESTOR_TIER = 0
MOVIES = {}
GRAPHS_CHECKED = 0
NUM_TIES = 0


# takes in a CSV file, sets global variables for movies
def import_weighted_from_csv(file="MCUphase1to3-weighted.csv"):
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
        this_movie.prevs_selected = True
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


def import_data_from_csv(file="data.csv"):
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


# this version considers every option, but is slow.
# returns a list containing every graph which tied for first place
def brute_force_subgraph_helper(excluded, included, n, children):
    global GRAPHS_CHECKED
    best_graphs = []
    if n == 0:
        GRAPHS_CHECKED += 1
        subgraph = included.copy()
        return [subgraph]
    max_weight = 0
    #best_graph = included
    excluded_copy = excluded.copy()
    included_copy = included.copy()
    while len(excluded_copy) > n-1:
        movie = excluded_copy[0]
        included_copy.append(movie)
        excluded_copy.remove(movie)
        best_graph_next_level = []
        best_graph_next_level += brute_force_subgraph_helper(excluded_copy, included_copy, n-1, children)
        if RULE == "Relevant" and CURRENT_ANCESTOR_TIER < 2:
            weight = subgraph_weight(list(set(best_graph_next_level[0]) - set(children)), children)
        else:
            weight = subgraph_weight(best_graph_next_level[0], best_graph_next_level[0])
        if weight > max_weight:
            max_weight = weight
            best_graphs = best_graph_next_level.copy()
        elif weight == max_weight:
            best_graphs += best_graph_next_level
        #excluded_copy.append(movie)
        included_copy.remove(movie)
    #print(str(max_weight))
    return best_graphs


def tie_breaker(best_graphs, excluded, children):
    if len(best_graphs) == 1:
        return best_graphs[0]
    else:
        '''print("\nnumber of equally good choices: " + str(len(best_graphs)))
        print("the options are:")
        for graph in best_graphs:
            print(",".join(movie.name for movie in graph))'''
        best_graph = None
        max_score = 0
        '''max_weight = 0
        # find best of bests
        for graph in best_graphs:
            # create new list of excluded movies
            excluded_copy = excluded.copy()
            for movie in graph:
                if movie in excluded:
                    excluded_copy.remove(movie)
            best_plus_one = tie_breaker(brute_force_subgraph_helper(excluded_copy, graph, 1, children), excluded, children)
            weight = subgraph_weight(best_plus_one, best_plus_one)
            if weight > max_weight:
                max_weight = weight
                best_graph = graph
        # choose the subgraph of highest weight'''
        best_graphs_2 = []
        for graph in best_graphs:
            score = sum(int(movie.rt_score) for movie in graph)
            if score > max_score:
                best_graphs_2 = [graph]
                best_graph = graph
                max_score = score
            elif score == max_score:
                best_graphs_2.append(graph)
        if len(best_graphs_2) > 1:
            max_score = 0
            for graph in best_graphs_2:
                score = 0
                for movie in graph:
                    movie_score = sum(int(prev[1]) for prev in movie.prevs)
                    score += movie_score
                if score > max_score:
                    best_graph = graph
                    max_score = score
                elif score == max_score:
                    print("not rigorous enough")
        return best_graph


# find the n best other movies to watch if you've watched the watched and want to watch the children
def find_best_subgraph(watched, children, num_extras):
    global GRAPHS_CHECKED
    global CURRENT_ANCESTOR_TIER
    nodes = children.copy()
    children_copy = children.copy()
    num_to_check = num_extras
    if RULE == "Interconnected":
        prev_tree(nodes, watched)
    else:
        num_to_check = limited_prev_tree(nodes, watched, children_copy, num_extras)
    for parent in watched:
        nodes.append(parent)
    included = watched + children_copy
    most_nodes = len(nodes) - len(children) - len(watched)
    excluded = []
    if most_nodes <= num_extras:  # if most_nodes is less than n, include all watched plus n
        return nodes
    else:
        for movie in nodes:
            if movie not in included:
                excluded.append(movie)
    best_graphs = brute_force_subgraph_helper(excluded, included, num_to_check, children_copy)
    result = tie_breaker(best_graphs, excluded, children_copy)
    print("graphs checked: " + str(GRAPHS_CHECKED))
    return result


# NOTE: THIS FUNCTION MODIFIES THE LIST NODES
# generates subgraph containing all ancestors of every node in nodes
def prev_tree(nodes, watched):
    for movie in nodes:
        for prev in movie.prevs:
            if prev[1] > 1 and prev[0] not in watched and prev[0] not in nodes:
                nodes.append(prev[0])
                prev_tree(nodes, watched)


# NOTE: THIS FUNCTION MODIFIES THE LISTS NODES AND CHILDREN
# generates a limited ancestor tree, containing only more recent ancestors
# ancestors are broken up into generations. if multiple generations are included,
# all ancestors from every generation will be included except for some ancestors from
# the furthest back generation.
def limited_prev_tree(nodes, watched, children, n):
    global CURRENT_ANCESTOR_TIER
    total_nodes = nodes.copy()
    original_children_count = len(children)
    current_level_nodes = nodes.copy()  # the list of nodes whose parents we are currently finding
    recently_added_nodes = []  # keeps track of movies currently being added to the list
    children_duplicates = []  # handles situation where a tier contains one of the other movies they wanted to watch
    while len(nodes) - original_children_count < n and len(current_level_nodes) > 0:
        CURRENT_ANCESTOR_TIER = CURRENT_ANCESTOR_TIER + 1
        children_duplicates.clear()
        children.extend(list(set(recently_added_nodes) - set(watched)))
        recently_added_nodes = []
        prev_nodes = next_tier(current_level_nodes)
        for prev in prev_nodes:
            if prev not in recently_added_nodes and prev not in total_nodes:
                recently_added_nodes.append(prev)
            elif prev in children:
                children_duplicates.append(prev)
        total_nodes.extend(recently_added_nodes)
        current_level_nodes = recently_added_nodes + children_duplicates
        nodes.clear()
        nodes.extend(list(set(total_nodes) - set(watched)))
    return n - (len(children) - original_children_count)  # number left to check will be n minus how many we've added


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


# generates a watch order, excluding movies which have already been watched
def watch_order(watched, subgraph):
    order = []
    for movie in MOVIES:
        if MOVIES[movie] in subgraph and not MOVIES[movie] in watched:
            order.append(movie)
    return order


# returns the most recent ancestors of a movie
def next_tier(movies):
    # step 1: find all nodes which are immediately relevant
    direct_predecessors = []
    for movie in movies:
        for prev in movie.prevs:
            if prev[0] not in direct_predecessors and prev[1] > 1:
                direct_predecessors.append(prev[0])
    if RULE == "Recent":
        # step 2: generate family tree to discover if there will be missing pieces
        nodes = movies.copy()
        prev_tree(nodes, [])
        nodes = list(set(nodes) - set(movies))
        for film in nodes:
            for prev in film.prevs:
                if prev[0] in direct_predecessors and prev[1] > 1:
                    direct_predecessors.remove(prev[0])
    return direct_predecessors
