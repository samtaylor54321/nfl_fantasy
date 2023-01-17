FROM python:3.9.16-slim-buster

RUN adduser --system --no-create-home nonroot && \
    RUN mkdir -p /app
COPY . main.py /app/
COPY src /app/
COPY data /app/data/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
USER nonroot
EXPOSE 8080/tcp
# Specify the command to run on container start
CMD [ "python", "./main.py" ]
