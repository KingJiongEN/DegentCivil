from enum import Enum, auto

class PromptType(Enum):
    ACT = auto()
    CHATINIT = auto()
    CHATING = auto()
    ACTREFLECTION = auto()
    CHATRCEIVE = auto()
    CRITIC = auto()
    MEMORY_STORE = auto()
    PLAN = auto()
    PERSPECT = auto()
    Perspect_Quest = auto() #QA_FRAMEWORK_QUESTION
    Perspect_Ans = auto() #QA_FRAMEWORK_ANSWER
    TRADE = auto()
    USE = auto()
    DRAWINIT = auto()
    DRAW = auto()
    SUM = auto()
    APPRECIATE = auto()
    USERTRADE = auto()
    BARGAIN = auto()
    EMOTION = auto()
    ESTIMATE = auto()
    INNER_MONOLOGUE = auto()
    
    def to_str(self, ):
        return self.name.lower()
    
TypeName2Name = {name: state for name, state in PromptType.__members__.items()}

if __name__ == '__main__':
    print(PromptType.name2classes)