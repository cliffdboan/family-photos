# Alright!
Let's get to it. This is Family Photos.
This is my final project for Harvard Extension's CSCI-E 50.

Utilizing Flask, python, and some JS/HTML/CSS, this is a website that allows users to
register an account, upload and view photos in groups of albums.

The project is fairly straightforward to run, but there are a number of dependencies
needed to run it. You'll need to install `flask`, `sqlalchemy`, `flask_session`,
and `werkzeug`.

You'll also need a sqlite database, which, right now, is fairly simple. There's a users table, which holds an id, username, email,
and a password hash. Then there's an albums table which holds
an album id, the user id, and the album name. Finally, a photos table
which holds ids for the photo, user, and album (referencing the photo album id),
an image link to retrieve the photo, a caption, whether the image is deleted,
and if the photo is the album's cover or not.

The images are uploaded using a post method that uploads the image
and stores it in an uploads folder within the static folder. The
links to the photos are stored in the database, and called upon within each webpage. When deleted, the image is not removed, but
the image is no longer rendered on the webpage. Not great, but it sort of works.

In terms of running the project, as long as the dependencies are within the project, all you need to do is `flask run`!
