FROM node:11-stretch-slim

ENV DEPS_DIR=/usr/app/deps
RUN echo "DEPS_DIR=$DEPS_DIR" > /etc/environment

WORKDIR /usr/app/src/

RUN apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y ssh git \
    && git clone https://github.com/fidals/refarm-site.git $DEPS_DIR \
    && apt-get remove --purge -y git \
    && apt-get -y --purge autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY package.json package.json
COPY gulpfile.babel.js gulpfile.babel.js

# we use `--no-optional` because some optional npm dependencies fail on install
RUN npm install -g gulp-cli
# Took decision from SO: https://goo.gl/3uXZxw
RUN npm install imagemin-jpegtran imagemin-svgo imagemin-gifsicle imagemin-optipng --save
RUN npm install --no-optional

COPY front/ front
# Run it to check if `gulp build` works.
# There was problems with it. See stb#258 github issue.
RUN gulp build

# Keeps track of changes if static files are built, otherwise builds them
CMD bash -c "[ '$(ls -A /usr/app/src/front_build)' ] && gulp watch || (gulp build && gulp watch)"
