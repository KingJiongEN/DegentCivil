from enum import Enum, auto


class CharacterState(Enum):
    IDLE = auto()
    MOVE = auto()
    SLEEPING = auto()
    PLAN = auto()
    ACT = auto()
    PERSP = auto()
    PERSPQ = auto()
    PERSPA = auto()
    CRITIC = auto()
    CHATINIT = auto()
    CHATING = auto()
    ACTREFLECTION = auto()
    USE = auto()
    DRAW = auto()
    DRAWINIT = auto()
    SUM = auto()
    APPRECIATE = auto()
    TRADE = auto()
    BARGAIN = auto()
    EMOTION = auto()
    WORK = auto()
    USERTRADE = auto()
    ESTIMATE = auto()
    RECEIVECHAT = auto()

StateName2State = {name: state for name, state in CharacterState.__members__.items()}

'''
InterruptableStates are states that with lower priority so that an inserted state, like ReceiveChat can be inserted in front of them.
In general, these states have no strong relation to the previous states, otherwise working memory like act_obj can be disrupted.
for example:
if state in InterruptableStates and self.character.hang_states:
    state = self.character.hang_states.pop()
'''
# TODO: do we need to redesign the working memory or some new mechanism to transfer the information across the state ? 
InterruptableStates = [CharacterState.IDLE, CharacterState.PERSP, CharacterState.PLAN, CharacterState.ACT, CharacterState.MOVE, CharacterState.CHATINIT]

def get_state_name(state):
    for name, cls in StateName2State.items():
        if state.__class__ == cls:
            return name
        
if __name__ == '__main__':
    print(get_state_name('USE'))
