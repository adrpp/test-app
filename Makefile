
build:
	docker build -t test-app .

run:
	docker run -i -t --rm -p=8000:8000 -e PORT="8000" --name="test-app" test-app

# alias
up: build run

stop:
	docker stop test-app

rm: stop
	docker rm test-app

# alias
down: rm
