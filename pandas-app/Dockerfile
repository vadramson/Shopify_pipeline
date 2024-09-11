# syntax=docker/dockerfile:1

# Base image
FROM python:3.10.4-slim-buster

# Just an arbitrary name for the container's  working directory
WORKDIR /app 

# Use root user to install and copy all the necessary packages
USER root
RUN apt-get update -y && apt-get install -y python3-dev python3-pip build-essential  && apt-get install gcc -y && apt-get install sudo -y && apt-get clean


RUN apt-get update && apt-get -y install sudo
      

# Create new user airflow
RUN useradd -ms /bin/bash airflow

# Add new group docker
RUN groupadd docker

# Add the created airflow user to the docker group
RUN usermod -a -G docker airflow
RUN usermod -aG docker airflow

# ** --  Start add python dependencies   -- **

# The  COPY command below copy's all files and directory in the local folder to the container's parent directory call /app


COPY . .  

# Install all necessary packages
RUN pip install -r requirements.txt


# ** --  End add python dependencies   -- **


# Use airflow user to run docker container
USER airflow

# DONT DO THIS
#RUN chmod 777 /var/run/docker.sock


# Container Entry point to execute the container
CMD [ "python", "main.py"]


