from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.PERSPECT, type='prompt')
class PerspectPrompt(BasePrompt):
    '''
    discard the internal perspect part of the prompt
        the perceptions of your interal status are {internal_status}. 
        * analyse each item in incompleted agenda, external circumstance observation, internal status perception, plan-action reflection.
        "AnalyseInternalPerceptions":
                [
                    {
                        "perception": {
                                        "attribute": "satiety",
                                        "value": "3/10"
                                       },
                        "word_understanding": " hungery, need food",
                        "difference_level": 7,
                    },
                    {
                        "perception": {
                                        "attribute": "anger",
                                        "value": "10/10"
                                       },
                        "word_understanding": "angery, not a stable status, need to calm down",
                        "difference_level": 10,
                    },
                ],
    
    '''
    PROMPT = '''
        From your perception,
        Now the time is  {date},
        {agenda_info}
        your are at {in_building_name} now. 
        
        The observations of external circumstance are {external_obs}.
        For emotion values , higher emotion value means stronger emotion. 5 is a neutral value and means an ideal stable status.
        {plan_description} 
        your understanding of the world: {world_model}
        Considering your biography, plan and your understanding of this world, 
        find out the most substantial discrepancy between your ideal stable status and current situation.
        Ideal stable status means status
            1. meet your understanding and knowledge about the world
            2. in accordance with your previous arrangement
            3. with minium uncertainty
            4. with neutral emotion fluctuation 
        
        You follow these steps:
        {analyse_instr}
        * analyse each item in incompleted agenda, external circumstance observation, plan-action reflection.
        * for plan-action reflection, consider the discrepancy between the anticipation and the actual result
        * describe the discrepancy level from 0 to 10.
        * if all difference_level is lower than 3/10, continue your current plan
        * return in json format, begins with \{ and ends with \}, 
        
        
        Here is an example for the returned json:
        {EXAMPLE}
    '''
    
    EXAMPLE = {
            "AnalyseExternalObservations":
                [
                    {
                        "perception": {
                            "category": "building",
                            "object": "dinning room",
                            "description": "table on the wall",
                        },
                        "word_understanding": "1) tables are on the floor. 2) tables can hardly attached to the wall.",
                        "difference_level": 10,
                    },
                    {
                        "perception": {
                            "category": "building",
                            "object": "bedroom",
                            "description": "a bed in the room",
                        },
                        "word_understanding": "1) beds are always in the room. 2) rooms can have beds inside.",
                        "difference_level": 0,
                    },
                    {
                        "perception": {
                            "category": "people",
                            "object": "Jack",
                            "description": "Jack is talking with the waitress."
                        },
                        "word_understanding": "1) Jack is a friend of mine. 2) Jack is a good talker. 3) Jack is a good listener.",
                        "difference_level": 0,
                    }
                ],
            "AnalysePlanAction":
                [
                    {
                        "perception":{
                            "current_step": "go to the library to collect information about tables",
                            "previous_action": {"action": "USE", "act_obj": "library.counter", "purpose": "collect information about table physics"},
                            "interaction_summary": "Order a cup of coffee in library",
                        },
                        "word_understanding": "1) the library is a good place to collect information. 2) the interaction_summary did not realize the purpose of previous action.",
                        "difference_level": 9,
                    }
                ],
            
    }
        #     "MostDiscrepancy":{
        #                 "category": "observation",
        #                 "situation": "table on the wall",
        #                 "word_understanding": "1) tables are on the floor. 2) tables can hardly attached to the wall.",
        #                 "difference_level": 10,
        #             }
            
        
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type=prompt_type, state=state)
        self.check_exempt_layers = []
        
        # if char has ongoing agenda event, no need to perspect the incomplete agenda
        if self.character.event is None  or (self.character.event and  self.character.event.status == self.character.event.INPROGRESS):
            self.agenda_info = ''
            self.analyse_instr = "* analyse each item in external circumstance observation, internal status perception, plan-action reflection." 
        else:
            self.agenda_info = f"your incompleted agenda is {self.character.incompleted_agenda} "
            self.analyse_instr = "* analyse each item in incompleted agenda, external circumstance observation, internal status perception, plan-action reflection."

            self.EXAMPLE.update({"AnalyseIncompleteAgenda":
                    [
                        {
                            "perception": {
                                "scheduled_time": "2022-11-01 20:00",
                                "event": "Take part in the reading group in the Cafe about mystery books",
                                "status": "not started",
                                "plan": None
                            },
                            "word_understanding": "1) It is 2022-10-02 04:00, there is still much time to do this.",
                            "difference_level": 1
                        },
                        {
                            "perception": {
                                "scheduled_time": "2022-09-30 17:00",
                                "event": "Meet with Carlo to talk about future research plan. ",
                                "status": "unfinished",
                                "plan": '''GeneralDiscription: Meet with Carlo to talk about future research plan.
                                        Steps: 1) prepare the materials for the research plan 2) find Carlo 3) talk about future research plan, 
                                        CurrentStep: find Carlo '''
                            },
                            "word_understanding": "1) It is 2022-10-02 04:00, I missed the schedule time for a long time. 2) irritable personality, and he will feel displeased because of my late. 3) the research plan is very important. 4) I have finished the first step of the plan",
                            "difference_level": 8
                        }, 
                    ]}) 
    
    def create_prompt(self, perception):
        '''
        perception: {
            "external_obs":
            "internal_status": 
        }
        '''
        
        return self.format_attr(**perception)

        