import json
import os
import sys

print(os.environ.get('ENV'))
if os.environ.get('ENV') == 'production':
    from .config_prod import ProductionConfig as config
else:
    from .config_dev import DevelopmentConfig as config

# 获取当前文件夹的路径
dir_path = os.path.dirname(os.path.realpath(__file__))


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']
    except FileNotFoundError:
        if not os.environ.get('OPENAI_API_KEY'):
            print('No api_key.json found. Please create one with your OpenAI API key.')
            sys.exit(1)


# 使用绝对路径打开JSON文件
with open(os.path.join(dir_path, "building.json"), "r") as file:
    building_data_table = json.load(file)

with open(os.path.join(dir_path, "character.json"), "r") as file:
    character_data_table = json.load(file)

with open(os.path.join(dir_path, "equipment.json"), "r") as file:
    interactable_equipments_data_table = json.load(file)

with open(os.path.join(dir_path, "boss_character.json"), "r") as file:
    boss_data_table = json.load(file)

with open(os.path.join(dir_path, "city_status.json"), "r") as file:
    city_status = json.load(file)

with open(os.path.join(dir_path, "unique_names.json"), "r") as file:
    unique_names = json.load(file)
    
with open(os.path.join(dir_path, "cheap_apis.txt"), "r") as file:
    cheap_apis = [ line.strip() for line in file.readlines()]

with open(os.path.join(dir_path, "official_apis.txt"), "r") as file:
    official_apis = [ line.strip() for line in file.readlines()]
 
with open(os.path.join(dir_path, "OAI_CFG_TMPLT.txt"), "r") as file:
    cfg_tmplt = file.read()