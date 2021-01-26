"""
Copyright 2020 William Locatelli.
Interprets the data from the web app and process it through a
python script, returning data through system.out.
"""
import json
import sys
import Recommender as Rec


# find the n best other movies to watch if you've watched the watched and want to watch the children
# parameters:
#           watched:    list of films which have already been watched
#           children:   list of films which they want to watch
#           num_extras: the number of additional films to be included
#           rule:       the heuristic to be used to select additional films
#           count_rule: the heuristic to be used to decide how many films to return
def get_objects_and_find_best_subgraph(watched, children, num_extras, rule, count_rule):
    Rec.set_count_rule(count_rule)
    Rec.set_rule(rule)
    movies = Rec.get_movies()
    if count_rule == "Whatever It Takes":
        num_extras = len(movies)
    watched_movies = set()
    child_movies = set()
    for movie in watched:
        if movie in movies.keys():
            watched_movies.add(movies[movie])
    for movie in children:
        if movie in movies.keys():
            child_movies.add(movies[movie])
    result = Rec.find_best_subgraph(watched_movies, child_movies, num_extras)
    return Rec.watch_order(watched_movies, result)


data = json.loads(sys.argv[1])

# initialize Recommender
Rec.import_weighted_from_csv()
Rec.import_data_from_csv()

# check for the edge case in which the process times out due to heroku's restrictions
if (data['parents'][0] == "" and len(data['children']) == 1 and 11 < int(data['count']) < 13 and
        data['rule'] == "Interconnected" and data['count_rule'] == "Count" and
        data['children'][0] == "Spider-Man: Far From Home"):
    print("{'films': [], 'msg': 'This request is too computationally expensive. This can be fixed by adding a movie" +
          " you want to see, increasing/decreasing the number of requested films, or changing the heuristic.'}")
else:
    films = get_objects_and_find_best_subgraph(data['parents'], data['children'], int(data['count']), data['rule'],
                                               data['count_rule'])
    print("{'films': " + str(films) + ", 'msg': []}")
