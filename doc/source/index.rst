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



Indices and tables
==================

* :ref:`modindex`
* :ref:`search`
