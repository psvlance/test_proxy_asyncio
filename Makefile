.DEFAULT_GOAL :=all
build: compose/* docker-compose.yml
	docker-compose build
tests: build
	docker-compose run test-tests
run: tests
	docker-compose run test-proxy
all: run