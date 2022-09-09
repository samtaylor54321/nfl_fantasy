install:
	python3 -m pip install --upgrade pip &&\
		python3 -m pip install -r requirements.txt

format:
	python3 -m black *.py src/*.py

lint:
	python3 -m pylint --disable=R,C *.py src/*.py

test:
	python3 -m pytest -vv --cov=src --cov=main test_*.py

build:
	docker build -t nfl-fantasy-dashboard .

run:
	docker run -p 127.0.0.1:8080:8080 nfl-fantasy-dashboard

all: install lint test build