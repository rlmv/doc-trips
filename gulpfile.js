

gulp = require('gulp')
gulpBower = require('gulp-bower')
gulpBowerFiles = require('gulp-bower-files')

gulp.task('bower', function() {
    return gulpBower()
});

gulp.task('bower-files', function() {

});

gulp.task('default', ['bower', 'bower-files']);
