from enum import Enum


def serialize(obj, seen=None, ignores=None, allowed=None):
    """
    Serialize a Python object into a dictionary, handling circular references,
    and optionally ignoring or including specific attributes based on configuration.

    :param obj: The Python object to be serialized.
    :param seen: (Internal use) A set used to track already visited objects to avoid circular references.
    :param ignores: A list of string names of attributes that should not be serialized.
    :param allowed: A list of string names of attributes that are allowed to be serialized. If provided,
                    only these attributes will be serialized. If this parameter is empty (default),
                    all attributes except those in the 'ignores' list will be serialized.

    Functionality:
    - Serializes basic data types, Enums, dictionaries, and custom class objects with __dict__ attributes.
    - Recursively serializes attributes or key-value pairs for dictionaries and custom class objects.
    - When handling dictionaries, if a value is of an Enum type, it is serialized as the name of the Enum.
    - Handles circular object references to avoid infinite recursion.
    - The 'ignores' and 'allowed' parameters allow for flexible configuration of serialization details.

    Return Value:
    Returns a dictionary representing the serialized object.

    Example Usage:
    class MyClass:
        def __init__(self, value):
            self.value = value
            self.circular_ref = None

    obj = MyClass(123)
    obj.circular_ref = obj

    # Serialize, ignoring the 'circular_ref' attribute
    serialized_obj = serialize(obj, ignores=['circular_ref'])

    # Serialize, including only the 'value' attribute
    serialized_obj = serialize(obj, allowed=['value'])
    """
    if seen is None:
        seen = set()
    if ignores is None:
        ignores = []

    # Directly handle Enum type
    if isinstance(obj, Enum):
        return obj.name

    # Handle simple, non-recursive types
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj

    # Handle dictionaries
    elif isinstance(obj, dict):
        # Serialize only allowed attributes if specified, otherwise serialize all except ignored ones
        return {str(key): serialize(value, seen, ignores)
                for key, value in obj.items()
                if (allowed is None and key not in ignores) or (allowed is not None and key in allowed)}

    # Handle objects with a __dict__ attribute (custom classes)
    elif hasattr(obj, '__dict__'):
        # Check for circular reference
        obj_id = id(obj)
        if obj_id in seen:
            # Skip circular reference
            return f"Object(id={obj_id}) - Circular Reference"

        seen.add(obj_id)

        # Serialize only allowed attributes if specified, otherwise serialize all except ignored ones
        return {str(attr): serialize(getattr(obj, attr), seen, ignores)
                for attr in vars(obj)
                if not callable(getattr(obj, attr)) and not attr.startswith("__")
                and ((allowed is None and attr not in ignores) or (allowed is not None and attr in allowed))}

    # Fallback for other types
    else:
        return str(obj)
