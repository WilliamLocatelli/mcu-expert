import math
from random import random

import Recommender as Rec
import Recommender2 as Rec2

def get_names(films):
    film_list = []
    for film in films:
        film_list.append(film.name)
    return str(film_list)

def test_all_films():
    all_films = []
    for movie in Rec.MOVIES:
        all_films.append(movie)
    rules = ["Relevant", "Interconnected", "Recent"]

    # generate random movie lists
    are_same = True
    for i in range(10000):
        rule = rules[math.floor(random() * 3)]
        #rule = "Relevant"
        #if i % 2 == 0:
        #    rule = "Recent"
        Rec.set_rule(rule)
        Rec2.set_rule(rule)
        films = all_films.copy()
        watched1 = set()
        children1 = set()
        watched2 = set()
        children2 = set()
        num_watched = math.floor(random() * len(all_films) / 3)
        num_children = 1 + math.floor(random() * len(all_films) / 3)
        num_extras = math.floor(random() * len(all_films) / 3)
        # num_watched = 2
        # num_children = 2
        # num_extras = 2
        for num in range(num_watched):
            n = math.floor(random() * len(films))
            watched1.add(Rec.MOVIES[films[n]])
            watched2.add(Rec2.MOVIES[films[n]])
            films.remove(films[n])

        for num in range(num_children):
            n = math.floor(random() * len(films))
            children1.add(Rec.MOVIES[films[n]])
            children2.add(Rec2.MOVIES[films[n]])
            films.remove(films[n])

        graph1 = Rec.find_best_subgraph(watched1, children1, num_extras)
        graph2 = Rec2.find_best_subgraph(watched2, children2, num_extras)

        # compare the graphs
        if len(graph1) != len(graph2):
            are_same = False
            print("Failed after " + str(i+1) + " attempts")
            print("Rule 1 was " + Rec.RULE)
            print("Rule 2 was " + Rec2.RULE)
            print("watched = " + get_names(watched1) + ", children = " + get_names(children1) + ", num_extras = " + str(num_extras))
            print("Graph 1 was " + get_names(graph1))
            print("Graph 2 was " + get_names(graph2))
            break
        else:
            for movie1 in graph1:
                are_same = False
                for movie2 in graph2:
                    if movie1.name == movie2.name:
                        are_same = True
            if not are_same:
                print("Failed after " + str(i+1) + " attempts")
                print("Rule 1 was " + Rec.RULE)
                print("Rule 2 was " + Rec2.RULE)
                print("watched = " + get_names(watched1) + ", children = " + get_names(children1) + ", num_extras = " + str(num_extras))
                print("Graph 1 was " + get_names(graph1))
                print("Graph 2 was " + get_names(graph2))
                break
        if i % 500 == 0:
            print(i)
    if are_same:
        print("Succeeded")

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

def test_specific_example(num_extras, watched, children):
    watched1 = set()
    children1 = set()
    watched2 = set()
    children2 = set()
    for name in watched:
        watched1.add(Rec.MOVIES[name])
    for name in children:
        children1.add(Rec.MOVIES[name])
    for name in watched:
        watched2.add(Rec2.MOVIES[name])
    for name in children:
        children2.add(Rec2.MOVIES[name])
    Rec.set_rule("Relevant")
    graph1 = Rec.find_best_subgraph(watched1, children1, num_extras)
    Rec2.set_rule("Relevant")
    graph2 = Rec2.find_best_subgraph(watched2, children2, num_extras)
    print("graph 1 is " + get_names(graph1))
    print("graph 2 is " + get_names(graph2))


Rec.import_weighted_from_csv()
Rec.import_data_from_csv()
Rec2.import_weighted_from_csv()
Rec2.import_data_from_csv()

watched = ['Ant-Man', 'Captain Marvel', 'Guardians of the Galaxy']
children = ['Iron Man 2', 'Black Panther', 'Spider-Man: Homecoming', 'Captain America: The Winter Soldier']

extras = 7

# test_specific_example(extras, watched, children)

test_all_films()
