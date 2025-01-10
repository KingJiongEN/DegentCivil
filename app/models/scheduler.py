class Schedule:
    def __init__(self) -> None:
        self.steps = []
        self.summary = None
        self.current_index = 0

    def advance(self):
        self.current_index += 1
        if self.is_complete:
            return 'Schedule is complete.'
        return self.steps[self.current_index]
    
    def set_steps(self, steps: list[str], summary: str, **kwargs) -> None:
        self.current_index = 0
        self.summary = summary
        self.steps = steps
    
    @property
    def current_step(self):
        if self.is_empty:
            return 'No schedule'
        if self.is_complete:
            return 'Schedule is complete.'
        return self.steps[self.current_index] 

    @property
    def is_empty(self):
        return self.summary is None

    @property
    def is_complete(self):
        if self.is_empty:
            return False
        return self.current_index >= len(self.steps)

    def __repr__(self) -> str:
        return f'''
        Overview: {self.summary},
        Steps: {self.steps},
        Current: {self.current_step}
    '''

class Task():
    '''
    Task class to store task details and progress
    '''
    PENDING, ACTIVE, PAUSED, DONE = 'pending', 'active', 'paused', 'done'
    
    def __init__(self, description: str, timing: str):
        self.description = description
        self.timing = timing
        self.status = self.PENDING
        self.valid_states = [self.PENDING, self.ACTIVE, self.PAUSED, self.DONE]
        self.schedule: Schedule = None

    def update_status(self):
        if self.schedule is None:
            self.status = self.PENDING
        elif self.schedule.is_complete:
            self.status = self.DONE

    def set_status(self, status):
        assert status in self.valid_states
        self.status = status
    
    def update_schedule(self, schedule: Schedule):
        self.schedule = schedule

    def get_description(self):
        return self.description

    def get_timing(self):
        return self.timing

    def get_status(self):
        return self.status

    def get_schedule(self):
        return self.schedule

    def __repr__(self):
        return f'Time: {self.timing}, Task: {self.description}\n, Status: {self.status}, Schedule: {self.schedule}'

class Agenda():
    '''
    Plan is interrupted by a new event: store in the agenda
    '''
    def __init__(self):
        self.agenda: dict[str, Task] = LimitedLengthDict(limit=20)
                        # {'2021-10-01 14:00': 
                        #     Event(event='Meeting with Dorothy Johnson at 2:00 PM to discuss her role and performance at the Cafe',
                        #         time='2021-10-01 14:00')
                        # }
        self.candidate_staus = ['not started', 'in progress', 'completed']
    def add_event(self, event:str, time):
        self.agenda[time] = Task(event=event, time=time)
        
    def check_date(self, date):
        return self.agenda.get(date)
    
    @property
    def incompleted_events(self):
        events = []
        for event in self.agenda.values():
            if event.status is not event.COMPLETED:
                events.append(event)
        return events
            
    @property
    def completed_events(self):
        events = []
        for event in self.agenda.values():
            if event.status is event.COMPLETED:
                events.append(event)
        return events 
   
    def serialize(self):
        return self.agenda
    
    def __repr__(self):
        return f'Agenda: {self.agenda}'

from collections import UserDict

class LimitedLengthDict(UserDict):
    def __init__(self, limit, *args, **kwargs):
        self.limit = limit
        super().__init__(*args, **kwargs)
        self._ensure_limit()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._ensure_limit()

    def _ensure_limit(self):
        while len(self.data) > self.limit:
            self.data.pop(next(iter(self.data)))
            
if __name__ == '__main__':
    agenda = Agenda()
    agenda.add_event(time='2021-10-01 14:00',
                    event='Meeting with Dorothy Johnson at 2:00 PM to discuss her role and performance at the Cafe',
                       )
    print(agenda)