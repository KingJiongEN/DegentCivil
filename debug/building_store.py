from app.service.simulation import Simulation
from app.models.building import Building

llm_cfg = Simulation.load_llm_config()['char_llm_cfg']

Building(id=1,name='home',
         llm_cfg=llm_cfg,
         xMax=100,
         xMin=0,
         yMax=100,  
         yMin=0,
         )