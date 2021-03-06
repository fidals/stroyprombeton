import autoprefixer from 'autoprefixer';
import babelPreset from 'babel-preset-es2015';
import csso from 'postcss-csso';
import del from 'del';
import gulp from 'gulp';
import mqpacker from 'css-mqpacker';
import sequence from 'run-sequence';

const $ = require('gulp-load-plugins')();
const flexibility = require('postcss-flexibility')();
const spawnSync = require('child_process').spawnSync;

// ================================================================
// Utils
// ================================================================
/**
 * Get src paths from given appName.
 * Usage:
 *   appPath = getAppSrcPath('pages');
 *
 *   const path = {
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
  const pythonPackagesPath = process.env.DEPS_DIR;
  return require(`${pythonPackagesPath}/${appName}/front/paths.js`);
}


// ================================================================
// CONSTS
// ================================================================
const env = {
  development: true,
  production: false,
};

const plugins = [
  autoprefixer(),
  csso(),
  mqpacker({
    sort: true,
  }),
];

const buildDir = 'front_build';
const ecommercePaths = getAppSrcPaths('ecommerce');
const genericAdminPaths = getAppSrcPaths('generic_admin');

const path = {
  src: {
    sprites: {
      main: 'front/images/spriteSrc/main/*.png',
      pages: 'front/images/spriteSrc/pages/*.png',
    },

    styles: {
      main: [
        'front/scss/styles.scss',
        'front/scss/pages.scss',
      ],

      admin: [
        ...genericAdminPaths.css,
      ],
    },

    js: {
      vendors: [
        'front/js/vendors/shared/jquery-2.2.4.min.js',
        'front/js/vendors/shared/jquery.mmenu.min.js',
        'front/js/vendors/shared/jquery.mask.min.js',
        'front/js/vendors/shared/autocomplete.min.js',
        'front/js/vendors/shared/cookie.js',
        'front/js/vendors/shared/tooltipster.bundle.min.js',
        'front/js/vendors/shared/jquery.photoswipe.min.js',
      ],

      common: [
        ecommercePaths.trackers,
        'front/js/shared/services/*.es6',
        ecommercePaths.backcall,
        'front/js/shared/*.es6',
      ],

      vendorsPages: [
        'front/js/vendors/slick.min.js',
        'front/js/vendors/featherlight.core.with.gallery.js',
        'front/js/vendors/jquery.kladr.min.js',
      ],

      pages: [
        'front/js/*.es6',
        '!front/js/admin.es6',
      ],

      vendorsAdmin: [
        ...genericAdminPaths.vendors,
      ],

      admin: [
        ...genericAdminPaths.admin,
        'front/js/admin.es6',
      ],

      vendorsIE: [
        'front/js/vendors/html5shiv.min.js',
        'front/js/vendors/flexibility.js',
      ],
    },

    images: [
      'front/images/**/*',
      '!front/images/spriteSrc{,/**}',
      genericAdminPaths.img,
    ],

    fonts: 'front/fonts/**/*',
  },

  build: {
    sprites: {
      pathInCss: '../images',
      img: `${buildDir}/images/`,
      scss: {
        main: 'front/scss/common/',
        pages: 'front/scss/pages/',
      },
    },
    styles: `${buildDir}/css/`,
    js: `${buildDir}/js/`,
    images: `${buildDir}/images/`,
    fonts: `${buildDir}/fonts/`,
  },

  watch: {
    styles: [
      'front/scss/**/*.scss',
      genericAdminPaths.watch.css,
    ],
    js: [
      'front/js/**/*',
      ecommercePaths.watch,
      ecommercePaths.trackers,
      genericAdminPaths.watch.js,
    ],
    images: 'front/images/**/*',
    fonts: 'front/fonts/**/*',
    html: 'templates/**/*',
  },
};

// ================================================================
// Build : Run all build tasks in production mode.
// ================================================================
gulp.task('build', () => {
  env.development = false;
  env.production = true;

  sequence(
    'clear', [
      'js-common',
      'js-common-vendors',
      'js-pages',
      'js-pages-vendors',
      'js-admin',
      'js-admin-vendors',
      'js-ie-vendors',
      'styles-main',
      'styles-admin',
      'styles-ie',
      'sprites',
      'fonts',
    ],
    'images',
  );
});

// ================================================================
// Clear : Clear destination dir before build.
// ================================================================
gulp.task('clear', () => del(`${buildDir}/**/*`, { force: true }));

// ================================================================
// Styles : Build all stylesheets.
// ================================================================
gulp.task('styles-main', () => {
  gulp.src(path.src.styles.main)
    .pipe($.changed(path.build.styles, { extension: '.css' }))
    .pipe($.if(env.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.sassGlob())
    .pipe($.sass())
    .pipe($.if(env.production, $.postcss(plugins)))
    .pipe($.rename({ suffix: '.min' }))
    .pipe($.if(env.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(path.build.styles))
    .pipe($.livereload());
});

gulp.task('styles-admin', () => {
  gulp.src(path.src.styles.admin)
    .pipe($.changed(path.build.styles, { extension: '.css' }))
    .pipe($.plumber())
    .pipe($.concat('admin.min.css'))
    .pipe($.if(env.production, $.postcss(plugins)))
    .pipe(gulp.dest(path.build.styles))
    .pipe($.livereload());
});

gulp.task('styles-ie', () => {
  gulp.src(path.src.styles.main)
    .pipe($.sassGlob())
    .pipe($.sass())
    .pipe($.concat('ie.min.css'))
    .pipe($.postcss([...plugins, flexibility]))
    .pipe(gulp.dest(path.build.styles));
});

// ================================================================
// JS : Concat & minify vendor js.
// ================================================================
function vendorJS(source, destination, fileName) {
  gulp.src(source)
    .pipe($.changed(path.build.js, { extension: '.js' }))
    .pipe($.concat(`${fileName}.js`))
    .pipe($.rename({ suffix: '.min' }))
    .pipe($.uglify({ mangle: { reserved: ['ga'] } }))
    .pipe(gulp.dest(destination));
}

function appJS(source, destination, fileName) {
  gulp.src(source)
    .pipe($.changed(destination, { extension: '.js' }))
    .pipe($.if(env.development, $.sourcemaps.init()))
    .pipe($.plumber())
    .pipe($.concat(`${fileName}.js`))
    .pipe($.babel({
      presets: [babelPreset],
      compact: false,
    }))
    .pipe($.rename({ suffix: '.min' }))
    .pipe($.if(
      env.production,
      $.uglify({
        mangle: { reserved: ['ga'] },
      })
    ))
    .pipe($.if(env.development, $.sourcemaps.write('.')))
    .pipe(gulp.dest(destination))
    .pipe($.livereload());
}

// ================================================================
// JS : Build common js.
// ================================================================
gulp.task('js-common', () => {
  appJS(path.src.js.common, path.build.js, 'main');
});

// ================================================================
// JS : Build common vendors js only.
// ================================================================
gulp.task('js-common-vendors', () => {
  vendorJS(path.src.js.vendors, path.build.js, 'main-vendors');
});

// ================================================================
// JS : Build js for all inner pages.
// ================================================================
gulp.task('js-pages', () => {
  appJS(path.src.js.pages, path.build.js, 'pages');
});

// ================================================================
// JS : Build common vendors js only for inner pages.
// ================================================================
gulp.task('js-pages-vendors', () => {
  vendorJS(path.src.js.vendorsPages, path.build.js, 'pages-vendors');
});

// ================================================================
// JS : Build js for admin page only.
// ================================================================
gulp.task('js-admin', () => {
  appJS(path.src.js.admin, path.build.js, 'admin');
});

// ================================================================
// JS : Build admin vendors js only
// ================================================================
gulp.task('js-admin-vendors', () => {
  vendorJS(path.src.js.vendorsAdmin, path.build.js, 'admin-vendors');
});

// ================================================================
// JS : Build vendors js for IE
// ================================================================
gulp.task('js-ie-vendors', () => {
  vendorJS(path.src.js.vendorsIE, path.build.js, 'ie-vendors');
});

// ================================================================
// Images: Sprites.
// ================================================================
gulp.task('sprites', () => {
  let spriteData = gulp.src(path.src.sprites.main)
    .pipe($.spritesmith({
      imgName: 'sprite-main.png',
      cssName: 'sprite-main.css',
      imgPath: `${path.build.sprites.pathInCss}/sprite-main.png`,
    }));

  spriteData.img.pipe(gulp.dest(path.build.sprites.img));

  spriteData.css
    .pipe($.rename({ extname: '.scss' }))
    .pipe(gulp.dest(path.build.sprites.scss.main));

  spriteData = gulp.src(path.src.sprites.pages)
    .pipe($.spritesmith({
      imgName: 'sprite-pages.png',
      cssName: 'sprite-pages.css',
      imgPath: `${path.build.sprites.pathInCss}/sprite-pages.png`,
    }));

  spriteData.img.pipe(gulp.dest(path.build.sprites.img));

  spriteData.css
    .pipe($.rename({ extname: '.scss' }))
    .pipe(gulp.dest(path.build.sprites.scss.pages));
});

// ================================================================
// Images : Optimize and copy images.
// ================================================================
gulp.task('images', () => {
  gulp.src(path.src.images)
    .pipe($.imagemin())
    .pipe(gulp.dest(path.build.images));
});

// ================================================================
// Fonts : Copy fonts.
// ================================================================
gulp.task('fonts', () => {
  gulp.src(path.src.fonts)
    .pipe($.changed(path.build.fonts))
    .pipe(gulp.dest(path.build.fonts));
});

// ================================================================
// WATCH
// ================================================================
gulp.task('watch', () => {
  $.livereload.listen();
  gulp.watch(path.watch.styles, [
    'styles-main',
    'styles-admin',
  ]);
  gulp.watch(path.watch.js, [
    'js-common',
    'js-pages',
    'js-admin',
  ]);
  gulp.watch(path.watch.images, ['images']);
  gulp.watch(path.watch.fonts, ['fonts']);
  gulp.watch(path.watch.html, $.livereload.changed);
});

// ================================================================
// DEFAULT
// ================================================================
gulp.task('default', ['watch']);
