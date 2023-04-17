# BaseBot

To install 

    pip install git+https://github.com/sergeybok/BaseBot.git


## To download mobile app

Provide links to iOS and Android app.

## To implement a bot

You should probably setup your database first by following the instructions below so that you can actually run the bot. But I'll descrbe how to implement a bot here for visibility.



### To start your bot

Uvicorn or gunicorn 

## To setup local db

Install and launch MongoDB by following the instructions in the [official MongoDB documentation](https://www.mongodb.com/docs/manual/administration/install-community/).

After you start your mongodb server, you have to set the environment variable to point to it. BaseBot expects the variable to be `MONGO_URI`. I recommend appending it to your bash_profile (if on Mac) or bashrc (if on Linux). The following line appends the default mongodb port (27017) to the Linux profile script which is by default `~/.bashrc`. And the `source` line re-runs the bash profile so that you don't need to start a new terminal shell for the environment variable to be present.

```
echo 'export MONGO_URI=mongodb://localhost:27017' >> ~/.bashrc
source ~/.bashrc
```


### Ubuntu Linux (summary of the official documentation)

Run the following commands to install:

```
sudo apt-get update
sudo apt-get install -y mongodb-org
```

Run the following commands to start the server:

```
sudo systemctl start mongod     # You need to run this command each time you reboot your computer
sudo systemctl status mongod    # Check that it's running
```

If there are errors e.g. `Failed to start mongod.service: Unit mongod.service not found.` Run this before re-running the commands above:

```
sudo systemctl daemon-reload
```


## To ngrok your server (Ubuntu Linux)

REFERENCE: https://www.slingacademy.com/article/deploying-fastapi-on-ubuntu-with-nginx-and-lets-encrypt/


