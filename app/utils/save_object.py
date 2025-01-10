import copy
import inspect
from os import kill
import ssl
import dill

def find_instance_specific_data_attrs(instance):
    cls = instance.__class__
    base_attrs = set()
    for base_cls in inspect.getmro(cls)[1:]:  # Skip the instance's class itself
        base_attrs.update(dir(base_cls))
    # assert "reply_at_receive" in base_attrs
    instance_attrs = set(dir(instance)) - base_attrs
    
    # __import__('ipdb').set_trace()
    # Filter out methods and properties from the instance's class
    data_attrs = {attr for attr in instance_attrs\
                    if not callable(getattr(instance, attr)) \
                    and not isinstance(getattr(cls, attr, None), property)\
                    and not attr.startswith('_') \
                    and not isinstance(getattr(instance, attr), ssl.SSLContext)}
    clean_data_attrs = copy.deepcopy(data_attrs)
    # for attr in data_attrs:
    #     if attr in ['drawing_agent', 'appreciate_agent', 'drawings', 'client', 'reply_at_receive','hook_lists']: # manually found
    #         clean_data_attrs.remove(attr)
    #         continue
    #     try:
    #         if is_circular_ref( instance, getattr(instance, attr)):
    #             clean_data_attrs.remove(attr)
    #     except ValueError:
    #         pass
   
    clean_data_attrs = find_savable_attr(dict((attr, getattr(instance, attr)) for attr in clean_data_attrs)) 
    
    
    # data_attrs = data_attrs -  {'drawing_agent', 'appreciate_agent', 'drawings', 'client'} # FIXME
    return list(clean_data_attrs)

def is_circular_ref( instance, attr_value):
    # for attr in data_attrs:
    # attr_value = instance.__getattribute__(attr) 
    for sub_attr_name in dir(attr_value):
            sub_attr_value = getattr(attr_value, sub_attr_name, None)
            if sub_attr_value is instance:
                return True
    return False

def find_savable_attr(attr2val):
    savable_attr = []
    for k, v in attr2val.items():
        try:
            dill.dumps(v)
            savable_attr.append(k)
        except:
            pass
    return savable_attr
            

# if __name__ == '__main__':
#     print(find_instance_specific_data_attrs(Character))