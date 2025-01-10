from collections import defaultdict
from typing import Dict
import random
import json

class StateManager:
    """Manages internal states with numerical values between 0 and 10.
    """
    state_options = ["positive_a", "positive_b", "negative_a", "neutral_a", "negative_b", "negative_c", "negative_d", "positive_c"]
    positive_states = ["positive_a", "positive_b", "positive_c", "neutral_a"]
    negative_states = ["negative_a", "neutral_a", "negative_b", "negative_c", "negative_d"]
    
    def __init__(self, initial_state: Dict[str, float]=None, update_rate=0.7, decay_rate=0.01) -> None:
        self.states = dict()
        self.initialize_states()
        if initial_state is not None:
            for k, v in initial_state.items(): 
                v = float(v)
                assert 0 <= v <= 10, f"states should be between 0 and 10. Current state is {initial_state}"
                if k in self.state_options:
                    self.states[k] = v
        self.update_rate = update_rate
        self.decay_rate = decay_rate
        self.significant_events = defaultdict(dict)
    
    def initialize_states(self):
        """
        Initialize states with balanced values.
        """
        for key in self.state_options:
            if random.random() < 0.1:
                self.states[key] = random.randint(6, 10)
            elif random.random() < 0.8:
                self.states[key] = random.randint(0, 4)
            else:
                self.states[key] = random.randint(4, 6)
    
    def update_states(self, state_changes: list[dict]=None) -> None:
        if state_changes is None:
            self.apply_decay()
        else:
            for change in state_changes:
                state_type, intensity_delta, trigger = change.get('state'), change.get('change'), change.get('reason')
                try:
                    self.update_single_state(state_type, intensity_delta, trigger)
                except:
                    pass
                    
    def update_single_state(self, state_type: str, intensity_delta: float, trigger: str = None) -> None:
        assert state_type in self.state_options, f"state type must be in state_options. Current type is {state_type}"
        assert -5 <= intensity_delta <= 5, f"intensity change must be between -5 and 5. Current change is {intensity_delta}"
        self.states[state_type] += intensity_delta
        if trigger:
            self.record_significant_event(state_type, intensity_delta, trigger)
    
    def apply_decay(self, state_type=None, custom_rate=None):
        if custom_rate is None: 
            custom_rate = self.decay_rate
        
        if state_type is None:
            for key in self.states.keys():
                if self.states[key] > 7:
                    self.states[key] -= self.states[key] * random.uniform(0, 10) * custom_rate
                else:
                    self.states[key] += self.states[key] * random.randrange(0, 5) * custom_rate
        else:
            if self.states[state_type] > 7:
                self.states[state_type] -= self.states[state_type] * random.randrange(-5, 5) * custom_rate
            else:
                self.states[state_type] += self.states[state_type] * random.randrange(-5, 5) * custom_rate
                
        for state in self.states.keys():
            self.states[state] = max(0, min(10, round(self.states[state], 2)))
                
    def record_significant_event(self, state_type, state_delta, trigger: str):
        prev_delta = self.significant_events.get(state_type, dict()).get('delta', 1)
        if prev_delta < state_delta:
            self.significant_events[state_type].update({'delta': state_delta, 'trigger': trigger})
        else:
            self.significant_events[state_type].update({'delta': min(1, prev_delta-self.decay_rate*50), 'trigger': trigger})
            
    @property
    def current_states(self) -> Dict[str, float]:
        return self.states
    
    @property
    def most_significant_event(self):
        highest_delta = 0
        significant_trigger, trigger_state = '', ''
        for key in self.significant_events.keys():
            delta = self.significant_events[key].get('delta', 0)
            if delta > highest_delta:
                highest_delta = delta
                significant_trigger = self.significant_events[key].get('trigger', None)
                trigger_state = key
                assert significant_trigger is not None, f'trigger is None, event is {significant_trigger}'
        return significant_trigger, trigger_state
         
    @property
    def dominant_state(self) -> dict:
        dominant = max(self.states, key=self.states.get)
        return {dominant: f"{self.states[dominant]}/10"}

    @property
    def dominant_state_type(self) -> dict:
        return max(self.states, key=self.states.get)

    @property
    def dominant_state_value(self) -> dict:
        dominant = max(self.states, key=self.states.get)
        return self.states[dominant]
    
    def __repr__(self) -> str:
        return f"""States: {self.states}
                Dominant State: {self.dominant_state}"""
                
                
if __name__ == '__main__':
    print(StateManager().state_options)