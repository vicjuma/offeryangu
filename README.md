# offeryangu
Company Website and Mobile App


### Virtualenvironment configuration

#### creation of the venv
venv folder is exempted in the git repository because of its size
to set up the venv folder

for python3 users

```shell
  python -m venv <vituarl environment name : recommended venv, env>
```

to activate

for unix users

```shell
  source <virtual environment name>/bin/activate or
  . venv/bin/activate
```

for windows users

```shell
  <virtual environment name>\Scripts\activate
```

to install the modules

```shell
  pip install -r requirements.txt
```


to run the app in development environment use

```shell
    flask run or python app.py
```

### Mail Configurations
before running the app ensure you set email configurations as environment variables
```shell
  export MAIL_USERNAME=<your mail username>
  export MAIL_PASSWORD=<Your mail password>
```

You can also set your your configurations as defaults in the virtual environment


### Database and migrations

initalize the database migration by using the flask migrations module

```shell
        flask db init
        flask db migrate -m "first migrations " && flask db upgrade
```

For more information visit [Victor Oluoch](https://mouseinc.net/)
