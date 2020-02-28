""" Creates a GUI in which users can walk through an interactive
MCU watch-through, following strict rules with regards to when you
are allowed to watch certain movies.
"""

from graphics import *
import csv

root = []

BEST_COLOR = color_rgb(163, 216, 241)
HOVER_COLOR = color_rgb(76, 237, 78)
SELECTED_COLOR = color_rgb(31, 222, 34)
PROHIBIT_SELECTED_COLOR = color_rgb(156, 194, 147)
PROHIBIT_OPEN_COLOR = color_rgb(196, 196, 196)
DESELECT_COLOR = color_rgb(76, 237, 78)
POTENTIAL_COLOR = color_rgb(234, 234, 234)
RECT_HEIGHT = 7
RECT_WIDTH = 20
BIG_X = 0
BIG_Y = 0

# handles hover response
def motion(event):
    global BIG_X, BIG_Y
    BIG_X, BIG_Y = event.x, event.y
    # if we hover over an open movie, show which movies will be unlocked if we watch this movie.
    for movie in Movie.open:
        potentials = movie.seqs
        # if we are hovering over this movie, show which movies will be unlocked
        if movie.p1.getX() < BIG_X/5 < movie.p2.getX() and movie.p1.getY() < 140 - (BIG_Y/5) < movie.p2.getY():
            movie.my_square.setFill(HOVER_COLOR)
            parents_selected = 0
            for seq in potentials:
                for prev in seq.prevs:
                    if prev.selected:
                        parents_selected += 1
                if parents_selected >= len(seq.prevs) - 1:
                    seq.my_square.setFill(POTENTIAL_COLOR)
            break
        # if we are not hovering over this movie, reset the colors back to normal
        else:
            for seq in potentials:
                seq.my_square.setFill("gray")
            if movie is Movie.first:
                movie.my_square.setFill(BEST_COLOR)
            else:
                movie.my_square.setFill("white")
    # if we hovered over a selected movie, change color of it and its children to indicate consequence of deselecting
    for movie in Movie.selected:
        if movie.p1.getX() < BIG_X/5 < movie.p2.getX() and movie.p1.getY() < 140 - (BIG_Y/5) < movie.p2.getY():
            movie.my_square.setFill(DESELECT_COLOR)
            prohibit_children(movie)
            break
        else:
            movie.my_square.setFill(SELECTED_COLOR)
    #print('{}, {}'.format(BIG_X, BIG_Y))


# when we hover over a selected movie, call this to recursively indicate the movies which will be deselected if we
# deselect this one.
def prohibit_children(movie):
    for seq in movie.seqs:
        if seq.prevs_selected:
            if seq in Movie.selected:
                seq.my_square.setFill(PROHIBIT_SELECTED_COLOR)
            else:
                seq.my_square.setFill(PROHIBIT_OPEN_COLOR)
            prohibit_children(seq)


#import the graph from a csv file
def import_movies_from_csv(file="AdjacencyList.csv"):
    # put all the rows of the csv file into a list
    movies_list = []
    with open(file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            movies_list.append(row)
    result = {}
    # initial position
    layer = 0
    # iterate through the list of movies, creating an object for each
    for movie in movies_list:
        this_movie = Movie(movie[3], int(movie[0]), int(movie[1]), int(movie[2]))
        result[movie[3]] = this_movie  # add the movie to a dictionary with the name as the key
        # generate adjacency list of previous movies
        prevs = []
        # keep track of layers
        previous_layer = []
        for prev in movie:
            if not prev == movie[0] and not prev == movie[1] and not prev == movie[2] and not prev == movie[3] and len(prev) > 1:
                prevs.append(result.get(prev))
                previous_layer.append(result.get(prev).layer)
        this_movie.prevs = prevs
        # increment the layers if necessary
        if len(previous_layer) > 0 and layer <= max(previous_layer):
            layer = layer + 1
        this_movie.layer = layer
    # generate adjacency lists of seqs
    for movie in result.values():
        if len(movie.prevs) > 0:
            for prev in movie.prevs:
                prev.seqs.append(movie)
        else:
            movie.prevs_selected = True
    # give each movie a coordinate
    handle_positions(result)
    return result


# set screen positions for movies, based on layers
def handle_positions(movies):
    layers = {}
    for movie in movies.values():
        if layers.__contains__(movie.layer):
            layers[movie.layer].append(movie)
        else:
            layers[movie.layer] = [movie]
    y = 130
    for layer in layers.values():
        size = len(layer)
        pos = 100 / (size + 1)
        x = pos
        for movie in layer:
            movie.set_point(Point(x - RECT_WIDTH/2, y))
            x = x + pos
        y = y - 1.5*RECT_HEIGHT


# draw the window for the movies, and respond to user clicks.
def make_window(movies):
    Movie.win.bind('<Motion>', motion)
    #draw movies
    for movie in movies.values():
        movie.draw()
        # draw lines connecting movies
        '''if len(movie.prevs) > 0:
            for prev in movie.prevs:
                line = Line(movie.p2, prev.p1)
                line.draw(Movie.win)'''
    color_best_movie(movies)
    update()
    # respond to clicks
    while True:
        p = Movie.win.getMouse()
        for movie in movies.values():
            if movie.p1.getX() < p.getX() < movie.p2.getX() and movie.p1.getY() < p.getY() < movie.p2.getY():
                if movie.prevs_selected is True:  # proceed only if the prevs of this movie have been selected
                    if movie.selected is False:
                        select_movie(movie)
                        color_best_movie(movies)
                    else:
                        movie.my_square.setFill(HOVER_COLOR)
                        Movie.selected.remove(movie)
                        movie.selected = False
                        clear_nexts(movie)
                        Movie.open.append(movie)
                        color_best_movie(movies)
                #else, do something special.


# update rank list swapping to be generalizable
def color_best_movie(movies):
    global PRIORITY_LIST
    max_rank = len(movies)
    max_movie = None
    for open_movie in Movie.open:
        open_movie.my_square.setFill("white")
        if not movies.get("The Avengers").selected:
            r = open_movie.rank[0]
        elif not movies.get("Avengers: Age of Ultron").selected:
            r = open_movie.rank[1]
        else:
            r = open_movie.rank[2]
        if r <= max_rank:
            max_rank = r
            max_movie = open_movie
        open_movie.my_square.setWidth(1)
    if max_movie:
        Movie.first = max_movie
        max_movie.my_square.setFill(BEST_COLOR)
        max_movie.my_square.setWidth(3)


# recursively marks all of the passed movie's children as unwatchable
def clear_nexts(movie):
    for seq in movie.seqs:
        if seq in Movie.open: Movie.open.remove(seq)
        if seq in Movie.selected: Movie.selected.remove(seq)
        seq.selected = False
        seq.prevs_selected = False
        seq.my_square.setFill("gray")
        seq.my_square.setWidth(1)
        clear_nexts(seq)


# marks a movie as watched and updates its children as watchable, if permissible
def select_movie(movie):
    movie.my_square.setWidth(1)
    Movie.open.remove(movie)
    Movie.selected.append(movie)
    movie.selected = True
    movie.my_square.setFill(SELECTED_COLOR)
    for seq in movie.seqs:
        prevs_selected = True
        for prev in seq.prevs:
            if not prev.selected:
                prevs_selected = False
        if prevs_selected:
            seq.prevs_selected = True
            Movie.open.append(seq)
            seq.my_square.setFill("white")
        else:
            seq.my_square.setFill("gray")


# create a class for movies. each movie will be at a certain point and have a name. clicking on the movie will make it
# do stuff.
class Movie:
    first = None
    open = []
    selected = []
    win = GraphWin(width=500, height=700, title="MCU Tracker", autoflush=False)
    win.setCoords(0, 0, 100, 140)

    def __init__(self, name, rank1=0, rank2=0, rank3=0):
        self.selected = False  # whether or not this movie has been marked as watched
        self.prevs = []  # the parents of this movie
        self.seqs = []  # the children of this movie
        self.p1 = None
        self.p2 = None
        self.my_square = None
        self.name = name  # the name of the movie
        self.prevs_selected = False  # whether or not all of this movies parents have been marked as watched
        self.rank = [rank1, rank2, rank3]

    def draw(self):
        self.my_square.draw(self.win)  # draw it to the window
        if not self.prevs_selected:
            self.my_square.setFill("gray")
        else:
            Movie.open.append(self)
        # work back from character 16 to find the last space before character 16
        if len(self.name) > 16:
            n = 16
            k = self.name[n]
            while not k == " ":
                n -= 1
                k = self.name[n]
            self.name = self.name[:n] + "\n" + self.name[n:]
        title = Text(self.my_square.getCenter(), self.name)
        title.draw(self.win)

    def set_point(self, point):
        self.p1 = Point(point.getX(), point.getY())
        self.p2 = Point(point.getX() + RECT_WIDTH, point.getY() + RECT_HEIGHT)
        self.my_square = Rectangle(self.p1, self.p2)


if __name__ == '__main__':
    all_movies = import_movies_from_csv()
    make_window(all_movies)
