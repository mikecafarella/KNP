# Installation

Here's how you install and run the [__Knowledge Client__](knowledgeclient.md) and the [__Universal Knowledge Collaboration Network__](sharingservice.md).



1. Berkeley DB libraries need to be available on the system. On a Mac, these can be installed using Homebrew:

        brew install berkeley-db4

    On Ubuntu,

        sudo apt install libdb-dev

2. Move to the desired directory and clone the GitHub repository using the code below

        git clone https://github.com/mikecafarella/KNP

2. From the newly created `KNP` directory, use the following command to install the Knowledge Client package. This command will install the client package as `knps` and some required packages. You can use `pip3 uninstall knps` to remove the package.

        pip3 install -e client

3. Up to now, the `knps` package is ready to go if you choose to use our server, use the following code in your program or python intepreter to import the package. The package APIs can be found at [here](api.md).

        import knps


4. To run a UKCN server locally, create a `personal.yaml` file in the repo root directory with the following contents, setting the address and port to your liking:

        server:
          SERVER_ADDRESS: 'http://127.0.0.1'
          SERVER_PORT: '4242'

5. Use the following commands to configure the flask app and run the server

        export FLASK_APP=server/server.py
        flask run

## Tutorial

Now that you've installed the system, [try out the tutorial](tutorial.md).
