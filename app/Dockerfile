FROM python:3.7.10-slim-buster

ENV CODE_DIR /var/code

RUN mkdir ${CODE_DIR}
WORKDIR ${CODE_DIR}

COPY . . 

# Install MySQL client dependencies
RUN apt-get update
RUN apt-get --yes install python3-dev default-libmysqlclient-dev build-essential

RUN pip3 install -r requirements.txt