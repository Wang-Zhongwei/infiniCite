## Create Virtual Environment infiniCite
```
python -m venv infiniCite
```

## Activate the Virtual Environment
```
source .venv/bin/activate
```

## Install Dependencies
```
pip install -r requirements.txt
```

## Create Configuration Files
```
mkdir -p config && cd config
touch db_config.py
touch django_config.py
cd ..
```
## Configurations
### PostgreSQL
Copy
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'infinicite',
        'USER': '<username>',
        'PASSWORD': '<password>',
        'HOST': '<host>',
        'PORT': '5432',
    }
}
```
to `config/db_config.py`. 

### Django
Copy
```
SECRET_KEY = '<your-secret-key>'
```
to `config/django_config.py`. 