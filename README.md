[![PDD status](http://www.0pdd.com/svg?name=fidals/stroyprombeton)](http://www.0pdd.com/p?name=fidals/stroyprombeton)


# Stroyprombeton's site documentation
Репозиторий интернет-магазина stroyprombeton.
Разрабатываем [по методологии PDD](http://fidals.com/dev).

## Команда
[Линк на роли в команде](https://goo.gl/Qq4vi4) разработки сайта.

## Разворачиваем проект

Инструкции для быстрой развёртки проекта для разработки.
Подробности смотрите Makefile и drone.yml.

Для сокращения введём такие алиасы::

```bash
bash alias dc="docker-compose"
bash alias dcp="docker-compose -f docker-compose-production.yml"
```

### Для разработки

**Готовим код к работе**
```bash
git clone git@github.com:fidals/stroyprombeton.git
cd stroyprombeton/docker/
# this command will ask you to fill some files.
# See this instruction below to get out how to do it.
make deploy-dev
```

**Файлы env**
`make deploy-dev` создаст файлы для окружения (env) со стандартными значениями.
А затем попросит заполнить их.
Пару рекомендаций по заполнению:
- Генерим случайные: Django secret key, пароли к локальным базам

Проверяем адрес `http://127.0.0.1:8020` - загружается сайт.
Вместо порта `8020` может быть другой - переменная окружения (env var) `VIRTUAL_HOST_PORT`.

**Установка refarm-site**
Сайт использует refarm-site как внешнюю зависимость.
Интерфейс refarm-site нестабилен,
поэтому иногда при разработке фичи сайта
нужно поправить код refarm-site вместе с кодом сайта.
Для этого можно установить его как зависимость для разработки (`pip -e`).
И примонтировать внутрь контейнера app.
Смотрите на переменную окружения `REFARM_SITE`.

**Админка**
Адрес: /admin/

Логин/пароль:
admin/asdfjkl;

### Для деплоя
Этот раздел полезен только Архитекторам.
Деплой на сервер делаем руками.

```bash
make deploy
```


## Бекапы


### Создаем бекап

Запускаем специальный контейнер - `stb-backup-data`:

```bash
cd <proj root>/docker
make backup
```

В результате работы контейнер создаст несколько архивов в хост-системе:

* `/opt/backups/stroyprombeton/database.tar.gz` - дамп базы данных
* `/opt/backups/stroyprombeton/media.tar.gz` - дамп медиафайлов
* `/opt/backups/stroyprombeton/static.tar.gz` - дамп статики

### Применяем бекап

Для восстановления базы данных и медиафайлов достаточно запустить ``make restore``.
Скрипт скачает последний бекап с сервера и разместит файлы в продакшен-папках.
Для доступа к бэкап-серверу используются public+private ключи.

* `/opt/database/stroyprombeton` - база данных, используется как volume контейнера stb-postgres
* `/opt/media/stroyprombeton` - медиафайлы, используется как volume контейнера stb-source
* `/opt/static/stroyprombeton` - статика, не подключается как volume, нужно скопировать вручную в директорию с статикой

N.B.: Некоторые данные (например, медиафайлы) могут иметь большой размер. На момент написания этой заметки, архив с медиафайлами Stroyprombeton весил ~1GB.

# Фичи
- [Tracking aims](https://github.com/fidals/shopelectro/blob/master/doc/tracking_aims.md)
- [Table Editor](https://github.com/fidals/stroyprombeton/blob/master/doc/table_editor.md)
- [Options](https://github.com/fidals/stroyprombeton/blob/master/doc/options.md)
