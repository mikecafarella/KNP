import datetime

func_list = []

def add_func(func):
    func_list.append(func)
    
def func_num():
    return len(func_list)

def temp0(x):
    return x

def temp1(name: str):
    return name.split(' ')[0]

def temp2(name: str):
    return name.split(' ')[-1]

def temp3(birth):
    if birth == 'NA':
        return 'NA'
    date_time_obj = datetime.datetime.strptime(birth[:4], '%Y')
    return datetime.datetime.now().year - date_time_obj.year

func_list = [temp0, temp1, temp2, temp3]