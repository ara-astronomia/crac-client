# crac-client

> **Archiviato.** Superato da [crac-cloud](https://github.com/ara-astronomia/crac-cloud),
> l'interfaccia web che ha preso il suo posto in produzione. Nessuna modifica
> qui dal 2022-04-03, contro lo sviluppo continuo di crac-cloud.
>
> Vantaggi di crac-cloud rispetto a questo client desktop:
> - **Nessuna installazione**: basta un browser, niente ambiente Python/Poetry
>   da configurare su ogni postazione da cui si vuole operare.
> - **Deployment centralizzato**: un solo servizio da aggiornare, non N
>   installazioni sparse da tenere allineate.
> - **Accessibile da remoto**: non serve essere sulla stessa rete locale del
>   server, a differenza della connessione gRPC diretta usata qui.
>
> Il codice resta qui per riferimento storico; non aprire PR su questo repo.

Client for connection to crac-server via gRPC

# Pre-requisite

``` linux
sudo apt install python3-tk
```
or 

``` mac
brew install python-tk
```

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
