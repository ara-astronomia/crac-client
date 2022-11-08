# crac-client
Client for connection to crac-server via gRPC

# Pre-requisite

sudo apt install python3-tk

sudo apt install libopencv-dev python3-opencv

# Install Dependencies and Configure environment

We are using Poetry as a dependency management and packaging
Go to https://python-poetry.org/ and install it

Before using this project, you should clone the crac-protobuf project 
alongside this one so that the dependency expressed on pyprject.toml 
can find the package to install.

```
poetry shell
poetry install
```

# Execute the service

You can start the gui client with:

```
cd crac_client
python app.py
```

# Compile localization

```
cd $WORKSPACE/crac-client/locales/it/LC_MESSAGES
(path to msgfmt)
/usr/local/Cellar/python@3.10/3.10.1/Frameworks/Python.framework/Versions/3.10/share/doc/python3.10/examples/Tools/i18n/msgfmt.py -o base.mo base
```
