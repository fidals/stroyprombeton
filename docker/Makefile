dc=docker-compose
d=docker
dcp=docker-compose -f docker-compose-production.yml

# for local env
static:
	$(dc) up stb-nodejs

# for local env
build: static
	$(dc) build stb-python && $(dcp) build
	$(dcp) push

# for local env
test-env-up: static
	$(dc) up -d stb-selenium

# for local env
test: test-env-up
	$(dc) exec stb-python python manage.py test --liveserver=stb-python:8001-8010 --parallel=8
	$(dc) stop

# for local env
restore:
	@bash ../etc/stb-backup-restore.sh

# for serv env
backup:
	$(dcp) up stb-backup-data

# @todo #117 run backup before deploy

# for serv env
deploy:
	$(dcp) pull
	$(dcp) stop
	$(dcp) rm stb-source
	$(dcp) up -d
	$(dcp) exec stb-python python manage.py migrate
	# launch "collectstatic" not in build env, but on deploy.
	# Because ManifestStaticStorage writes to db
	$(dcp) exec stb-python python manage.py collectstatic --noinput
	$(dcp) exec stb-python bash -c "cd doc/ && make html"
	$(dcp) stop && dc up -d  # to make fresh collected static visible immediately

# for local env
lint:
	$(dc) up -d stb-python
	$(d) run --rm --volumes-from stb-python --workdir=/usr/app/src -it coala/base coala
	$(dc) stop
