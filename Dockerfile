FROM python:3.11

# copy files 
RUN mkdir -p /home/app
COPY ./requirements.txt /home/app

# install OS dependencies
RUN apt-get update && apt-get install -y git
RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /home/app
RUN pip install -r requirements.txt

# django backend entry command
CMD ["sleep", "infinity"] 
# CMD ["python", "manage.py", "runserver"]
