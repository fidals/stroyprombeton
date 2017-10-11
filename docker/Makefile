static:
	docker-compose up stb-nodejs
	docker-compose exec stb-python python manage.py collectstatic --noinput

build: static
	docker-compose -f docker-compose-production.yml build

test-env-up: static
	docker-compose up -d stb-selenium

test: test-env-up
	docker-compose exec stb-python python manage.py test --liveserver=stb-python:8001-8010 --parallel=8
	docker-compose stop

# @todo #117 run backup before deploy
deploy:
	docker-compose -f docker-compose-production.yml stop
	docker-compose -f docker-compose-production.yml pull
	docker-compose -f docker-compose-production.yml rm stb-source
	docker-compose -f docker-compose-production.yml up -d

lint:
	@docker-compose up -d stb-python
	@docker run --rm --volumes-from stb-python --workdir=/usr/app/src -it coala/base coala
	@docker-compose stop
