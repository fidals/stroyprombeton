.. stroyprombeton documentation master file, created by
   sphinx-quickstart on Tue Aug 29 15:31:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stroyprombeton's documentation
==============================

.. toctree::
   :maxdepth: 2

   table_editor
   table_editor_dev

Деплой
======
todo: Create delivery

Пока деплой происходит руками. Список команд для деплоя.

*На локали*::

   # in <proj root>/docker/
   make build


*На сервере*::

   # in <proj root>/docker/
   make deploy

todo: Resolve ci bug with imagemin
Сейчас nodejs контейнер падает при билде статики.
Чтоб не падал, залазим в него ручками и ставим руками пару npm-пакетов::

   node node_modules/optipng-bin/lib/install.js
   node node_modules/jpegtran-bin/lib/install.js
   node node_modules/gifsicle/lib/install.js

Если эти команды не помогли, вот `коммент с дополнительными инструкциями <https://github.com/fidals/shopelectro/issues/183#issuecomment-334427473>`_


Бекапы
======


Создаем бекап
-------------

Запускаем специальный контейнер - ``stb-backup-data``: ::

   cd <proj root>/docker
   make backup

В результате работы контейнер создаст несколько архивов в хост-системе:

* ``/opt/backups/stroyprombeton/database.tar.gz`` - дамп базы данных
* ``/opt/backups/stroyprombeton/media.tar.gz`` - дамп медиафайлов
* ``/opt/backups/stroyprombeton/static.tar.gz`` - дамп статики

Как применить бекап
-------------------

Для восстановления базы данных и медиафайлов достаточно запустить ``make restore`` - специальный скрипт скачает последний бекап с сервера (для доступа используются public+private ключи, в процессе восстановления всё опционально, можно выбрать то что нужно загрузить) и разместит данные директориях из которых их забирает production-версия контейнеров, т.е.:

* ``/opt/database/stroyprombeton`` - база данных, используется как volume контейнера stb-postgres
* ``/opt/media/stroyprombeton`` - медиафайлы, используется как volume контейнера stb-source
* ``/opt/static/stroyprombeton`` - статика, не подключается как volume, нужно скопировать вручную в директорию с статикой

N.B.: Некоторые данные (например, медиафайлы) могут иметь большой размер. На момент написания этой заметки, архив с медиафайлами Stroyprombeton весил ~1GB.

Indices and tables
==================

* :ref:`modindex`
* :ref:`search`
