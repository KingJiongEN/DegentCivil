from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import paired_distances

from ..repository.artwork_repo import update_artwork_in_db, get_artwork_from_db
from .db_modules.milvus_collections import artwork_milvus_data_store, retrieve_artwork_by_prompt_emb

class MarketAdjust:
    '''
    estimate the price of an artwork based on the market model
    '''
    def __init__(self, commodities=None, model=None):
        self.commodities = commodities if commodities else []
        self.model = model if model else OpenAIEmbeddings(model="text-embedding-3-large")
        all_drawings = [] # TODO sql query to get all drawings   
        self.artwork_milvus_data_store = artwork_milvus_data_store
    
    def update(self):
        market_info = self.get_market_info()
        self.update_market(market_info)
     
    def get_market_info(self):
        return "Ronna McDaniel: Internal revolt forces Republican ex-chairwoman out at NBC"
        
        
    
    def update_market(self, market):
        '''
        estimate the price of an artwork based on the market model, here the market is a piece of news
        '''
        retrieved_artwork_high_sim = retrieve_artwork_by_prompt_emb(market, topk=20, 
                                                           other_param= {"param": {
                                                                    "metric_type": "COSINE",
                                                                   "params": {"radius": 0.0, #outer boundary of your search space
                                                                    "range_filter": 0.2} # innner boundary of your search space
                                                                    }},)
        retrieved_artwork_low_sim = retrieve_artwork_by_prompt_emb(market, topk=20, 
                                                           other_param= {"param": {
                                                                     "metric_type": "COSINE",
                                                                    "params": {"radius": 0.0, #outer boundary of your search space
                                                                    "range_filter": 0.2} # innner boundary of your search space
                                                                    }},)
        for retrieved_artwork in [retrieved_artwork_high_sim, retrieved_artwork_low_sim]:
            for row in retrieved_artwork:
                for item in row:
                    self.price_fluctuation_by_sim(item.resource_id, item.distance)
                
        # market_embed = self.call_model(market)     
        # for commodity in self.commodities:
        #     commodity_embed = self.get_commodity_embed(commodity)
        #     delta_price = self.price_fluctuation(market_embed, commodity_embed)
        #     commodity.set_price(commodity.price + delta_price)
        
    def call_model(self, commodity):
        '''
        get the embedding of a commodity
        rewrite this function if you want to use a different model rather than embedding model
        '''
        commodity_embed = self.model.embed_query(commodity)
        return commodity_embed
        
    def get_commodity_embed(self, commodity):
        '''
        rewrite this function if your commodity has no attr description
        '''
        assert hasattr(commodity, 'description') or hasattr(commodity, 'embed'), f"commodity should have attribute description or embed, your type of commodity is {type(commodity)}" 
        if hasattr(commodity, 'embed'):
            return commodity.embed
        else:
            description = commodity.description
            assert type(description) == str, f"the type of description should be str, your description is {description}. The type is {type(description)}"
            return self.call_model(description)
    
    def price_fluctuation(self, market_embed, commodity_embed):
        '''
        calculate the price of an artwork based on the similarity of their emebddings
        '''
        sim = paired_distances(market_embed[None,...], commodity_embed[None,...], metric='cosine')
        fluctuation = (sim-0.4) * 1000
        return fluctuation

    def price_fluctuation_by_sim(self, resource_id, sim):
        '''
        calculate the price of an artwork based on the similarity of their emebddings
        '''
        fluctuation = (sim-0.4) * 1000
        self.artwork_price_change(resource_id, fluctuation)
        return fluctuation
    
    def artwork_price_change(self, artwork_id, delta_price):
        '''
        change the price of an artwork
        '''
        artwork = get_artwork_from_db(artwork_id)
        if artwork:
            artwork.price += delta_price
            update_artwork_in_db(artwork_id, artwork )
            print(f"the price of the artwork {artwork_id} has changed by {fluctuation}")
            return artwork.price
        
        
if __name__ == '__main__':
    me = MarketAdjust([])
    me.update_market("Ronna McDaniel: Internal revolt forces Republican ex-chairwoman out at NBC")