StateName2Registered = {}
FuncName2Registered = {}
PromptName2Registered = {}
import inspect

def register(name, type):
    def decorator(obj):
        assert type in ['state', 'func',  'prompt']
        class_name = name if name else obj.__name__
        if inspect.isclass(obj) or inspect.isfunction(obj):
            if type == 'state':
                StateName2Registered[class_name] = obj
            elif type == 'func':
                FuncName2Registered[class_name] = obj
            elif type == 'prompt':
                PromptName2Registered[class_name] = obj
        else:
            raise TypeError("Only classes and functions can be registered")
        
        return obj
    return decorator


from functools import wraps

# Decorator to validate return type
def validate_return_type(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not (isinstance(result, tuple) and len(result) == 2 and
                isinstance(result[0], bool) and isinstance(result[1], dict)):
            raise TypeError(f"Function {func} must return a tuple containing a stop_signal(bool) and a return dictionary. The current return is {result}")
        return result
    return wrapper