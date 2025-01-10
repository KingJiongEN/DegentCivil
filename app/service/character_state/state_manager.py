from queue import Queue
from .base_state import BaseState
from .state_factory import get_initialized_states
from ...constants.character_state import CharacterState, get_state_name


class LengthLimitedList(list):
    def __init__(self, limit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit = limit

    def append(self, item):
        super().append(item)
        while len(self) > self.limit:
            self.pop(0)

    def extend(self, iterable):
        super().extend(iterable)
        while len(self) > self.limit:
            self.pop(0)

    def insert(self, index, item):
        if len(self) < self.limit or index < self.limit:
            super().insert(index, item)
        while len(self) > self.limit:
            self.pop(0)

class StateManager:
    def __init__(self, character, character_list, building_list, state_config: dict, init_state=None):
        '''
        update -> change state -> exist state -> enter state
        '''
        self.character = character
        self.current_state = None
        self.previous_states:LengthLimitedList[BaseState] = LengthLimitedList(limit=999)
        self.state_config = state_config
        self.states: dict[CharacterState, BaseState] = \
            get_initialized_states(character, character_list, building_list,
                                   self.change_state_callback,
                                   state_config=self.state_config)
        self.init_state = init_state if init_state else next(iter(self.states.keys()))
        self.change_state_by_enum(self.init_state)

    def change_state_by_enum(self, state_name: CharacterState):
        if not self.states.keys().__contains__(state_name):
#            __import__('ipdb').set_trace()
            raise Exception(f"no state: {state_name}")
        self.change_state(self.states[state_name])

    def post_process(self):
        """
        post exist process, 
        """
        # handing overloop
        for state in self.previous_states:
            state.post_exit()
            if state.loop_duration < 0:
                self.previous_states.remove(state)

    def change_state(self, new_state: BaseState):
        self.post_process()
             
        if self.current_state:
            self.current_state.exit_state()
            self.previous_states.append(self.current_state)
        self.current_state = new_state
        prev_state = self.previous_states[-1].state_name if len(self.previous_states) > 0 else None
        self.current_state.set_previous_state(prev_state) # TODO: cls to str
        self.current_state.enter_state()

    def add_state(self, state_name, state_obj):
        self.states[state_name] = state_obj

    def update_state(self, *args, **kwargs):
        if self.current_state: # check overlooped circle
            print(f"{self.character.name} update state: {self.current_state.__class__.__name__}")
            try:
                self.current_state.update_state(*args, **kwargs)
            except RecursionError:
                raise RecursionError(f'{self.current_state} is over looped, the circle is {self.previous_states}')
                

    def change_state_callback(self, next_state: CharacterState):
        self.change_state_by_enum(next_state)

    @property
    def last_state(self):
        return self.previous_states[-1] if self.previous_states else None
    
# class TransitionMachineManager:
#     def __init__(self, config_file):
#         self.config_file = config_file
#         self.create_state_machine(self.config_file)

#     def load_config(self):
#         with open(self.config_file, "r") as file:
#             config = json.load(file)
#             for name, sm_config in config.items():
#                 self.create_state_machine(name, sm_config)

#     def get_states(self):
#         states = [StateA(name='A')]
#         return states

#     def create_state_machine(self, sm_config):
#         states = sm_config['states']
#         transitions = sm_config['transitions']
#         self.machine = Machine( states=self.get_states(), transitions=transitions, initial=states[0])

#     def __repr__(self) -> str:
#         return f'''config:  {self.config_file},
#                     state:  {self.machine.states},
# '''
