# "infiniCite": Academic Paper Knowledge Base & Visualization Platform

[![GitHub stars](https://img.shields.io/github/stars/Wang-Zhongwei/infiniCite.svg?style=social&label=Star)](https://github.com/Wang-Zhongwei/infiniCite)
[![GitHub forks](https://img.shields.io/github/forks/Wang-Zhongwei/infiniCite.svg?style=social&label=Fork)](https://github.com/Wang-Zhongwei/infiniCite/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/Wang-Zhongwei/infiniCite.svg?style=social&label=Watch)](https://github.com/Wang-Zhongwei/infiniCite)

## Overview

"infiniCite" is an advanced academic paper knowledge base that hosts a subset of the world's academic paper metadata and offers a combination of keyword and semantic search engine with chat interfaces. Users are allowed to add papers to their personal library and perform operations like sharing, merging, and commenting. The platform also provides graph-based visualizations of references, citations, and co-authorship, allowing user to visualize the relationships between papers and authors in a graph traversal format.

## Features

- **Knowledge Base Hosting**: hosts a subset of academic paper metadata including the embedding vectors and tldr summaries in order to integrate with semantic search and chatbot functionalities. The platform has approximately a million articles, summing up to 90GB of data. 

- **Backend Management**: Django backend for user account management, offering functionalities such as library categorization of literature. It allows users to add papers and perform operations like sharing, merging, and commenting.

- **Interactive UI**: Developed parts of the frontend user interface using React. Integrated D3 for graph-based visualizations, enabling users to view references, citations, and co-authorship in a graph traversal format, enhancing user interactivity and experience.

- **Search Functionality**: Incorporated Elasticsearch to create an interactive chat interface in the user's knowledge base. It provides keyword search with multiple filters. Leveraging article embedding vectors and the OpenAI API, semantic search capabilities have been added to the platform.

- **Deployment**: A Docker image has been crafted for the project, and it is deployed using AWS EC2.

## Configurations
### PostgreSQL
Local or cloud PostgreSQL database is required.
```python
# In `config/db_config.py`. 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<dbname>',
        'USER': '<username>',
        'PASSWORD': '<password>',
        'HOST': '<host>',
        'PORT': '5432',
    }
}
```

### Django
Configure django secret key. 
```python
# config/django_config.py
SECRET_KEY = '<your-secret-key>
```

### Elasticsearch
Elasticsearch is a search engine that is used to provide advanced search functionality in infiniCite. When combined with article embedding, it enables semantic search capabilities, allowing users to search for papers based on their meaning rather than just keywords. Elasticsearch can be hosted either locally or in the cloud, depending on your preference.

```python
# config/elastic_config.py
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': '<your_connection_string>'
    },
}
```

### API Keys
The OpenAI API is used to integrate with elasticsearch to provide a chat search interface. 
```python
# config/api_keys.py
OPENAI_API_KEY = "<your_openai_api_key>"
```

## Installation & Usage

### Bare Metal (on Mac M1)
1. Install system-level dependencies
```bash
brew install libpq
brew install postgresql
```

2. Create and activate virtual environment `infiniCite`
```bash
python -m venv infiniCite
source .venv/bin/activate
pip install -r requirements.txt
```

3. Start Django server
```bash
python manage.py runserver
```

### Docker 
1. Start all services
```bash
docker-compose -f docker-compose.yaml up
```

2. Attach to running container 
```bash
docker exec -it <container_id> bash
```

3. Run Django server (In container)
```bash
python manage.py runserver
```

3. Stop all services (On host)
```bash
docker-compose -f docker-compose.yaml down
```

## Contributions

We welcome contributions! Please see `CONTRIBUTING.md` for details.

## License

(Include license details here.)

## Acknowledgements

(Include any acknowledgments, if necessary.)
