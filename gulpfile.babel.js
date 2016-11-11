// ================================================================
// IMPORTS
// ================================================================
import gulp from 'gulp';
import sequence from 'run-sequence';

const $ = require('gulp-load-plugins')();
const spawnSync = require('child_process').spawnSync;

// ================================================================
// Utils
// ================================================================
/**
 * Get src paths from given appName.
 * Usage:
 *   appPath = getAppSrcPath('pages');
 *
 *   const PATH = {
 *     src: {
 *       styles: [
 *         'front/less/admin.less',
 *         'front/less/styles.less',
 *         'front/less/pages.less',
 *         ...appPath.styles,
 *       ],
 * @param {string} appName
 * @returns {Object} - app's source file paths
 * (ex. {styles: ['~/app_name/front/styles/style.less'], ...})
 */
function getAppSrcPaths(appName) {
  const processData = spawnSync('python3', ['manage.py', 'get_app_path_for_gulp', appName]);
  const err = processData.stderr.toString().trim();
  if (err) throw Error(err);

  const appPath = processData.stdout.toString().trim();

  return require(`${appPath}/front/paths.js`);
}

// ================================================================
// CONSTS
// ================================================================
const ENV = {
  development: true,
  production: false,
};

const ecommercePaths = getAppSrcPaths('ecommerce');

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
        'front/js/vendors/shared/*.js',
      ],

      vendorsPages: [
        'front/js/vendors/*.js',
      ],

      common: [
        'front/js/shared/services/*.es6',
        ecommercePaths.backcall,
        'front/js/shared/*.es6',
      ],

      pages: [
        'front/js/*.es6',
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
    js: [
      'front/js/**/*',
      ecommercePaths.watch,
    ],
    images: 'front/src/images/**/*',
    fonts: 'front/src/fonts/**/*',
    html: 'templates/**/*',
  },
};

// ================================================================
// Build : Run all build tasks in production mode.
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
// Styles : Build all stylesheets.
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
// JS : Concat & minify vendor js.
// ================================================================
function vendorJS(source, destination, fileName) {
  gulp.src(source)
    .pipe($.changed(PATH.build.js, { extension: '.js' }))
    .pipe($.concat(`${fileName}.js`))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.uglify())
    .pipe(gulp.dest(destination));
}

function appJS(source, destination, fileName) {
  gulp.src(source)
    .pipe($.changed(destination, { extension: '.js' }))
    .pipe($.if(ENV.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.babel({
      presets: ['es2015'],
    }))
    .pipe($.concat(`${fileName}.js`))
    .pipe($.rename({
      suffix: '.min',
    }))
    .pipe($.if(ENV.production, $.uglify()))
    .pipe($.if(ENV.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(destination))
    .pipe($.livereload());
}

// ================================================================
// JS : Build common vendors js only.
// ================================================================
gulp.task('js-vendors', () => {
  vendorJS(PATH.src.js.vendors, PATH.build.js, 'vendors');
});

// ================================================================
// JS : Build common vendors js only for inner pages.
// ================================================================
gulp.task('js-vendors-pages', () => {
  vendorJS(PATH.src.js.vendorsPages, PATH.build.js, 'vendors-pages');
});

// ================================================================
// JS : Build common js.
// ================================================================
gulp.task('js-common', () => {
  appJS(PATH.src.js.common, PATH.build.js, 'main');
});

// ================================================================
// JS : Build js for all inner pages.
// ================================================================
gulp.task('js-pages', () => {
  appJS(PATH.src.js.pages, PATH.build.js, 'pages');
});

// ================================================================
// JS : Build js for admin page only.
// ================================================================
gulp.task('js-admin', () => {
  appJS(PATH.src.js.admin, PATH.build.js, 'admin');
});

// ================================================================
// Images : Copy images.
// ================================================================
gulp.task('images', () => {
  gulp.src(PATH.src.images)
    .pipe($.changed(PATH.build.images))
    .pipe(gulp.dest(PATH.build.images));
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
// Fonts : Copy fonts.
// ================================================================
gulp.task('fonts', () => {
  gulp.src(PATH.src.fonts)
    .pipe($.changed(PATH.build.fonts))
    .pipe(gulp.dest(PATH.build.fonts));
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
