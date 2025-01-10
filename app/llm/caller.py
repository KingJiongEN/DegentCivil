import json
import re
from typing import Dict, Any

from .llm_expends.basic_caller import BasicCaller
from .llm_expends.gpt35 import GPT35Caller
from .llm_expends.gpt4 import GPT4Caller
from ..utils.log import LogManager

choices = {
    'gpt-4': GPT4Caller,
    'gpt-3.5': GPT35Caller,
}


def get_caller(model: str) -> BasicCaller:
    return choices[model]


class LLMCaller:
    def __init__(self, model: str) -> None:
        self.model = model
        self.caller = get_caller(model)()

    async def ask(self, prompt: str) -> Dict[str, Any]:
        result = await self.caller.ask(prompt)
        try:
            result = json.loads(result)
            return result
        except Exception as e:
            LogManager.log_debug(f"[LLMCaller]: response is not json, {e}")

        try:
            info = re.findall(r"\{.*\}", result, re.DOTALL)
            if info:
                info = info[-1]
                result = json.loads(info)
            else:
                result = {"response": result}
        except Exception:
            result = {"response": result}

        return result
