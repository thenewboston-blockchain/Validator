## Project Setup

Install required packages:
```
sudo pip3 install -r requirements/local.txt
```

When adding a package, add to `requirements/base.in` and then :
```
bash scripts/compile_requirements.sh
```

Set required environment variables:
```
# Valid values are development, local, postgres_local, production, or staging
DJANGO_APPLICATION_ENVIRONMENT

# 64 character signing key used to authenticate network requests
NETWORK_SIGNING_KEY
```

To initialize the project:
1. Fill out `fixtures/self_configuration.json`
2. Run `bash scripts/reboot.sh` to load in fixture data
3. Run `python3 manage.py initialize_validator` to initialize related models

## Running Tests

Run all tests:
```
python3 manage.py test
```

Run all tests in parallel:
```
python3 manage.py test --parallel
```

Test account keys: https://docs.google.com/spreadsheets/d/1XzkE-KOOarIRkBZ_AoYIf7KpRkLEO7HOxOvLcWGxSNU/edit?usp=sharing
