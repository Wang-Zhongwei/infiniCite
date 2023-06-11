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
### MongoDB
Copy
```
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'infiniCite',
        'CLIENT': {
            'host': '<your-connection-string>'
        }
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