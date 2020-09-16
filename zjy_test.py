import requests
import os
import kgpl

path_img = "./example_graph.png"
url = 'http://127.0.0.1:5000/upload'


def upload_file(filename, value_id):
    with open(filename, 'rb') as img:
        name_img= os.path.basename(filename)
        file_to_upload = {
            'file': open(name_img,'rb'),
            "value_id": open(str(value_id),'w+')
        }
        os.remove(str(value_id))
        r = requests.post(url, files=file_to_upload)
        return r.json()["filename_stored"]


def test1():
    a = upload_file(path_img, 1)
    print("original")
    print(path_img)
    print("after")
    print(a)

def test2():
    file_dict = {
        "__file__":"pic",
        "original_name": "sunrise.jpg"
    }
    kgpl.value(file_dict,"file upload test","Alice_Zou")

def test3():
    a = kgpl.load_val("http://127.0.0.1:5000/val/0")
    print(a)

def test4():
    file_dict = {
        "__file__":"pdf",
        "original_name": "01.pdf"
    }
    kgpl.value(file_dict,"file upload test 2","Peter_Chen")

def test5():
    a = kgpl.load_val("http://127.0.0.1:5000/val/1")
    print(a)

def main():

    test2()
    # test3()
    test4()
    # test5()


if __name__=="__main__":
    main()