FROM python:3.8.13-slim-buster

RUN mkdir -p /app
COPY . main.py /app/
COPY ./data/nfl-dynasty-rosters.csv /app/nfl-dynasty-rosters.csv
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "main.py" ]
ENTRYPOINT [ "python" ]
