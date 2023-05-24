FROM python:3.11

RUN mkdir -p /home/app
COPY ./app /home/app
COPY ./requirements.txt /home/app

WORKDIR /home/app
RUN pip install -r requirements.txt

# django backend entry command

