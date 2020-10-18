# Community

Join the community to stay updated on the most recent developments, project roadmaps, and random discussions about
completely unrelated topics.

- [thenewboston.com](https://thenewboston.com/)
- [Slack](https://join.slack.com/t/thenewboston/shared_invite/zt-hkw1b98m-X3oe6VPX6xenHvQeaXQbfg)
- [reddit](https://www.reddit.com/r/thenewboston/)
- [Facebook](https://www.facebook.com/TheNewBoston-464114846956315/)
- [Twitter](https://twitter.com/bucky_roberts)
- [YouTube](https://www.youtube.com/user/thenewboston)

# Project Setup

Follow the steps below to set up the project on your environment. If you run into any problems, feel free to leave a 
GitHub Issue or reach out to any of our communities above.

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

Run Celery (run each as a separate process):
```
celery -A config.settings worker -l debug
celery -A config.settings worker -l debug --queue block_queue --pool solo
celery -A config.settings worker -l debug --queue confirmation_block_queue --pool solo
```

To monitor Celery tasks:
```
celery flower -A config.settings --address=127.0.0.1 --port=5555
```

## Local Development (Docker edition)

Run:
```
docker-compose up # add -d to detach from donsole
```

To run all tests in parallel:
```
docker-compose run app pytest -n auto
# or
docker-compose exec app pytest # if docker-compose run is running
```

To monitor Celery tasks:
```
docker-compose exec celery celery flower -A config.settings --address=127.0.0.1 --port=5555
```

## Developers

To watch log files:
```commandline
tail -f logs/warning.log -n 10
```

To run all tests in parallel:
```
pytest -n auto
```

When adding a package, add to `requirements/base.in` and then :
```
bash scripts/compile_requirements.sh
```
