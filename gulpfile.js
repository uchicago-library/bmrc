"use strict";

var gulp = require('gulp');
var sass = require('gulp-sass');
var maps = require('gulp-sourcemaps');
var browserSync = require('browser-sync').create();


//Compile Sass to css
gulp.task('compileSass', function() {
	return gulp.src(['scss/**/*.scss'])
		.pipe(maps.init()) // Sass source map 1/2
		.pipe(sass())
		.pipe(maps.write('./')) // Sass source map 2/2
		.pipe(gulp.dest('css'))
	.pipe(browserSync.reload({
      stream: true
    }))
});

// Watch Files
gulp.task('watchFiles', ['browserSync', 'compileSass'], function() {
	gulp.watch('scss/**/*.scss', ['compileSass']);
	gulp.watch('*.html', browserSync.reload);
});

// Load and refresh on local
gulp.task('browserSync', function() {
  browserSync.init({
    server: {
      baseDir: './'
    },
  })
})


//gulp.task('serve', ['watchFiles']);

gulp.task("build", ['compileSass', 'watchFiles']);

gulp.task("default", ['build']);