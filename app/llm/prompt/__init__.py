from ...constants.prompt_type import PromptType
from .base_prompt import BasePrompt
from .perspect_prompt import PerspectPrompt
from .plan_prompt import PlanPrompt
from .actreflect_prompt import ActRlectPrompt
from .chatinit_prompt import ChatInitPrompt
from .act_prompt import ActPrompt
from .use_prompt import UsePrompt
from .drawinit_prompt import DrawInitPrompt
from .summary_prompt import SumPrompt
from .appreciate_prompt import AppreciatePrompt
from .emotion_prompt import EmotionPrompt
from .bargain_prompt import BargainPrompt
from .estimate_prompt import EstimatePrompt
# promptype2class = {PromptType.ACT : BasePrompt,
#                 PromptType.CHATINIT : BasePrompt,
#                 PromptType.CHATING: BasePrompt,
#                 PromptType.ACTREFLECTION : BasePrompt,
#                 PromptType.CHATRCEIVE : BasePrompt,
#                 PromptType.CRITIC: BasePrompt,
#                 PromptType.MEMORY_STORE : BasePrompt,
#                 PromptType.PLAN : BasePrompt,
#                 PromptType.Perspect_Quest : BasePrompt, #QA_FRAMEWORK_QUESTION
#                 PromptType.Perspect_Ans : BasePrompt, #QA_FRAMEWORK_ANSWER
#                 PromptType.TRADE : BasePrompt,
#                 PromptType.USE : BasePrompt,
#         }
 