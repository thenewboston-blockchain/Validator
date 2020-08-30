# Project Setup
x
You can join in the discussion over at [thenewboston Slack](https://thenewboston.slack.com/join/shared_invite/zt-fmj4j8af-reXJKdQADo7QIvAp92Ro5w?fbclid=IwAR1AKKWJ_ljPi8SpfEuQW2oCcZ8r_ho9ebanqH0fDvuppQKxSiN-k5VY4jk#/)

## Windows

This guide targets a unix environment however it is possible to perform this setup on Windows by installing Cygwin 
[here](https://cygwin.com/install.html).

When installing Cygwin ensure you add the following packages in the setup wizard choosing the most up-to-date version for each:

* python3
* python3-devel
* pip3
* gcc-core
* libffi-devel
* make
* python38-wheel
* libintl-devel
  
Once installed use Cygwin for all your command-line operations.

*This is because one of the dependencies, uWSGI, does not provide Windows support directly.*

## Steps

Set required environment variables:
```
# Valid values are development, local, postgres_local, production, or staging
export DJANGO_APPLICATION_ENVIRONMENT='local'

# 64 character signing key used to authenticate network requests
export NETWORK_SIGNING_KEY='6f812a35643b55a77f71c3b722504fbc5918e83ec72965f7fd33865ed0be8f81'
```

Install Redis:
```
brew install redis
```

Create a virtual environment with Python 3.6 or higher.

Install required packages:
```
pip3 install -r requirements/local.txt
```

To initialize the project:
```
python3 manage.py migrate
python3 manage.py initialize_test_primary_validator -ip [IP ADDRESS]
```

## Local Development

Run Redis:
```
redis-server
```

Run Celery:
```
celery -A config.settings worker -l debug
```

To monitor Celery tasks:
```
celery flower -A config.settings --address=127.0.0.1 --port=5555
```

## Developers

To watch log files:
```commandline
tail -f logs/warning.log -n 10
```

To run all tests:
```
pytest
```

When adding a package, add to `requirements/base.in` and then :
```
bash scripts/compile_requirements.sh
```

Test account keys: https://docs.google.com/spreadsheets/d/1XzkE-KOOarIRkBZ_AoYIf7KpRkLEO7HOxOvLcWGxSNU/edit?usp=sharing
