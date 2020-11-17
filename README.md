If you are in the right branch and right version: \
After git clone/ git pull
1. `pip install -e client`
1. If you don't want to use the default lasagna.eecs.umich.edu address, create a `personal.yaml` file in the root directory with the following contents, setting the address and port to your liking:
```server:
  SERVER_ADDRESS: 'http://127.0.0.1'
  SERVER_PORT: '4242'```


If you are encountering dependency issues, please manually install
1. `pip install pandas`
1. `pip install numpy`
1. `pip install requests`
1. `pip install SPARQLWrapper`

Use hard refresh to refresh the website!\
Window + Chrome: ctrl+F5\
Mac + Chrome: Command + Shift + R\
Others: Google if you are not sure ;)


If you need to delete the git repo or want to do a reinstallation: 
1. `pip uninstall knps`
1. `git clone git@github.com:mikecafarella/KNP.git`
1. `pip install -e client`


If the website cannot be opened normally:
1. Check the address is correctly defined in the personal.yaml file as above
1. Check whether it is redirected to https website. Currently https is not supported
1. If you are using a Chrome Browser, and you are constantly redirected to `https://lasagna...`:\
Open `chrome://net-internals/#hsts`, \
Delete domain security policies: eecs.umich.edu


Sample Usage:
```
import knps

def main():
    a = knps.value(42,"value comment 0","Tiramisu")
    b = knps.variable(a,"variable comment 0","Tiramisu")

if __name__ == "__main__":
    main()
```

The server URL can be retrieved programatically using `knps.server_url`

More usages: See COVID_19_examples

Tips for COVID19_example: \
When running person3.py and person3tomorrow.py, please make sure that your working directory is in that folder. Because when runs `pre1 = knps.File("predict_1.png")`, the file "predict_1.png" need to be in the current working directory. 
