#!/bin/env sh

# @todo #205:30m Enable rsync --backup option.
#  To leave changed and/or deleted media files saved.

# sync local media with remote server, that hosts backups
rsync -r /opt/media/ backup@$BACKUP_HOST:~/stroyprombeton.ru/media
rsync -r /opt/media/ /opt/backup/stroyprombeton/media

# @todo #205:30m Do textual db backups.
#  Use pgdump utility.
