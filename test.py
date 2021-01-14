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

# generate random movie lists
are_same = True
for i in range(10000):
    #rule = rules[math.floor(random() * 3)]
    rule = "Relevant"
    if i % 2 == 0:
        rule = "Recent"
    Rec.set_rule(rule)
    Rec2.set_rule(rule)
    films = all_films.copy()
    watched = []
    children = []
    #num_watched = math.floor(random() * len(all_films) / 3)
    #num_children = 1 + math.floor(random() * len(all_films) / 3)
    #num_extras = math.floor(random() * len(all_films) / 3)
    num_watched = 2
    num_children = 2
    num_extras = 2
    for num in range(num_watched):
        n = math.floor(random() * len(films))
        watched.append(Rec.MOVIES[films[n]])
        films.remove(films[n])

    for num in range(num_children):
        n = math.floor(random() * len(films))
        children.append(Rec.MOVIES[films[n]])
        films.remove(films[n])

    graph2 = Rec2.find_best_subgraph(watched, children, num_extras)
    graph1 = Rec.find_best_subgraph(watched, children, num_extras)

    # compare the graphs
    if len(graph1) != len(graph2):
        are_same = False
        print("Failed after " + str(i) + " attempts")
        print("Rule 1 was " + Rec.RULE)
        print("Rule 2 was " + Rec2.RULE)
        print("Watched was " + get_names(watched) + ", Children were " + get_names(children) + ", num_extras was " + str(num_extras))
        print("Graph 1 was " + get_names(graph1))
        print("Graph 2 was " + get_names(graph2))
        break
    else:
        for movie in graph1:
            if movie not in graph2:
                are_same = False
        if not are_same:
            print("Failed after " + str(i) + " attempts")
            print("Rule 1 was " + Rec.RULE)
            print("Rule 2 was " + Rec2.RULE)
            print("Watched was " + get_names(watched) + ", Children were " + get_names(children) + ", num_extras was " + str(num_extras))
            print("Graph 1 was " + get_names(graph1))
            print("Graph 2 was " + get_names(graph2))
            break

print("Succeeded")
#Graph 1 was ['Doctor Strange', 'Guardians of the Galaxy Vol. 2', 'Captain Marvel', 'Ant-Man', 'Guardians of the Galaxy', 'Avengers: Age of Ultron']
#Graph 2 was ['Doctor Strange', 'Guardians of the Galaxy Vol. 2', 'Captain Marvel', 'Ant-Man', 'Guardians of the Galaxy', 'The Avengers']
# films = all_films.copy()
# watched = [Rec.MOVIES['Doctor Strange'], Rec.MOVIES['Guardians of the Galaxy Vol. 2']]
# children = [Rec.MOVIES['Captain Marvel'], Rec.MOVIES['Ant-Man']]
# num_extras = 2
#num_watched = math.floor(random() * len(all_films) / 3)
#num_children = 1 + math.floor(random() * len(all_films) / 3)
#num_extras = math.floor(random() * len(all_films) / 3)
'''num_watched = 2
num_children = 2
for num in range(num_watched):
    n = math.floor(random() * len(films))
    watched.append(Rec.MOVIES[films[n]])
    films.remove(films[n])

for num in range(num_children):
    n = math.floor(random() * len(films))
    children.append(Rec.MOVIES[films[n]])
    films.remove(films[n])'''

# Rec.set_rule("Relevant")
# graph1 = Rec.find_best_subgraph(watched, children, num_extras)
# Rec.set_rule("Recent")
# graph2 = Rec.find_best_subgraph(watched, children, num_extras)
# Rec.set_rule("Relevant")
# graph3 = Rec.find_best_subgraph(watched, children, num_extras)
# print("graph 1 is " + get_names(graph1))
# print("graph 2 is " + get_names(graph2))
# print("graph 3 is " + get_names(graph3))
