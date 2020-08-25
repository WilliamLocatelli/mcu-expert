""" Main code for the recommendation algorithm.
"""
#from ProcessData.MarvelTracker import Movie
import csv

RULE = "Relevant"
COUNT_RULE = "Count"
CURRENT_ANCESTOR_TIER = 0
MOVIES = {}
GRAPHS_CHECKED = 0
NUM_TIES = 0


# takes in a CSV file, sets global variables for movies
def import_weighted_from_csv(file="ProcessData/MCUphase1to3-weighted.csv"):
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


def import_data_from_csv(file="ProcessData/data.csv"):
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


def tie_breaker(best_graphs, excluded, children, parents):
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


# for use by web app Launch Script
def get_objects_and_find_best_subgraph(watched, children, num_extras, rule, count_rule):
    global COUNT_RULE
    COUNT_RULE = count_rule
    if COUNT_RULE == "Whatever It Takes":
        num_extras = len(MOVIES)
    watched_movies = []
    child_movies = []
    for movie in watched:
        if movie in MOVIES.keys():
            watched_movies.append(MOVIES[movie])
    for movie in children:
        if movie in MOVIES.keys():
            child_movies.append(MOVIES[movie])
    result = find_best_subgraph(watched_movies, child_movies, num_extras, rule)
    return watch_order(watched_movies, result)


# find the n best other movies to watch if you've watched the watched and want to watch the children
def find_best_subgraph(watched, children, num_extras, rule):
    global RULE
    RULE = rule
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
    result = tie_breaker(best_graphs, excluded, children_copy, watched)
    # print("graphs checked: " + str(GRAPHS_CHECKED))
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
    discarded_nodes = []  # used only for Most Recent heuristic
    while len(nodes) - original_children_count < n and (len(current_level_nodes) > 0 or len(discarded_nodes) > 0):
        CURRENT_ANCESTOR_TIER = CURRENT_ANCESTOR_TIER + 1
        children_duplicates.clear()
        # ONLY add stuff to children if this isn't the final tier
        children.extend(list(set(recently_added_nodes) - set(watched)))
        prev_nodes, recently_discarded_nodes = next_tier(current_level_nodes)
        recently_added_nodes = []
        for prev in prev_nodes:
            if prev not in recently_added_nodes and prev not in total_nodes:
                recently_added_nodes.append(prev)
            elif prev in children:
                children_duplicates.append(prev)
        total_nodes.extend(recently_added_nodes)  # recently added nodes
        current_level_nodes = list(set(recently_added_nodes) - set(watched)) + children_duplicates
        # make discarded nodes = all the nodes that have been discarded that weren't put back in
        discarded_nodes.extend(list(set(recently_discarded_nodes) - set(discarded_nodes) - set(total_nodes)))
        discarded_nodes = list(set(discarded_nodes) - set(total_nodes))
        recently_added_watched = set(watched).intersection(set(recently_added_nodes))
        # Check if any of the discarded movies are a parent of a movie we watched. If so, create a custom movie with
        # those movies as parents, and add that custom movie to the next round of parent lookups
        # (but don't add it into anything permanent).
        for movie in recently_added_watched:
            temp_movie = Movie("Temp Movie")
            for prev in movie.prevs:
                if prev[0] in discarded_nodes:
                    temp_movie.prevs.append(prev)
            if len(temp_movie.prevs) > 0:
                current_level_nodes.append(temp_movie)
        # if we traversed the whole tree and somehow missed some nodes, put those nodes back in. (is this possible?)
        if len(current_level_nodes) == 0 and len(discarded_nodes) > 0:
            temp_movie = Movie("Temp Movie")
            for discard in discarded_nodes:
                temp_movie.prevs.append((discard, 0))
            current_level_nodes.append(temp_movie)
            discarded_nodes.clear()
        # current_level_nodes = recently_added_nodes + children_duplicates
        nodes.clear()
        # nodes now equals every node that has been looked at that wasn't watched
        nodes.extend(list(set(total_nodes) - set(watched)))
        if COUNT_RULE == "Whatever It Takes":  # breaks out of loop after first tier
            break
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
    discarded_predecessors = []
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
                    if prev[0] not in discarded_predecessors:
                        discarded_predecessors.append(prev[0])
    return direct_predecessors, discarded_predecessors

# COPIED FROM MARVELTRACKER
# create a class for movies. each movie will be at a certain point and have a name. clicking on the movie will make it
# do stuff.
class Movie:
    first = None
    open = []
    selected = []
    # if this is the main program, create the window
    if __name__ == '__main__':
        win = GraphWin(width=500, height=700, title="MCU Tracker", autoflush=False)
        win.setCoords(0, 0, 100, 140)

    def __init__(self, name, rank1=0, rank2=0, rank3=0, series=""):
        self.selected = False  # whether or not this movie has been marked as watched
        self.prevs = []  # the parents of this movie
        self.seqs = []  # the children of this movie
        self.p1 = None
        self.p2 = None
        self.my_square = None
        self.name = name  # the name of the movie
        self.prevs_selected = False  # whether or not all of this movies parents have been marked as watched
        self.rank = [rank1, rank2, rank3]
        self.series = series
