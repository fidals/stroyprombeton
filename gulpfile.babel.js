// ================================================================
// IMPORTS
// ================================================================
import gulp from 'gulp';
import sequence from 'run-sequence';

const $ = require('gulp-load-plugins')();

// ================================================================
// CONSTS
// ================================================================
const ENV = {
  development: true,
  production: false,
};

const PATH = {
  src: {
    sprites: {
      main: 'front/images/spriteSrc/main/*.png',
      pages: 'front/images/spriteSrc/pages/*.png',
    },

    styles: [
      'front/scss/styles.scss',
      'front/scss/pages.scss',
    ],

    js: {
      vendors: [
        'front/js/vendors/jquery-2.2.4.min.js',
        'front/js/vendors/bootstrap.min.js', // should be removed;
        'front/js/vendors/cookie.js',
        'front/js/vendors/jquery.mask.min.js',
        'front/js/vendors/auto-complete.min.js',
        'front/js/vendors/tooltipster.bundle.min.js',
      ],

      pages: [
        'front/js/components/innerPages.es6',
        'front/js/components/productCountInput.es6',
        'front/js/components/product.es6',
        'front/js/components/category.es6',
        'front/js/components/catalog.es6',
        'front/js/components/order.es6',
      ],

      vendorsPages: [
      ],

      common: [
        'front/js/shared/*.es6',
        'front/js/components/main.es6',
        'front/js/components/autocomplete.es6',
        'front/js/components/headerCart.es6',
      ],
    },

    images: [
      'front/images/**/*',
      '!front/images/spriteSrc{,/**}',
    ],

    fonts: 'front/fonts/**/*',
  },

  build: {
    sprites: {
      pathInCss: '../images',
      img: 'front/build/images/',
      scss: {
        main: 'front/scss/common/',
        pages: 'front/scss/pages/',
      },
    },
    styles: 'front/build/css/',
    js: 'front/build/js/',
    images: 'front/build/images/',
    fonts: 'front/build/fonts/',
  },

  watch: {
    styles: 'front/scss/**/*.scss',
    js: 'front/js/**/*',
    images: 'front/src/images/**/*',
    fonts: 'front/src/fonts/**/*',
    html: 'templates/**/*',
  },
};

// ================================================================
// BUILD
// ================================================================
gulp.task('build', (callback) => {
  ENV.development = false;
  ENV.production = true;

  sequence(
    'js-vendors',
    'js-vendors-pages',
    'js-common',
    'js-pages',
    // 'js-admin',
    'sprites',
    'styles',
    'images',
    'fonts',
    callback
  );
});

// ================================================================
// Styles : Build all stylesheets
// ================================================================
gulp.task('styles', () => {
  gulp.src(PATH.src.styles)
    .pipe($.changed(PATH.build.styles, { extension: '.css' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.sassGlob())
    .pipe($.sass())
    .pipe($.if(ENV.production, $.autoprefixer({
      browsers: ['last 3 versions'],
    })))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.cssnano()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.styles))
    .pipe($.livereload());
});

// ================================================================
// JS : Build common vendors js only
// ================================================================
gulp.task('js-vendors', () => {
  gulp.src(PATH.src.js.vendors)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.concat('vendors.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.uglify())
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build common vendors-pages js only
// ================================================================
gulp.task('js-vendors-pages', () => {
  gulp.src(PATH.src.js.vendorsPages)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.concat('vendors-pages.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.uglify())
    .pipe(gulp.dest(PATH.build.js));
});

// ================================================================
// JS : Build common scripts
// ================================================================
gulp.task('js-common', () => {
  gulp.src(PATH.src.js.common)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.babel({
      presets: ['es2015'],
    }))
    .pipe($.concat('main.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.uglify()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js))
    .pipe($.livereload());
});

// ================================================================
// JS : Build all pages scripts
// ================================================================
gulp.task('js-pages', () => {
  gulp.src(PATH.src.js.pages)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.babel({
      presets: ['es2015'],
    }))
    .pipe($.concat('pages.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.uglify()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js))
    .pipe($.livereload());
});

// ================================================================
// JS : Build admin page scripts
// ================================================================
gulp.task('js-admin', () => {
  gulp.src(PATH.src.js.admin)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.babel({
      presets: ['es2015'],
    }))
    .pipe($.concat('admin.js'))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.uglify()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(PATH.build.js))
    .pipe($.livereload());
});

// ================================================================
// Images : Copy images
// ================================================================
gulp.task('images', () => {
  gulp.src(PATH.src.images)
    .pipe($.changed(PATH.build.images))
    .pipe(gulp.dest(PATH.build.images));
});

// ================================================================
// Fonts : Copy fonts
// ================================================================
gulp.task('fonts', () => {
  gulp.src(PATH.src.fonts)
    .pipe($.changed(PATH.build.fonts))
    .pipe(gulp.dest(PATH.build.fonts));
});

// ================================================================
// Sprites
// ================================================================
gulp.task('sprites', () => {
  let spriteData = gulp.src(PATH.src.sprites.main)
    .pipe($.spritesmith({
      imgName: 'sprite-main.png',
      cssName: 'sprite-main.css',
      imgPath: `${PATH.build.sprites.pathInCss}/sprite-main.png`,
    }));

  spriteData.img.pipe(gulp.dest(PATH.build.sprites.img));

  spriteData.css
    .pipe($.rename({
      extname: '.scss',
    }))
    .pipe(gulp.dest(PATH.build.sprites.scss.main));

  spriteData = gulp.src(PATH.src.sprites.pages)
    .pipe($.spritesmith({
      imgName: 'sprite-pages.png',
      cssName: 'sprite-pages.css',
      imgPath: `${PATH.build.sprites.pathInCss}/sprite-pages.png`,
    }));

  spriteData.img.pipe(gulp.dest(PATH.build.sprites.img));

  spriteData.css
    .pipe($.rename({
      extname: '.scss',
    }))
    .pipe(gulp.dest(PATH.build.sprites.scss.pages));
});

// ================================================================
// WATCH
// ================================================================
gulp.task('watch', () => {
  $.livereload.listen();
  gulp.watch(PATH.watch.styles, ['styles']);
  gulp.watch(PATH.watch.js, ['js-common', 'js-pages']);
  gulp.watch(PATH.watch.images, ['images']);
  gulp.watch(PATH.watch.fonts, ['fonts']);
  gulp.watch(PATH.watch.html, $.livereload.changed);
});

// ================================================================
// DEFAULT
// ================================================================
gulp.task('default', ['watch']);
