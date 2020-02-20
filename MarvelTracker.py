from graphics import *
import csv

root = []

SQUARE_SIZE = 5


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
        this_movie = Movie(movie[0])
        result[movie[0]] = this_movie  # add the movie to a dictionary with the name as the key
        # generate adjacency list of previous movies
        prevs = []
        # keep track of layers
        previous_layer = []
        for prev in movie:
            if not prev == movie[0] and len(prev) > 1:
                prevs.append(result.get(prev))
                previous_layer.append(result.get(prev).layer)
        this_movie.prevs = prevs
        # increment the layers if necessary
        if len(previous_layer) > 0 and layer <= max(previous_layer):
            layer = layer + 1
        this_movie.layer = layer
    # add nexts
    for movie in result.values():
        if len(movie.prevs) > 0:
            for prev in movie.prevs:
                prev.seqs.append(movie)
        else:
            movie.prevs_selected = True
    # give each movie a coordinate
    handle_positions(result)
    return result


def handle_positions(movies):
    layers = {}
    for movie in movies.values():
        if layers.__contains__(movie.layer):
            layers[movie.layer].append(movie)
        else:
            layers[movie.layer] = [movie]
    y = 150
    for layer in layers.values():
        size = len(layer)
        pos = 100 / (size + 1)
        x = pos
        for movie in layer:
            movie.set_point(Point(x - SQUARE_SIZE/2, y))
            x = x + pos
        y = y - 10


# test
def make_window(movies):
    for movie in movies.values():
        movie.draw()
        # draw lines connecting movies
        '''if len(movie.prevs) > 0:
            for prev in movie.prevs:
                line = Line(movie.p2, prev.p1)
                line.draw(Movie.win)'''
    update()
    while True:
        p = Movie.win.getMouse()
        for movie in movies.values():
            if movie.p1.getX() < p.getX() < movie.p2.getX() and movie.p1.getY() < p.getY() < movie.p2.getY():
                if movie.prevs_selected is True:  # proceed only if the prevs of this movie have been selected
                    if movie.selected is False:
                        select_movie(movie)
                    else:
                        movie.my_square.setFill("white")
                        movie.selected = False
                        clear_nexts(movie)


# recursively marks all of the passed movie's children as unwatchable
def clear_nexts(movie):
    for seq in movie.seqs:
        seq.selected = False
        seq.prevs_selected = False
        seq.my_square.setFill("gray")
        clear_nexts(seq)


# marks a movie as watched and updates its children as watchable, if permissible
def select_movie(movie):
    movie.selected = True
    movie.my_square.setFill(color_rgb(125, 25, 32))
    for seq in movie.seqs:
        prevs_selected = True
        for prev in seq.prevs:
            if not prev.selected:
                prevs_selected = False
        if prevs_selected:
            seq.prevs_selected = True
            seq.my_square.setFill("white")


# create a class for movies. each movie will be at a certain point and have a name. clicking on the movie will make it
# do stuff.
class Movie:
    win = GraphWin(width=500, height=800, title="MCU Tracker", autoflush=False)
    win.setCoords(0, 0, 100, 160)

    def __init__(self, name):
        self.selected = False  # whether or not this movie has been marked as watched
        self.prevs = []  # the parents of this movie
        self.seqs = []  # the children of this movie
        self.p1 = None
        self.p2 = None
        self.my_square = None
        self.name = name  # the name of the movie
        self.prevs_selected = False  # whether or not all of this movies parents have been marked as watched

    def draw(self):
        self.my_square.draw(self.win)  # draw it to the window
        if not self.prevs_selected:
            self.my_square.setFill("gray")
        title = Text(self.my_square.getCenter(), self.name)
        title.draw(self.win)

    def set_point(self, point):
        self.p1 = Point(point.getX(), point.getY())
        self.p2 = Point(point.getX() + SQUARE_SIZE, point.getY() + SQUARE_SIZE)
        self.my_square = Rectangle(self.p1, self.p2)


if __name__ == '__main__':
    all_movies = import_movies_from_csv()
    make_window(all_movies)
