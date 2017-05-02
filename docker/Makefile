static:
	docker-compose up stb-nodejs
	docker-compose exec stb-python python manage.py collectstatic --noinput

build: static
	docker-compose -f docker-compose-production.yml build

test-env-up: static
	docker-compose up -d stb-selenium-hub

test: test-env-up
	docker-compose exec stb-python python manage.py test --liveserver=stb-python:8001-8010 --parallel=8
	docker-compose stop
