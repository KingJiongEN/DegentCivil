from functools import partial
import inspect
import os
import traceback
from typing import Optional, List, Tuple, Union

class ChainResult:
    def __init__(self, result_dict=None, continue_chain=True):
        if result_dict is None:
            result_dict = {}
        self.dict = result_dict
        self.continue_chain = continue_chain


class FunctionChain:
    '''
    a list of functions that can be executed sequentially 
    '''
    def __init__(self, func_list: Union[List[callable], Tuple[callable]] = None ):
        self._functions = func_list if func_list else []
        self._results = {}
        self.continue_chain = True
        self.args = dict()
        self.sanity_check()
        
    def sanity_check(self):
        pass
        
    def add(self, func, index=None):
        """add a function into the chain"""
        index=len(self._functions) if index is None else index
        # if inspect.ismethod(func) and func.__self__ is not None:
#        #     __import__('ipdb').set_trace()
        #     self._functions.insert(index, partial(func.__func__, self=func.__self__))
        # else:
        #     self._functions.insert(index, func)
            
        self._functions.insert(index, func)
        return self


    def execute(self, obj, *args, **kwargs):
        """执行链中的函数。"""
        stop_sign = False
        kwargs['obj'] = obj
        # self.args.update(kwargs)
        return_dict = {}
        for func in self._functions:
            try:
                sig = inspect.signature(func)
                kwargs.update(self.args)
                func_kwargs = {k: v for k,v  in kwargs.items() if k in sig.parameters}
                stop_sign, return_dict = func( **func_kwargs)
                # stop_sign, return_dict = func(*args, obj=obj, **kwargs, **self.args, **return_dict)
                kwargs.update(return_dict)
                if stop_sign: break
            except Exception as e:
                print(f'error in {func}, state: {obj.state_name}')
                traceback.print_exc()
                if os.getenv('DEBUG'):
                    __import__('ipdb').set_trace()
                return False, f'{e}'   

        return True, return_dict
        
    def clear(self):
        self._functions.clear()

    def stop(self):
        self.continue_chain = False

    def store_result(self, key, value):
        self._results[key] = value

    def store_dict_result(self, result_dict):
        self._results = result_dict

    def get_result(self, key, default_result=None):
        return self._results.get(key, default_result)