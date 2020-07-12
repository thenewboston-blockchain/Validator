## Project Setup

Set required environment variables:
```
# Valid values are development, local, postgres_local, production, or staging
DJANGO_APPLICATION_ENVIRONMENT='local'

# 64 character signing key used to authenticate network requests
NETWORK_SIGNING_KEY='6f812a35643b55a77f71c3b722504fbc5918e83ec72965f7fd33865ed0be8f81'
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
python3 manage.py initialize_test_validator -ip [IP ADDRESS]
```

## Running Application Locally

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

To run all tests in parallel:
```
python3 manage.py test --parallel
```

When adding a package, add to `requirements/base.in` and then :
```
bash scripts/compile_requirements.sh
```

Test account keys: https://docs.google.com/spreadsheets/d/1XzkE-KOOarIRkBZ_AoYIf7KpRkLEO7HOxOvLcWGxSNU/edit?usp=sharing
