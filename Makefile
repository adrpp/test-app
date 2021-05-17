
build:
	docker build -t test-app .

run:
	docker run -d --rm -p=8000:8000 -e PORT="8000" --name="test-app" test-app

# alias
up: build run

stop:
	docker stop test-app

rm: stop

# alias
down: rm
