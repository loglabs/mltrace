# pull official base image
FROM python:3.9

# set work directory
WORKDIR /src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV GIT_PYTHON_REFRESH=quiet

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# expose port
EXPOSE 8000

# copy project
COPY . .

# run command
CMD [ "python", "./mltrace/server/manage.py", "run", "--host", "0.0.0.0" ]