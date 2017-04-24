static:
	docker-compose up nodejs
	docker-compose exec python python manage.py collectstatic --noinput

build: static
	docker-compose -f docker-compose-production.yml build

test-env-up: static
	docker-compose up -d selenium-hub

test: test-env-up
	docker-compose exec python python manage.py test --liveserver=python:8001-8010 --parallel=8
