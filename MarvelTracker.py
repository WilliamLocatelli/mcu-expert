from graphics import *
import csv

root = []


def import_movies(file = "MCUphase1to3.csv"):
    # put all the rows of the csv file into a list
    movies_list = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            movies_list.append(row)


# test
def make_window():
    avengers = Movie(Point(10, 20), "The Avengers")
    avengers.draw()
    captainamerica = Movie(Point(25, 50), "Captain America")
    captainamerica.draw()
    ironman = Movie(Point(80, 20), "Iron Man")
    ironman.draw()
    movies = [avengers, captainamerica, ironman]
    while True:
        p = avengers.win.getMouse()
        for movie in movies:
            if movie.p1.getX() < p.getX() < movie.p2.getX() and movie.p1.getY() < p.getY() < movie.p2.getY():
                if movie.selected is False:
                    movie.mySquare.setFill(color_rgb(125, 25, 32))
                    movie.selected = True
                else:
                    movie.mySquare.setFill("white")
                    movie.selected = False



# create a class for movies. each movie will be at a certain point and have a name. clicking on the movie will make it
# do stuff.
class Movie():
    win = GraphWin(width=500, height=500)

    def __init__(self, point, name):
        self.selected = False
        self.p1 = Point(point.getX(), point.getY())
        self.p2 = Point(point.getX() + 15, point.getY() + 15)
        self.name = name
        self.mySquare = Rectangle(self.p1, self.p2)

    def draw(self):
        self.win.setCoords(0, 0, 100, 100)  # set the coordinates of the window; bottom left is (0, 0) and top right is (10, 10)
        self.mySquare.draw(self.win)  # draw it to the window


if __name__ == '__main__':
    import_movies()
