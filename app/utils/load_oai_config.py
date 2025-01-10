import json
import os
import shutil

# refresh the runtime folder, which is used to store the api-agent mapping, more details: config.load_oai.config.register_callback
# TODO: wrap it 
shutil.rmtree('runtime',  )
os.makedirs('runtime')

def plug_api_to_cfg(cfg_tmplt, assert_tk='$', **kwargs):
    assert 'cheap_api' in kwargs
    assert 'official_api' in kwargs
    for k, v in kwargs.items():
        cfg_tmplt = cfg_tmplt.replace(f'{assert_tk}'+'{' + f'{k}' + '}', v)
    
    if assert_tk in cfg_tmplt:
        raise AssertionError('Not all tokens are replaced')
    cfg = eval(cfg_tmplt)
    
    return cfg

def build_runtime_apis_file(api_ls, file_path):
    # TODO: singleton
    res_dict = {}
    for api in api_ls:
        res_dict[api] = []
    
    with open(f'{file_path}', 'w') as file:
        json.dump(res_dict, file, indent=1)
    
    
def register_callback(llm_cfg, guid, prefix):
    '''
    add agent id back to api
    llm_cfg = {
        'cheap_api': 'xxx',
        'official_api': 'xxx',
    }
    '''
    if type(llm_cfg) is dict:
        assert all( k in llm_cfg.keys() for k in ['cheap_api', 'official_api']), 'llm_cfg should contain cheap_api and official_api' 
        for k, v in llm_cfg.items():
            if 'api' in k:
                cate = k.split('_')[0]
                os.makedirs(f'runtime', exist_ok=True)
                file_to_write = f'runtime/{k}s.json' 
                
                with open(file_to_write, 'r') as file:
                    apis = json.load(file)
                
                if type(apis[v]) is list:
                    apis[v].append(f"{prefix}_{guid}")
                else:
                    raise NotImplementedError
                
                with open(file_to_write, 'w') as file:
                    json.dump(apis, file, indent=1)  
                    
    else:
        raise NotImplementedError