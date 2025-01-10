from .register import register, validate_return_type
from ...models.character import CharacterState
from .base_state import BaseState
import numpy as np

@register(name="mute_followed_funcs", type="func")
@validate_return_type
def mute_followed_funcs(*args, **kwargs):
    return True, dict()

@register(name="router_use_or_chat", type="func")
@validate_return_type
def router_use_or_chat(result, obj:BaseState, *args, **kwargs):
    action = result.get("action", "")
    if action == "use":
        obj.turn_on_states( next_state_names = CharacterState.USE)        
    elif action == "chat":
        obj.turn_on_states(next_state_names = CharacterState.CHATINIT)
  
    return True, result

@register(name="router_idle_perspq", type="func")
@validate_return_type
def router_idle_perspq(overduration ,obj:BaseState, *args, **kwargs):
    if not overduration:
        return False, dict()
    
    prob = np.random.rand()
    if prob >0.5:
        obj.turn_on_states( next_state_names = CharacterState.IDLE)        
    else:
        obj.turn_on_states(next_state_names = CharacterState.PERSPQ)

    return True, dict()


@register(name="change_state_to_idle", type="func")
@validate_return_type
def change_state_to_idle(obj:BaseState, overlooped:bool, *args, **kwargs):
    if overlooped:
        obj.on_change_state(CharacterState.IDLE)
        return True, dict()
    return True, dict()
    
