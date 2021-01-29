# Installation

Here's how you install and run the [__Knowledge Client__](knowledgeclient.md) and the [__Universal Knowledge Collaboration Network__](sharingservice.md).



1. Berkeley DB libraries need to be available on the system. On a Mac, these can be installed using Homebrew:

        brew install berkeley-db4

    On Ubuntu,

        sudo apt install libdb-dev

2. Move to the desired directory and clone the GitHub repository using the code below

        git clone https://github.com/mikecafarella/KNP

2. From the newly created `KNP` directory, use the following command to install the Knowledge Client package. (Recommended: install within a  **virtual environment**.)

        pip3 install -e client

    This command will install the client package as `knps` and some required packages. You can use `pip3 uninstall knps` to remove the package.

3. You can now use `import knps` in python programs. The package APIs can be found at [here](api.md).

## UKCN server configuration

4. To run a UKCN server locally, create a `personal.yaml` file in the repo root directory with the following contents, setting the address and port to your liking:

        server:
          SERVER_ADDRESS: 'http://127.0.0.1'
          SERVER_PORT: '4242'

5. Use the following commands to configure the flask app and run the server

        python server/server.py

## Tutorial

Now that you've installed the system, [try out the tutorial](tutorial.md).
