from ORM_client import *
import requests


def test1():
    print("20 Singers")
    r = createRelation("Q177220")
    r.extend("P106", True, "Singer", limit=20)
    r.changeFocus("Singer_P106")
    r.extend("P569", False, "Date_of_Birth")
    r.query()
    print(r.df)

def test2():
    print("20 Singers")
    r = createRelation("Q177220")
    r.extend("P106", True, "Singer", limit=20)
    r.changeFocus("Singer_P106")
    r.extend("P569", False, "Date_of_Birth")
    r.query()
    def age_cal(birth):
        if birth == 'NA':
            return 'NA'
        date_time_obj = datetime.datetime.strptime(birth[:4], '%Y')
        return datetime.datetime.now().year - date_time_obj.year

    r.extendWithFunction('Date_of_Birth_P569',age_cal,'Age')

    print(r.df)

def test3():
    print("20 Singers")
    r = createRelation("Q177220")
    r.extend("P106", True, "Singer", limit=20, label=True)
    r.changeFocus("Singer_P106")
    r.extend("P569", False, "Date_of_Birth")
    r.query()
    r.extendWithFunction('Singer_P106Label','F1','First Name')
    r.extendWithFunction('Singer_P106Label','F2','Last Name')

    print(r.df)

def test4():

    def pob(x):
        if x == 'NA':
            return 'NA'
        url = 'https://www.google.com/maps/place/'
        for word in x.split(' '):
            url += (word + '%20')
        url = url[:-3]
        r = requests.get(url)
        return r.url
    
    pd.set_option('display.max_colwidth', 1000)
    r = createRelation("Q11696")
    r.extend('P39',True, 'President', limit=20,label=True)
    r.changeFocus('President_P39')
    r.extend('P19',False, 'Place_of_birth',label=True)
    r.query()
    r.extendWithFunction('Place_of_birth_P19Label', pob, 'url')
    print(r.df)

if __name__ == "__main__":
    # test2()
    test3()
    # test4()