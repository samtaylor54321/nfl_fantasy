FROM python:3.8.13-slim-buster

RUN mkdir -p /app
COPY . main.py /app/
COPY . src /app/
COPY . data /app/data/
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8050/tcp
# Specify the command to run on container start
CMD [ "python", "./main.py" ]
