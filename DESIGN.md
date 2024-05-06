# DESIGN
# On Start
When a user first navigates to the webpage, they'll see a login form.
Since this is their first time, they'll have to navigate to the Register link
and set up an account. After registration, they'll be redirected to an upload page
where they can upload their first image. From there they can view albums, or all of their uploaded images.
If they click on their image, they can delete the image, set it as the album cover, or
set a caption for the image.

# Data Handling
The database schema is described in the README, but it's user data, image data (including
the link to access the image), and photo album data.

# Technical Design
This project utilizes Python, Flask, SQL, and some JS/HTML/CSS. Each flask route first checks
if the user id is in the flask session. This is to ensure a user is never where they shouldn't be.
Before getting into the valid routes, there is a 404 error route that directs users to
a 404 page that can guide them to the rest of the site. Much of the routes are full of
SQL queries, using SQLAlchemy. First the app connects to the engine (language and db route specified in `config.py`).
In each route, the app connects to the 'engine',
runs its query, then finishes its transaction and closes the engine (temporarily).

The uploads currently go into /static/uploads/... where they are stored and linked to for visual display
as `img src` links. It doesn't seem like the optimal solution, but seemed better than storing the images
as BLOB objects within the SQL database itself.
