If you are in the right branch and right version: \
After git clone/ git pull
1. `pip install -e client`
1. Change the `server_url = "http://lasagna.eecs.umich.edu:8080"` in kgpl.py to the url that you opened on the server.


Use hard refresh to refresh the website!\
Window + Chrome: ctrl+F5\
Mac + Chrome: Command + Shift + R\
Others: Google if you are not sure ;)


If you need to delete the git repo or want to do a reinstallation: 
1. `pip uninstall kgpl_client`
1. `git clone git@github.com:mikecafarella/KNP.git`
1. `git checkout merged_server`
1. `pip install -e client`


If the website cannot be opened normally:\
1. Check the address is correct `"http://lasagna.eecs.umich.edu:yourport`
1. Check whether it is redirected to https website. Currently https is not supported
1. If you are using a Chrome Browser, and you are constantly redirected to `https://lasagna...`:\
Open `chrome://net-internals/#hsts`, \
Delete domain security policies: eecs.umich.edu


Sample Usage:
```
from kgpl_client import kgpl

def main():
    a = kgpl.value(42,"value comment 0","Tiramisu")
    b = kgpl.variable(a,"variable comment 0","Tiramisu")

if __name__ == "__main__":
    main()
```