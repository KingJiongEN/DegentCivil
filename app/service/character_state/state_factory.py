from typing import Callable

from . import FuncName2Registered, PromptName2Registered, StateName2Registered
from .act_state import ActState
from .base_state import BaseState
from .critic_state import CriticState
from .idle_state import IdleState
from .move_state import MoveState
from .drawinit_state import DrawInitState
from .draw_state import DrawState
from .perspect_ans_state import PerspectAnsState
from .perspect_quest_state import PerspectQuestionState
from .plan_state import PlanState
from .appreciate_state import AppreciateState
from .bargain_state import BargainState
from .emotion_state import EmotionState
from .summarize_state import SummarizeState
from .estimate_state import EstimateState
from ...constants.character_state import CharacterState
from ...models.location import BuildingList
from ...models.character import Character, CharacterList


def get_initialized_states(
        character: Character,
        character_list: CharacterList,
        building_list: BuildingList,
        change_state_callback: Callable,  # TODO better abstract
        state_config=None,
        # state_classes:dict[CharacterState, BaseState]=None,
) -> dict[CharacterState, BaseState]:
    """
    Initializes the states for a given character.
    change_state_callback: callback to change character state. By default: StateManager.change_state_by_enum
    """

    if state_config is None:
        state_classes = {
            CharacterState.IDLE: IdleState,
            CharacterState.PLAN: PlanState,
            CharacterState.PERSPQ: PerspectQuestionState,
            CharacterState.PERSPA: PerspectAnsState,
            CharacterState.MOVE: MoveState,
            CharacterState.ACT: ActState,
            CharacterState.CRITIC: CriticState,
            CharacterState.DRAWINIT: DrawInitState,
            CharacterState.DRAW: DrawState,
            CharacterState.APPRECIATE: AppreciateState,
            CharacterState.EMOTION: EmotionState,
            CharacterState.BARGAIN: BargainState,
            CharacterState.SUM: SummarizeState,
            CharacterState.ESTIMATE: EstimateState,
        }


        state_dict= {state: cls(character, character_list, building_list, change_state_callback) for state, cls in
                state_classes.items()}
    else:
        states:list[BaseState] = [ StateName2Registered[state](character, character_list, building_list, change_state_callback, **cfg) for state, cfg in state_config.items()]
        state_dict = { state.state_name: state for state in states}
        

    return state_dict
