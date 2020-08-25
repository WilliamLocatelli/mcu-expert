import json
import sys
import ProcessData.Recommender as Rec

data = json.loads(sys.argv[1])
# initialize Recommender
Rec.import_weighted_from_csv()
Rec.import_data_from_csv()
# print(data)
if (data['parents'][0] == "" and len(data['children']) == 1 and 10 < int(data['count']) < 14 and
        data['rule'] == "Interconnected" and data['count_rule'] == "Count" and
        data['children'][0] == "Spider-Man: Far From Home"):
    print("{'films': [], 'msg': 'This request is too computationally expensive. This can be fixed by adding a movie" +
          " you want to see, increasing/decreasing the number of requested films, or changing the heuristic.'}")
else:
    films = Rec.get_objects_and_find_best_subgraph(data['parents'], data['children'], int(data['count']), data['rule'],
                                                   data['count_rule'])
    print("{'films': " + str(films) + ", 'msg': []}")
# print(data)
# for parent in data['parents']:
#   print(parent)
