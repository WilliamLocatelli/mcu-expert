from graphics import *
import csv

root = []

SQUARE_SIZE = 5
RECT_HEIGHT = 7
RECT_WIDTH = 20
BIG_X = 0
BIG_Y = 0


# handles hover response
def motion(event):
    global BIG_X, BIG_Y
    BIG_X, BIG_Y = event.x, event.y
    for movie in Movie.open:
        if movie.p1.getX() < BIG_X/5 < movie.p2.getX() and movie.p1.getY() < 140 - (BIG_Y/5) < movie.p2.getY():
            movie.my_square.setFill("blue")
        elif movie is Movie.first:
            movie.my_square.setFill("green")
        else:
            movie.my_square.setFill("white")
    #print('{}, {}'.format(BIG_X, BIG_Y))


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


# test
def make_window(movies):
    Movie.win.bind('<Motion>', motion)
    for movie in movies.values():
        movie.draw()
        # draw lines connecting movies
        '''if len(movie.prevs) > 0:
            for prev in movie.prevs:
                line = Line(movie.p2, prev.p1)
                line.draw(Movie.win)'''
    color_best_movie(movies)
    update()
    while True:
        p = Movie.win.getMouse()
        for movie in movies.values():
            if movie.p1.getX() < p.getX() < movie.p2.getX() and movie.p1.getY() < p.getY() < movie.p2.getY():
                if movie.prevs_selected is True:  # proceed only if the prevs of this movie have been selected
                    if movie.selected is False:
                        select_movie(movie)
                        color_best_movie(movies)
                    else:
                        movie.my_square.setFill("white")
                        movie.selected = False
                        clear_nexts(movie)
                        Movie.open.append(movie)
                        color_best_movie(movies)


def color_best_movie(movies):
    max_rank = len(movies)
    max_movie = None
    for open_movie in Movie.open:
        open_movie.my_square.setFill("white")
        if not movies.get("The Avengers").selected:
            r = open_movie.rank1
        elif not movies.get("Avengers: Age of Ultron").selected:
            r = open_movie.rank2
        else: r = open_movie.rank3
        if r <= max_rank:
            max_rank = r
            max_movie = open_movie
    if max_movie:
        Movie.first = max_movie
        max_movie.my_square.setFill("green")


# recursively marks all of the passed movie's children as unwatchable
def clear_nexts(movie):
    for seq in movie.seqs:
        if seq in Movie.open: Movie.open.remove(seq)
        seq.selected = False
        seq.prevs_selected = False
        seq.my_square.setFill("gray")
        clear_nexts(seq)


# marks a movie as watched and updates its children as watchable, if permissible
def select_movie(movie):
    Movie.open.remove(movie)
    movie.selected = True
    movie.my_square.setFill(color_rgb(160, 17, 27))
    for seq in movie.seqs:
        prevs_selected = True
        for prev in seq.prevs:
            if not prev.selected:
                prevs_selected = False
        if prevs_selected:
            seq.prevs_selected = True
            Movie.open.append(seq)
            seq.my_square.setFill("white")


# create a class for movies. each movie will be at a certain point and have a name. clicking on the movie will make it
# do stuff.
class Movie:
    first = None
    open = []
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
        self.rank1 = rank1
        self.rank2 = rank2
        self.rank3 = rank3

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
