from graphics import *
import csv

root = []


def import_movies(file="AdjacencyList.csv"):
    # put all the rows of the csv file into a list
    movies_list = []
    with open(file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            movies_list.append(row)
    result = {}
    x = 10
    y = 150
    layer = 0
    for movie in movies_list:
        this_movie = Movie(Point(x, y), movie[0])
        result[movie[0]] = this_movie
        # add prevs
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
            x = 10
            y = y - 10
            this_movie.set_point(Point(x, y))
        this_movie.layer = layer
        # update coordinates for next movie
        x = x + 20
        '''if x > 80:
            x = 10
            y = y - 20'''
    # add nexts:
    for movie in result.values():
        if len(movie.prevs) > 0:
            for prev in movie.prevs:
                prev.seqs.append(movie)
        else:
            movie.prevs_selected = True

    return result


# test
def make_window(movies):
    '''avengers = Movie(Point(10, 20), "The Avengers")
    avengers.draw()
    captainamerica = Movie(Point(25, 50), "Captain America")
    captainamerica.draw()
    ironman = Movie(Point(80, 20), "Iron Man")
    ironman.draw()
    movies = [avengers, captainamerica, ironman]'''
    for movie in movies.values():
        movie.draw()
        '''if len(movie.prevs) > 0:
            for prev in movie.prevs:
                line = Line(movie.p2, prev.p1)
                line.draw(Movie.win)'''
    update()
    while True:
        p = Movie.win.getMouse()
        for movie in movies.values():
            if movie.p1.getX() < p.getX() < movie.p2.getX() and movie.p1.getY() < p.getY() < movie.p2.getY():
                if movie.prevs_selected is True:
                    if movie.selected is False:
                        movie.selected = True
                        movie.mySquare.setFill(color_rgb(125, 25, 32))
                        for seq in movie.seqs:
                            prevs_selected = True
                            for prev in seq.prevs:
                                if not prev.selected is True:
                                    prevs_selected = False
                            if prevs_selected is True:
                                seq.prevs_selected = True
                                seq.mySquare.setFill("white")
                    else:
                        movie.mySquare.setFill("white")
                        movie.selected = False
                        clear_nexts(movie)

def clear_nexts(movie):
    for seq in movie.seqs:
        seq.selected = False
        seq.prevs_selected = False
        seq.mySquare.setFill("gray")
        clear_nexts(seq)
# create a class for movies. each movie will be at a certain point and have a name. clicking on the movie will make it
# do stuff.
class Movie:
    win = GraphWin(width=500, height=800, title="MCU Tracker", autoflush=False)
    win.setCoords(0, 0, 100, 160)

    def __init__(self, point, name):
        self.selected = False
        self.prevs = []
        self.seqs = []
        self.p1 = Point(point.getX(), point.getY())
        self.p2 = Point(point.getX() + 5, point.getY() + 5)
        self.mySquare = Rectangle(self.p1, self.p2)
        self.name = name
        self.prevs_selected = False

    def draw(self):
        self.mySquare.draw(self.win) # draw it to the window
        if len(self.prevs) > 0:
            self.mySquare.setFill("gray")
        title = Text(self.mySquare.getCenter(), self.name)
        title.draw(self.win)

    def set_point(self, point):
        self.p1 = Point(point.getX(), point.getY())
        self.p2 = Point(point.getX() + 5, point.getY() + 5)
        self.mySquare = Rectangle(self.p1, self.p2)


if __name__ == '__main__':
    movies = import_movies()
    make_window(movies)
