[![PDD status](http://www.0pdd.com/svg?name=fidals/stroyprombeton)](http://www.0pdd.com/p?name=fidals/stroyprombeton)


# Stroyprombeton's documentation

## Деплой

todo: Create delivery

Пока деплой происходит руками. Список команд для деплоя.

### На локали
Разворачиваем среду разработки

```bash
git clone git@github.com:fidals/stroyprombeton.git
cd stroyprombeton/docker/
# cp .env.dist .env - только в первый раз
# меняем значения из `.env` на свои собственные. См ниже
make dev
```

*Файл .env*
После копирования из `.env.dist` заполняем файл `.env` или случайными значениями, или выданными.
Примеры:
- Генерим случайные: Django secret key, пароли к локальным базам
- Запрашиваем у Архитектора: Пароль к FTP и почтовому серву 

Проверяем адрес `http://127.0.0.1:8020` - загружается сайт.
Вместо порта `8020` может быть другой - константа `VIRTUAL_HOST_EXPOSE_PORT` в файле `.env`. 

### На сервере

```bash
# in <proj root>/docker/
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

Для восстановления базы данных и медиафайлов достаточно запустить `make restore` - специальный скрипт скачает последний бекап с сервера (для доступа используются public+private ключи, в процессе восстановления всё опционально, можно выбрать то что нужно загрузить) и разместит данные директориях из которых их забирает production-версия контейнеров, т.е.:

* `/opt/database/stroyprombeton` - база данных, используется как volume контейнера stb-postgres
* `/opt/media/stroyprombeton` - медиафайлы, используется как volume контейнера stb-source
* `/opt/static/stroyprombeton` - статика, не подключается как volume, нужно скопировать вручную в директорию с статикой

N.B.: Некоторые данные (например, медиафайлы) могут иметь большой размер. На момент написания этой заметки, архив с медиафайлами Stroyprombeton весил ~1GB.

# Инструкции к фичам
- [Table Editor](https://github.com/fidals/stroyprombeton/blob/master/doc/table_editor.md)
