import json
import sys
import ProcessData.Recommender as Rec

data = json.loads(sys.argv[1])
# initialize Recommender
Rec.import_weighted_from_csv()
Rec.import_data_from_csv()
films = Rec.get_objects_and_find_best_subgraph(data['parents'], data['children'], int(data['count']), data['rule'])
print(films)
# print(data)
#for parent in data['parents']:
 #   print(parent)
