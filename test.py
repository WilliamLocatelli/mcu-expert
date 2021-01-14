import math
from random import random

import Recommender as Rec
import Recommender2 as Rec2


def get_names(films):
    film_list = []
    for film in films:
        film_list.append(film.name)
    return str(film_list)

Rec.import_weighted_from_csv()
Rec.import_data_from_csv()
Rec2.import_weighted_from_csv()
Rec2.import_data_from_csv()

all_films = []
for movie in Rec.MOVIES:
    all_films.append(movie)

rules = ["Relevant", "Interconnected", "Recent"]

print(all_films)

# generate random movie lists
are_same = True
for i in range(100):
    films = all_films.copy()
    watched = []
    children = []
    num_watched = math.floor(random() * len(all_films) / 3)
    num_children = 1 + math.floor(random() * len(all_films) / 3)
    num_extras = math.floor(random() * len(all_films) / 3)
    for num in range(num_watched):
        n = math.floor(random() * len(films))
        watched.append(Rec.MOVIES[films[n]])
        films.remove(films[n])

    for num in range(num_children):
        n = math.floor(random() * len(films))
        children.append(Rec.MOVIES[films[n]])
        films.remove(films[n])

    graph1 = Rec.find_best_subgraph(watched, children, num_extras)
    graph2 = Rec2.find_best_subgraph(watched, children, num_extras)

    # compare the graphs
    if len(graph1) != len(graph2):
        are_same = False
        print("Failed")
        print("Watched was " + get_names(watched) + ", Children were " + get_names(children) + ", num_extras was " + str(num_extras))
        print("Graph 1 was " + get_names(graph1))
        print("And graph 2 was " + get_names(graph2))
        break
    else:
        for movie in graph1:
            if movie not in graph2:
                are_same = False
        if not are_same:
            print("Failed")
            print("Watched was " + movie.name for movie in watched)
            print(", Children were " + child.name for child in children)
            print(", num_extras was " + str(num_extras))
            print("Graph 1 was " + str(graph1))
            print("And graph 2 was " + str(graph2))
            break

if are_same:
    print("Succeeded")
