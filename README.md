## Project Setup

The development environment uses a private repository. To be able to install this as a dependency you will need to add
an SSH key to your GitHub account. 

```
# Check if you already have an SSH key
cat ~/.ssh/id_rsa.pub

# Create a SSH key you do not already have one
ssh-keygen -t rsa

# Copy to clipboard (Mac)
pbcopy < ~/.ssh/id_rsa.pub
```

Add your SSH key to GitHub: https://github.com/settings/keys

Set required environment variables:
```
# Valid values are development, local, postgres_local, production, or staging
DJANGO_APPLICATION_ENVIRONMENT='local'

# 64 character signing key used to authenticate network requests
NETWORK_SIGNING_KEY='6f812a35643b55a77f71c3b722504fbc5918e83ec72965f7fd33865ed0be8f81'
```

Install and run Redis:
```
brew install redis
redis-server
```

Install required packages:
```
pip3 install -r requirements/local.txt
```

To initialize the project:
1. Fill out `fixtures/self_configuration.json`
2. Run `bash scripts/reboot.sh` to load in fixture data
3. Run `python3 manage.py initialize_validator` to initialize related models

Run Celery:
```
celery -A config.settings worker -l debug
```

## Running Tests

Run all tests:
```
python3 manage.py test
```

Run all tests in parallel:
```
python3 manage.py test --parallel
```

## Developers

When adding a package, add to `requirements/base.in` and then :
```
bash scripts/compile_requirements.sh
```

Test account keys: https://docs.google.com/spreadsheets/d/1XzkE-KOOarIRkBZ_AoYIf7KpRkLEO7HOxOvLcWGxSNU/edit?usp=sharing
