""" Creates a GUI which allows user to specify which films they have seen and which films they
would like to see, and gives them recommendations as to which movies they should watch in between.
"""
from MarvelTracker import Movie
from graphics import *
import csv

RULE = "Recent"
MOVIES = {}
WIDTH = 1200
HEIGHT = 600
GRAPHS_CHECKED = 0
NUM_CHOSEN = 0
HOVER_COLOR = color_rgb(76, 237, 78)
SELECTED_COLOR = color_rgb(31, 222, 34)
CHOSEN_COLOR = color_rgb(18, 173, 206)
WATCHED_COLOR = color_rgb(83, 116, 81)
CHILDREN_COLOR = color_rgb(206, 191, 18)
BUTTON_COLOR = color_rgb(210, 222, 31)
INSTRUCTION_TEXT = None
CHILDREN = []
WATCHED = []
CHANGED = False
NUM_TIES = 0
NEXT_TEXT = None
REC_TEXT = None
BUTTONS = {}

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


# this version considers every option, but is slow.
# returns a list containing every graph which tied for first place
def brute_force_subgraph_helper(excluded, included, n):
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
        best_graph_next_level += brute_force_subgraph_helper(excluded_copy, included_copy, n-1)
        weight = subgraph_weight(best_graph_next_level[0])
        if weight > max_weight:
            max_weight = weight
            best_graphs = best_graph_next_level.copy()
        elif weight == max_weight:
            best_graphs += best_graph_next_level
        #excluded_copy.append(movie)
        included_copy.remove(movie)
    #print(str(max_weight))
    return best_graphs


def tie_breaker(best_graphs, excluded):
    if len(best_graphs) == 1:
        return best_graphs[0]
    else:
        print("number of equally good choices: " + str(len(best_graphs)))
        best_graph = None
        max_weight = 0
        # find best of bests
        for graph in best_graphs:
            # create new list of excluded movies
            excluded_copy = excluded.copy()
            for movie in graph:
                if movie in excluded:
                    excluded_copy.remove(movie)
            best_plus_one = tie_breaker(brute_force_subgraph_helper(excluded_copy, graph, 1), excluded)
            weight = subgraph_weight(best_plus_one)
            if weight > max_weight:
                max_weight = weight
                best_graph = graph
        # choose the subgraph of highest weight
        return best_graph


# find the n best other movies to watch if you've watched the watched and want to watch the children
def find_best_subgraph(watched, children, num_extras):
    nodes = children.copy()
    children_copy = children.copy()
    num_to_check = num_extras
    if RULE == "Recent":
        num_to_check = most_recent_prev_tree(nodes, watched, children_copy, num_extras)
    else:
        prev_tree(nodes, watched)
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
    best_graphs = brute_force_subgraph_helper(excluded, included, num_to_check)
    return tie_breaker(best_graphs, excluded)


# NOTE: THIS FUNCTION MODIFIES NODES
# generates subgraph containing all ancestors of every node in nodes
def prev_tree(nodes, watched):
    for movie in nodes:
        for prev in movie.prevs:
            if (prev[1] > 1 or RULE == "Recent") and prev[0] not in watched and prev[0] not in nodes:
                nodes.append(prev[0])
                prev_tree(nodes, watched)


# NOTE: THIS FUNCTION MODIFIES NODES AND CHILDREN
# generates a limited ancestor tree, containing only more recent ancestors
# ancestors are broken up into generations. if multiple generations are included,
# all ancestors from every generation will be included except for some ancestors from
# the furthest back generation.
def most_recent_prev_tree(nodes, watched, children, n):
    total_nodes = nodes.copy()
    original_children_count = len(children)
    current_level_nodes = nodes.copy()  # the list of nodes whose parents we are currently finding
    recently_added_nodes = []  # keeps track of movies currently being added to the list
    children_duplicates = []  # handles situation where a tier contains one of the other movies they wanted to watch
    while len(nodes) - original_children_count < n and len(current_level_nodes) > 0:
        children.extend(list(set(recently_added_nodes) - set(watched)))
        recently_added_nodes = []
        prev_nodes = most_recent_tier(current_level_nodes)
        for prev in prev_nodes:
            if prev not in recently_added_nodes and prev not in total_nodes:
                recently_added_nodes.append(prev)
            elif prev in children:
                children_duplicates.append(prev)
        total_nodes.extend(recently_added_nodes)
        current_level_nodes = recently_added_nodes + children_duplicates
        nodes.clear()
        nodes.extend(list(set(total_nodes) - set(watched)))
    return n - (len(children) - original_children_count)


# computes and returns the weight of the subgraph
def subgraph_weight(subgraph):
    weight = 0
    for movie in subgraph:
        for prev in movie.prevs:
            if prev[0] in subgraph:
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
def most_recent_tier(movies):
    # step 1: find all nodes which are immediately relevant
    direct_predecessors = []
    for movie in movies:
        direct_predecessors.extend(prev[0] for prev in movie.prevs if prev[0] not in direct_predecessors)
    # step 2: generate family tree to discover if there will be missing pieces
    nodes = movies.copy()
    prev_tree(nodes, [])
    nodes = list(set(nodes) - set(movies))
    for film in nodes:
        for prev in film.prevs:
            if prev[0] in direct_predecessors:
                direct_predecessors.remove(prev[0])
    return direct_predecessors


# draws the window
def draw_window():
    # sort each movie by series
    series = {}
    for movie in MOVIES.values():
        if movie.series not in series:
            series[movie.series] = [movie]
        else:
            series[movie.series].append(movie)

    x_pos = 3
    # set position of each movie
    for movie_series in series:
        y_pos = 5
        for movie in series[movie_series]:
            point = Point(x_pos, y_pos)
            movie.set_point(point, height=8, width=14.5)
            y_pos = y_pos + 8*1.5
        x_pos = x_pos + 14.5*1.1
    '''x_pos = 5
    y_pos = 5
    # set position of each movie
    for movie in MOVIES.values():
        point = Point(x_pos, y_pos)
        movie.set_point(point, height=8, width=14)
        x_pos = x_pos + 10 * 1.5
        if x_pos > 160:
            y_pos = y_pos + 8 * 1.5
            x_pos = 5'''

    # draw window
    win = GraphWin(title="Most Interconnected MCU Watchlist", width=WIDTH, height=HEIGHT, autoflush=False)
    win.setCoords(0, 180*HEIGHT/WIDTH, 180, 0)
    win.bind('<Motion>', motion)
    for movie in MOVIES.values():
        movie.draw(win)

    next_button = Rectangle(Point(80, 60), Point(90, 65))
    next_button.setFill(BUTTON_COLOR)
    next_text = Text(next_button.getCenter(), text="Next")
    next_button.draw(win)

    BUTTONS["Next"] = {"Button": next_button, "Text": next_text}
    next_text.draw(win)

    prev_button = Rectangle(Point(60, 60), Point(70, 65))
    prev_button.setFill(BUTTON_COLOR)
    prev_text = Text(prev_button.getCenter(), text="Back")
    BUTTONS["Previous"] = {"Button": prev_button, "Text": prev_text}

    global INSTRUCTION_TEXT
    INSTRUCTION_TEXT = Text(Point(50, 70), text="Select the movies you have already seen.")
    INSTRUCTION_TEXT.setSize(20)
    INSTRUCTION_TEXT.draw(win)
    global REC_TEXT
    REC_TEXT = Text(Point(160, 50), text="")
    update()
    return win


# runs the main program
def run_program(win):
    global GRAPHS_CHECKED
    global NUM_TIES
    global REC_TEXT
    global CHANGED
    global CHILDREN
    level = 1
    watched = []
    selected = watched
    #children = []
    subgraph = []
    input_box = Entry(Point(INSTRUCTION_TEXT.getAnchor().getX() + 50, INSTRUCTION_TEXT.getAnchor().getY()), 10)
    input_box.setFill("white")
    input_box.setText("1")
    while (win.isOpen()):
        try:
            p = win.getMouse()
        except:
            break
        # Next Button
        if 80 < p.getX() < 90 and 60 < p.getY() < 65:
            # stage 1-> stage 2
            if level == 1:
                level = 2
                selected = CHILDREN
                for movie in watched:
                    Movie.open.remove(movie)
                    movie.my_square.setFill("gray")
                for movie in CHILDREN:
                    movie.my_square.setFill(SELECTED_COLOR)
                    movie.selected = True
                INSTRUCTION_TEXT.setText("Select the movies you would like to see.")
                if BUTTONS["Previous"]["Text"].getText() == "Reset":
                    BUTTONS["Previous"]["Text"].setText("Back")
                else:
                    BUTTONS["Previous"]["Button"].draw(win) #draw the back button
                    BUTTONS["Previous"]["Text"].draw(win)
            # stage 2-> stage 3
            elif level == 2:
                if len(CHILDREN) == 0:
                    INSTRUCTION_TEXT.setText("You must select at least 1 movie you would like to see.")
                else:
                    level = 3
                    Movie.open.clear()
                    for movie in CHILDREN:
                        movie.my_square.setFill(CHILDREN_COLOR)
                    INSTRUCTION_TEXT.setText("How many additional movies are you willing to watch?")
                    input_box.draw(win)
            #stage 3->stage 4
            elif level == 3:
                global NUM_CHOSEN
                if not str.isdigit(input_box.getText()):
                    input_box.setText("")
                    INSTRUCTION_TEXT.setText("How many additional movies are you willing to watch?\nOnly numbers are allowed.")
                else:
                    level = 4
                    if CHANGED or not NUM_CHOSEN == int(input_box.getText()):
                        CHANGED = False
                        NUM_CHOSEN = int(input_box.getText())
                        subgraph = find_best_subgraph(watched, CHILDREN, NUM_CHOSEN)
                        order = watch_order(watched, subgraph)
                        #watched_string = "Already Watched:\n" + "\n".join(t.name for t in watched)
                        rec_string = "\nRecommended Watchlist:\n" + "\n\n".join(order)
                        REC_TEXT.setText(rec_string)
                        REC_TEXT.undraw()
                        REC_TEXT.draw(win)
                    for movie in MOVIES.values():
                        if movie not in watched and movie not in CHILDREN:
                            if movie in subgraph:
                                movie.my_square.setFill(CHOSEN_COLOR)
                            else:
                                movie.my_square.setFill("white")
                    input_box.undraw()
                    INSTRUCTION_TEXT.setText("Here are your recommendations!")
                    print("graphs checked: " + str(GRAPHS_CHECKED))

                    BUTTONS["Next"]["Button"].undraw()
                    BUTTONS["Next"]["Text"].undraw()
                    #NEXT_TEXT.setText("Reset")
        #back button
        if 60 < p.getX() < 70 and 60 < p.getY() < 65:
            # stage 4-->stage 3
            if level == 4:
                level = 3
                GRAPHS_CHECKED = 0
                INSTRUCTION_TEXT.setText("How many additional movies are you willing to watch?")
                BUTTONS["Next"]["Button"].draw(win)
                BUTTONS["Next"]["Text"].draw(win)
                input_box.draw(win)
            # stage 3--> stage 2
            elif level == 3:
                level = 2
                INSTRUCTION_TEXT.setText("Select the movies you would like to see.")
                input_box.undraw()
                selected = CHILDREN
                for movie in MOVIES.values():
                    if movie not in watched:
                        Movie.open.append(movie)
                        if movie not in CHILDREN:
                            movie.my_square.setFill("white")
                        else:
                            movie.my_square.setFill(SELECTED_COLOR)
            # stage 2--> stage 1 (disallowing repetition)
            elif level == 2:
                level = 1
                INSTRUCTION_TEXT.setText("Select the movies you have already seen.")
                selected = watched
                for movie in MOVIES.values():
                    if movie not in Movie.open:
                        Movie.open.append(movie)
                    if movie in watched:
                        movie.selected = True
                        movie.my_square.setFill(SELECTED_COLOR)
                    else:
                        movie.selected = False
                        if movie in CHILDREN:
                            movie.my_square.setFill(CHILDREN_COLOR)
                if len(CHILDREN) > 0 or len(watched) > 0:
                    BUTTONS["Previous"]["Text"].setText("Reset")
                else:
                    BUTTONS["Previous"]["Button"].undraw() #undraw the back button
                    BUTTONS["Previous"]["Text"].undraw()
            # reset button
            elif level == 1:
                watched.clear()
                CHILDREN.clear()
                for movie in MOVIES.values():
                    movie.selected = False
                    movie.my_square.setFill("white")
                REC_TEXT.undraw()
                BUTTONS["Previous"]["Button"].undraw()  # undraw the back button
                BUTTONS["Previous"]["Text"].undraw()
                BUTTONS["Previous"]["Text"].setText("Back")
        for movie in Movie.open:
            if movie.p1.getX() < p.getX() < movie.p2.getX() and movie.p1.getY() < p.getY() < movie.p2.getY():
                CHANGED = True
                if not movie.selected:
                    if movie in CHILDREN:
                        CHILDREN.remove(movie)
                    selected.append(movie)
                    movie.selected = True
                    movie.my_square.setFill(SELECTED_COLOR)
                else:
                    movie.my_square.setFill(HOVER_COLOR)
                    selected.remove(movie)
                    movie.selected = False


# tracks motion
def motion(event):
    global CHILDREN
    x = 180*event.x/WIDTH
    y = 180*event.y/WIDTH
    # if we hover over an open movie, show which movies will be unlocked if we watch this movie.
    for movie in Movie.open:
        if movie.p1.getX() < x < movie.p2.getX() and movie.p1.getY() < y < movie.p2.getY():
            movie.my_square.setFill(HOVER_COLOR)
        # if we are not hovering over this movie, reset the colors back to normal
        else:
            if movie.selected:
                movie.my_square.setFill(SELECTED_COLOR)
            elif movie in CHILDREN:
                movie.my_square.setFill(CHILDREN_COLOR)
            else:
                movie.my_square.setFill("white")
    for button in BUTTONS.values():
        button = button["Button"]
        if button.p1.getX() < x < button.p2.getX() and button.p1.getY() < y < button.p2.getY():
            button.setFill(HOVER_COLOR)
        # if we are not hovering over this movie, reset the colors back to normal
        else:
            button.setFill(BUTTON_COLOR)


if __name__ == '__main__':
    import_weighted_from_csv()
    win = draw_window()
    run_program(win)
