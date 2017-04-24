# Quickstart

```bash 
$ cp .env.dist .env
$ nano .env # modify env vars for yourself
$ make static # build .es6 / scss files
$ docker-compose up -d # run django runverser & selenium standalone server
```

## How to build / rebuild static files (JS/CSS)?

```bash
$ make static # run gulp build & django collectstatic
```

## How to run test suite?

NB: test suite uses Selenium for integrity tests, so overall process'll be slow.

```bash
$ make test # run python manage.py test --parallel=N
```

## How to build production image?

```bash
$ make build
```
