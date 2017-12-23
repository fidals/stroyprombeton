# Stroyprombeton's documentation

## Деплой

todo: Create delivery

Пока деплой происходит руками. Список команд для деплоя.

### На локали

```bash
# in <proj root>/docker/
make build
```

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
