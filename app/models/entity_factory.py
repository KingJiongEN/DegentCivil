import json
import random
from app.models.character import CharacterList
from app.models.character import Character
from app.repository.agent_repo import get_agent_from_db
from app.llm.caller import LLMCaller, GPT35Caller
from config import unique_names as name_list

from openai import OpenAI


class AgentCreation:
    default_bio = "The biography of your parents are: Parent A: {p1bio} and Parent B: {p2bio} "
    
    @staticmethod 
    def build_new_agent_from_msg( msg, character_ls: CharacterList):
        content = json.loads(msg['msg'])
        agent_id = content['agent_guid']
        neochar = AgentCreation.build_new_agent(agent_id, character_ls) 
        
        return neochar
        
    @staticmethod 
    def build_new_agent(agent_id, character_ls: CharacterList):
        
        par1, par2 = AgentCreation.find_parent_agent(agent_id, character_ls)
        new_chara_features = dict()
        for func in [AgentCreation.create_bio, AgentCreation.create_mbti, AgentCreation.get_name, AgentCreation.allocate_llm]:
            res = func(par1, par2)
            new_chara_features.update(res)

        return Character.decode_from_json(new_chara_features)
        

    @staticmethod 
    def find_parent_agent(agent_id, character_ls):
        agent_row = get_agent_from_db(agent_id)
        par_id_1 = agent_row['parent_agent_guid1']
        par1 = character_ls.get_character_by_id(par_id_1)
        par_id_2 = agent_row['parent_agent_guid2']
        par2 = character_ls.get_character_by_id(par_id_2)
        
        return par1, par2
        
    @staticmethod 
    def create_bio(par1:Character, par2: Character):
        p1bio = par1.bio
        p2bio = par2.bio
        prompt = f"Based on the biographs of the parents {p1bio} and {p2bio}, image the child's bio and name. Return in json format, like {{'child_bio': 'xxx', 'name': 'xxx'}}"
        client = OpenAI()
        response = client.chat.completions( 
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            response_format={ "type": "json_object" },
        )
        try:
            res = response['choices'][0]['message']['content']
            new_bio = json.load(res)['child_bio']
        except:
            new_bio = AgentCreation.default_bio.format(p1bio=p1bio, p2bio=p2bio)
            
        return {"bio":new_bio}
    
    @staticmethod 
    def create_mbti( par1:Character, par2: Character):
        p1mbti = par1.mbti
        p2mbti = par2.mbti
        new_mbti ='ABCD'
        for i in range(4):
            if p1mbti[i] == p2mbti[i]:
                new_mbti[i] = p1mbti[i]
            else:
                new_mbti[i] = p1mbti[i] if random.randint(0,1) == 0 else p2mbti[i]
                
        return {"mbti":new_mbti}
    
    @staticmethod 
    def get_name(agent_id, *args, **kwargs):
        return {"name":name_list[agent_id]}
    
    @staticmethod 
    def allocate_llm( *args, **kwargs):
        with open('runtime/cheap_apis.json', 'r') as file:
            cheap_apis = json.load(file)
        with open('runtime/official_apis.json', 'r') as file:
            official_apis = json.load(file)
        
        # find the least used api
        sorted_cheap_apis = dict(sorted(cheap_apis.items(), key=lambda item: len(item[1])))
        sorted_official_apis = dict(sorted(official_apis.items(), key=lambda item: len(item[1]))) 
        
        return {"llm_cfg":{'cheap_api':sorted_cheap_apis[0], 'official_api':sorted_official_apis[0]}}
         