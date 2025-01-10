from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.PLAN, type='prompt')
class PlanPrompt(BasePrompt):

    PROMPT = '''
    The only buildings in the small town : {buildings}
    The situation with highest suprise and the most discrepancy between the current situation and the ideal stable status: {MostDiscrepancy}
    
    Make a plan to mitigate the discrepancy between the current situation and the ideal stable status

    You must follow the following criteria:
    * Set a clear and detailed goal, with clear rubrics.
    * According to the rubrics of the goal, analyse the current situation
    * Given the buildings and your memory, make a clear and feasible plan with multiple steps to transform the current situation to the goal. You can only include the buildings in the small town.
    * Estimate the cost of the plan
    * Make more than one candidate plans
    * Choose the plan with mininum cost
    * Return in json format
    
    Here is an example:
    {EXAMPLE}
    
    '''
    
    EXAMPLE={
            "Goal": "Understand why the table is on the wall.",
            "GoalRubrics":{
                "1": "Understand the physical feauters of tables that makes the table on the wall. ",
                "2": "Understand the physical feauters of walls that makes the table on the wall. ",
                "3": "Understand the physical principles that may contribute to attaching the table to the wall. ",
            },
            "CurrentSituation":{
                "1": "No nothing about the physical feauters of tables that makes the table on the wall. ",
                "2": "No nothing about the physical feauters of walls that makes the table on the wall. ",
                "3": "No nothing about the physical principles that may contribute to attaching the table to the wall. ", 
            },
            "Plans":{
                "PlanA":{
                    "GeneralDiscription": "Ask the most knowledgable people for help.",
                    "Steps": {
                        "1": "Find the most knowledgable people.",
                        "2": "Ask about the physical feauters of tables.",
                        "3": "Ask about the physical feauters of walls.",
                        "4": "Ask about the physical principles that may contribute to attaching the table to the wall." ,
                    },
                    "StepCosts":{
                        "1": "Finding the most knowledgable people is hard because I am not sure who is the most knowledgable one and where he/she is. That may cost medium-amount of money and medium-amount of time ",
                        "2": "Asking about the physical feauters of tables is easy. That may cost low-amount of vigor.",
                        "3": "Asking about the physical feauters of walls is easy. That may cost low-amount of vigor .",
                        "4": "Asking about the physical principles that may contribute to attaching the table to the wall is easy. That may cost low-amount of vigor." , 
                    },
                    "TotalCost": "medium-amount of money and large-amount of time and 3* low-amount of vigor"
                },
                "PlanB":{
                    "GeneralDiscription": "Go to the library to find the answer from books.",
                    "Steps": {
                        "1": "Go to the library.",
                        "2": "Find the physical books containing the physical feauters of tables.",
                        "3": "Find the physical books containing the physical feauters of walls.",
                        "4": "Find the physical books containing the principles that may contribute to attaching the table to the wall.", 
                    } ,
                    "StepCosts":{
                        "1": "Going to the library is easy since it has a certain location. That may cost low-amount of money and low-amount of time ",
                        "2": "Finding the physical books containing the physical feauters of tables is hard, since I dont know which book contains these contents. That may cost large-amount of vigor and time.",
                        "3": "Finding the physical books containing the physical feauters of walls is hard, since I dont know which book contains these contents. That may cost large-amount of vigor and time.",
                        "4": "Finding the physical books containing the principles that may contribute to attaching the table to the wall is hard, since I dont know which book contains these contents. That may cost large-amount of vigor and time.", 
                    },
                    "TotalCost": "low-amount of money and low-amount of time and 3* large-amount of vigor and time" 
                },
            },
            "BestPlan": {
                    "GeneralDescription": "Ask the most knowledgable people for help.",
                    "Steps": {
                        "1": "Find the most knowledgable people.",
                        "2": "Ask about the physical feauters of tables.",
                        "3": "Ask about the physical feauters of walls.",
                        "4": "Ask about the physical principles that may contribute to attaching the table to the wall." ,
                    }, 
            }
        }
    
    
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.recordable_key = ['BestPlan', 'Goal', 'CurrentSituation']
    
    def create_prompt(self):    
        return super().create_prompt()