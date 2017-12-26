dc=docker-compose
d=docker
dcp=docker-compose -f docker-compose-production.yml

migrate:
	$(dc) exec stb-python python manage.py migrate

# for local env
static:
	@docker-compose run --rm stb-nodejs bash -c "\
		npm install && \
		npm install -g gulp-cli && \
		gulp build"

# for local env
build: static
	$(dc) build stb-python && $(dcp) build
	$(dcp) push

# for local env
test: static
	$(dc) up -d stb-selenium
	$(dc) exec stb-python python manage.py test --liveserver=stb-python:8001-8010 --parallel=8
	$(dc) stop

# for local env
lint:
	$(dc) up -d stb-python
	$(d) run --rm --volumes-from stb-python --workdir=/usr/app/src -it coala/base coala
	$(dc) stop

# for local env
restore:
	@bash ../etc/stb-backup-restore.sh

# for serv env
backup:
	$(dcp) up stb-backup-data

# start dev environment
dev: build
	$(dc) up -d stb-python
	$(dc) exec stb-python python manage.py migrate
	# launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(dc) exec stb-python python manage.py collectstatic --noinput
	$(dc) stop && $(dc) up -d  # to make fresh collected static visible immediately

# for serv env
deploy: backup
	$(dcp) pull
	$(dcp) stop
	$(dcp) rm -f stb-source
	$(dcp) up -d
	$(dcp) exec stb-python python manage.py migrate
	# launch "collectstatic" not in build env, but on deploy.
	# Because ManifestStaticStorage writes to db
	$(dcp) exec stb-python python manage.py collectstatic --noinput
	$(dcp) stop && $(dcp) up -d  # to make fresh collected static visible immediately
