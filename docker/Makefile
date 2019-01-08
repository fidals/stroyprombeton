dc=docker-compose
d=docker
dcb=$(dc) -f docker-compose-build.yml
dcp=$(dc) -f docker-compose-production.yml

.PHONY: migrate create-env build-static watch-static \
build test backup restore \
generate-production-static-data deploy


# ---------------------- Dev section ----------------------
migrate:
	$(dc) run --rm app python manage.py migrate

fixtures:
	$(dc) run --rm app bash -c "\
		python manage.py loaddata stroyprombeton/fixtures/admin.json \
		&& python manage.py loaddata stroyprombeton/fixtures/dump.json \
	"

prices:
	$(dc) exec app python manage.py price

create-env:
	@bash ./create-env.sh

create-config:
	@bash ./create-config.sh

npm-install:
	$(dcb) build --no-cache nodejs

build-static:
	$(dc) run --rm nodejs gulp build

watch-static:
	$(dc) run --rm nodejs

collectstatic:
	$(dc) exec app python manage.py collectstatic --noinput

test: build-static
	$(dc) up -d selenium
	$(dc) exec app python manage.py test --parallel
	$(dc) stop

lint-code:
	$(dc) run --rm lint

lint-pdd:
	$(dc) run --rm pdd

lint-pdd-verbose:
	$(dc) run --rm pdd --verbose

lint:
	$(MAKE) lint-code
	$(MAKE) lint-pdd

deploy-dev:
	$(MAKE) create-env
	# uncomment in #167
	# $(MAKE) create-config
	$(dc) pull
	$(dc) up -d app
	$(MAKE) build-static
	$(MAKE) migrate
	# Create admin user with login/pass: admin/asdfjkl;
	$(MAKE) fixtures
	# Launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(MAKE) collectstatic
	# to make fresh collected static visible immediately
	$(dc) stop app && $(dc) up -d app


# ---------------------- Production deploy section ----------------------
# @todo #142:60m Resurrect backup system.
#  Right now it's too dangerous and not used.
backup:
	$(dcp) run --rm backup-data sh /usr/bin/entrypoint.sh

restore:
	@bash ../etc/backup/backup-restore.sh

generate-production-static-data:
	$(dcp) exec app python manage.py price

# drone should do this in working flow.
# But if drone don't do this for some reasons,
# you can run this recipe from local machine.
prepare-deploy:
	rm -rf front/build
	$(dc) stop app && $(dcp) stop app
	$(dc) rm -f app && $(dcp) rm -f app
	$(MAKE) build-static
	$(dcb) build --no-cache python-dev python-prod
	$(dcb) push python-dev python-prod

deploy:
	$(dcp) pull
	$(dcp) stop
	# to flush nginx's inner static caches
	$(dcp) rm -f app nginx && $(dcp) up -d app nginx
	$(dcp) exec app python manage.py migrate
	$(MAKE) -j generate-production-static-data
	# Launch "collectstatic" not in static recipe because ManifestStaticStorage writes to db
	$(dcp) exec app python manage.py collectstatic --noinput
	# to make fresh collected static visible immediately
	$(dcp) stop && $(dcp) up -d
