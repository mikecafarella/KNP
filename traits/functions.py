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
        unit = targets[0][0]['value']['unit']
        for target in targets:
            for t in target:
                if(t['value']['unit'] != unit):
                    return False
    except:
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
    # print(value)
    
    for target in targets:
        # print(target)
        if(isinstance(target, list)):
            # [[argument_data_1], [], ...]
            (target, ) = wu.get_value_from_datavalue(target)
        # print(target)
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

def exist(_, targets):
    if(not targets):
        return False
    for target in targets:
        if(target is None):
            return False
    return True



def range_length_le(value, targets):
    return True

def range_length_ge(value, targets):
    return True

def inflation_adjusted(_, targets):
    return True

def dummy(_, __):
    return True