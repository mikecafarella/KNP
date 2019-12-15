"""
'targets' should be iterable, such as list, tuple...
"""
import wikidata_utils as wu


def same_unit(_, targets):
    """Return True if all targets have the same unit, otherwise False.
        
    Input:
      datavalue(s), 'type' should be 'quantity'.
    
    Output: 
      Boolean
    """
    if(not targets):
        return True
    try:
        unit = targets[0]['value']['unit']
    except:
        raise TypeError("Target is not a 'datavalue' of 'quantity' 'datatype'.")

    for target in targets:
        if(target['value']['unit'] != unit):
            return False
    return True


def _is(value, targets):
    """Return True if all targets are 'value', otherwise False.

    Input:
      Anything, 'value' should support 'in'

    Output:
      Boolean
    """
    if(not targets):
        return False
    for target in targets:
        if(isinstance(target, dict)):
            # it's 'datavalue'
            target = wu.get_value_from_datavalue(target)[0]
        if(target not in value):
            return False
    return True

def is_type(value, targets):
    if(not targets):
        return False
    for target in targets:
        if(not isinstance(target, eval(value))):
            return False
    return True

def range_limit(value, targets):
    """Return True if all targets """
    pass

def inflation_adjusted(_, targets):
    return True

def dummy(_, __):
    return True