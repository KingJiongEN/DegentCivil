import json
with open('./config/building.json') as f:
    buildings = json.load(f)
    
all_equips = []
for bldg in buildings.values():
    eqp_dict = bldg.pop('equipments')
    for eqp in eqp_dict.values():
        all_equips.append(eqp)
        
alleqp_dict = dict( (eqp['name'], eqp) for eqp in all_equips)

with open('./config/equipment.json', 'w') as f:
    json.dump(alleqp_dict, f, indent=4)
with open('./config/neo_building.json', 'w') as f:
    json.dump( buildings,f, indent=4)
    
 