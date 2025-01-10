from typing import Dict
import random

class PreferenceModel:
    categories = [
        "style_a", "style_b", "style_c", "style_d", 
        "style_e", "style_f", "style_g", "style_h", 
        "style_i", "style_j", "style_k", "style_l"
    ]
    
    def __init__(self, preferences: Dict[str, float]={}) -> None:
        self.preferences = {}
        for key in self.categories:
            self.preferences[key] = preferences.get(key, random.uniform(0, 10))
            assert isinstance(self.preferences[key], float) and 0 <= self.preferences[key] <= 10, "preference values must be between 0 and 10"
        
    @property
    def top_preferences(self, count=1) -> str:
        '''
        Return the top-N preferred categories
        '''
        return ', '.join(sorted(self.preferences, key=self.preferences.get, reverse=True)[:count])
    
    @property
    def preference_scores(self) -> Dict[str, float]:
        return self.preferences
    
    def update_preferences(self) -> None:
        for key in self.preferences:
            self.preferences[key] = min(10, max(0, self.preferences[key] + random.uniform(-0.2, 0.2)))
            
    