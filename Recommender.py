""" Creates a GUI which allows user to specify which films they have seen and which films they
would like to see, and gives them recommendations as to which movies they should watch in between.
"""
from MarvelTracker import Movie
import csv


# takes in a CSV file, outputs a tuple containing a list of movies and a list of edges
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
        all_movies[row[0]] = this_movie
        i += 1
    # create edges
    all_edges = []
    i = 1  # skip the title row
    while i < movie_count:
        row = csv_rows[i]
        i2 = 2  # skip the series column
        while i2 < len(row):
            weight = row[i2]
            if len(weight) > 0:
                # csv_rows[i] tells you what movies i comes from, so the edges need to
                # start at the movie it came from (found in the title list[i2] and end at i
                this_edge = WeightedEdge(title_list[i2], row[0], int(weight))
                all_edges.append(this_edge)
            i2 += 1
        i += 1
    return all_movies, all_edges


class WeightedEdge:

    def __init__(self, v1, v2, weight):
        self.v1 = v1
        self.v2 = v2
        self.weight = weight


if __name__ == '__main__':
    graph = import_weighted_from_csv()
