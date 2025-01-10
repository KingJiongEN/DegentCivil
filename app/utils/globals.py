task_executor = None
RESOURCE_SPLITER = '.'
emergency_fund = 100
resource_cache = dict()  # temporary dict to store resources
time_index = 0

def update_time_index(new_val: int):
    global time_index
    time_index = new_val