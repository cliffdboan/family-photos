import os
from sqlalchemy import create_engine, MetaData, Table, delete, update, insert, select # type: ignore
from sqlalchemy.orm.exc import NoResultFound # type: ignore

from flask import Flask, flash, redirect, render_template, request, session # type: ignore
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from config import DATABASE_URL, SECRET_KEY

# Base app setup and configuration used from CS50's Finance problem

# configure application
app = Flask(__name__)

UPLOAD_FOLDER = "./static/uploads"
FILE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]

# use filesystem instead of assigned cookies
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
Session(app)

# connect and configure database
engine = create_engine(DATABASE_URL, echo=True)
metadata_obj = MetaData()

user_table = Table(
    "users",
    metadata_obj,
    autoload_with=engine,
)

album_table = Table(
    "albums",
    metadata_obj,
    autoload_with=engine,
)

photo_table = Table(
    "photos",
    metadata_obj,
    autoload_with=engine,
)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/add_to_album/int<album_id>/<int:img_id>")
def add_to_album(album_id, img_id):
    """Add photo to album"""
    # redirect to login page if not logged in
    if not "user_id" in session:
        flash("Please login to add photos to albums", "primary")
        return redirect("/login")

    # open the database
    with engine.begin() as conn:
        # check if the album exists. if not, create it and add to album

        # update the photo table
        conn.execute(update(photo_table).where(
            photo_table.c.photo_id == img_id
        ).values(
            photo_album_id = album_id
        ))

    return redirect(f"/albums")

@app.route("/")
def index():
    """Show albums if logged in, otherwise, show login page"""
    if "user_id" in session:
        return redirect("/photos")
    else:
        return redirect("/login")

@app.route("/albums")
def albums():
    """Display clickable albums"""
    # redirect to login page if not logged in
    if not "user_id" in session:
        flash("Please login to view albums", "primary")
        return redirect("/login")

    album_covers = []
    album_names = []

    # open the database
    with engine.begin() as conn:
        # get the cover images for each album
        covers_sql = select(photo_table).where(
            photo_table.c.user_id == session["user_id"],
            photo_table.c.deleted == "false",
            photo_table.c.album_cover == "true"
        )
        images = conn.execute(covers_sql)
        for img in images:
            album_covers.append(img)

        # get the names of each album and add them to the list
        for album in album_covers:
            name_objects = conn.execute(
                select(album_table.c.album_name).where(
                    album_table.c.album_id == album.photo_album_id
                )
            )
            for name in name_objects:
                album_names.append(name[0])

    # zip the lists together for pairing when rendering
    album_pairs = zip(album_covers, album_names)

    return render_template("albums.html", album_pairs=album_pairs)

@app.route("/albums/<album_name>")
def album(album_name):
    """Show photos in album"""
    # redirect to login page if not logged in
    if not "user_id" in session:
        flash("Please login to view albums", "primary")
        return redirect("/login")

    # open db
    with engine.begin() as conn:
        # get the album info
        album_info = conn.execute(select(album_table).where(
            album_table.c.user_id == session["user_id"],
            album_table.c.album_name == album_name
        ))
        for info in album_info:
            album_id = info.album_id
            name = info.album_name

        # get photos from that album
        photos_obj = conn.execute(select(photo_table).where(
            photo_table.c.user_id == session["user_id"],
            photo_table.c.deleted == "false",
            photo_table.c.photo_album_id == album_id
        ))

    # render template
    return render_template("album.html", content=photos_obj, album_name=name)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    """Delete photo"""
    # redirect to login page if not logged in
    if not "user_id" in session:
        flash("Please login to delete photos", "primary")
        return redirect("/login")

    # TODO: This is temporary, will be replaced with a hard delete.
    # There was an issue with using "delete(photo_table)....." where engine.begin would happen 10 times and break.

    # delete image info from database
    with engine.begin() as conn:
        sql = update(photo_table).where(
            photo_table.c.photo_id == id,
            photo_table.c.user_id == session["user_id"]
            ).values(deleted = "True")
        conn.execute(sql)

    # flash successful message and redirect home
    flash("Image deleted", "success")
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    if request.method == "POST":
        # if user is already logged in, redirect to homepage
        if "user_id" in session:
            flash("Already logged in", "primary")
            return redirect("/")

        username = request.form.get("username")
        password = request.form.get("password")

        # validate both inputs are used
        if not username:
            flash("Must provide username", "danger")
            return redirect("/login")
        if not password:
            flash("Must provide password", "danger")
            return redirect("/login")

        # log user in
        with engine.begin() as conn:
            query = select(user_table).where(user_table.c.username == username.lower())
            rows = conn.execute(query)

            # check username and password
            try:
                row = rows.one()
                if not check_password_hash(row[3], password):
                    flash("Incorrect password, please try again", "danger")
                    return redirect("/login")
                else:
                    session["user_id"] = row[0]
                    flash("Logged in successfully", "success")
                    return redirect("/")
            except NoResultFound:
                flash("Incorrect username, please try again", "danger")
                return redirect("/login")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # forget any user_id
    session.clear()

    # redirect user to homepage
    flash("Logged out successfully", "success")
    return redirect("/")

@app.route("/photos")
def photos():
    """Show all photos"""
    # if user is not logged in, redirect to login page
    if not session["user_id"]:
        flash("Please login to view photos", "primary")
        return redirect("/login")

    # query database for photos
    with engine.begin() as conn:
        sql = select(photo_table).where(photo_table.c.user_id == session["user_id"])
        rows = conn.execute(sql)

    # render template
    return render_template("photos.html", pictures=rows)

@app.route("/photo/<int:photo_id>")
def photo(photo_id):
    """Show photo"""
    # if user is not logged in, redirect to login page
    if not session["user_id"]:
        flash("Please login to view photos", "primary")
        return redirect("/login")

    # open SQL database
    with engine.begin() as conn:
        # get album names for dropdown menu selection
        albums = []
        for row in conn.execute(select(album_table.c.album_name).where(
            album_table.c.user_id == session["user_id"]
            )):
            albums.append(row[0])

        # get photo info
        sql = select(photo_table).where(
            photo_table.c.photo_id == photo_id,
            photo_table.c.user_id == session["user_id"]
            )
        rows = conn.execute(sql)
        result = rows.fetchone()

        if result:
            return render_template("photo.html", image=result, albums=albums)
        else:
            flash("Error retrieving image", "warning")
            return redirect("/photos")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user"""
    # if user is logged in, redirect to homepage
    if "user_id" in session:
        flash("Already logged in", "primary")
        return redirect("/")

    # TODO: imporove validation
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirm")

        if not username:
            flash("Must provide username", "warning")
            return redirect("/register")
        if not email:
            flash("Must provide email", "warning")
            return redirect("/register")
        if not password:
            flash("Must provide password", "warning")
            return redirect("/register")
        if not confirmation:
            flash("Must confirm password", "warning")
            return redirect("/register")
        if password != confirmation:
            flash("Passwords do not match", "warning")
            return redirect("/register")

        # hash password
        hash = generate_password_hash(
            password, method="scrypt", salt_length=16)

        # begin engine
        with engine.begin() as conn:
        #     # check if username or email are already in use
        #     ### i thought about using a SQL OR statement, but i wanted to give better
        #     ### feedback to the user than just a generic error message
            usr_sql = select(user_table).where(user_table.c.username == username.lower())
            email_sql = select(user_table).where(user_table.c.email == email)

            for row in conn.execute(usr_sql):
                user_check = True
                if user_check:
                    flash("Username is taken!", "warning")
                    return redirect("/register")

            for row in conn.execute(email_sql):
                email_check = True
                if email_check:
                    flash("Email already in use!", "warning")
                    return redirect("/register")

            # insert new user's information into database
            sql = insert(user_table).values(username=username.lower(), hash=hash, email=email)
            conn.execute(sql)

            # keep user logged in
            for row in conn.execute(select(user_table.c.id).where(user_table.c.username == username.lower())):
                session["user_id"] = row.id
            return redirect("/")

    else:
        return render_template("register.html")

@app.route("/set_cover/<int:album_id>/<int:photo_id>", methods=["POST"])
def set_cover(photo_id, album_id):
    """Set album cover for selected photo"""
    # if user is not logged in, redirect to login page
    if not session["user_id"]:
        flash("Please login to set album cover", "primary")
        return redirect("/login")

    # open database
    with engine.begin() as conn:
        # set current album cover image to false
        sql = update(photo_table).where(
            photo_table.c.user_id == session["user_id"],
            photo_table.c.album_cover == "true",
            photo_table.c.photo_album_id == album_id
            ).values(album_cover = "false")
        conn.execute(sql)

        # set selected photo's album cover to true
        sql = update(photo_table).where(
            photo_table.c.photo_id == photo_id,
            photo_table.c.user_id == session["user_id"]
            ).values(album_cover = "true")
        conn.execute(sql)

        # redirect to album page
        flash("Album cover set", "success")
        return redirect(f"/albums")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload a photo"""
    # if user is not logged in, redirect to login page
    if not session["user_id"]:
        flash("Please login to upload", "primary")
        return redirect("/login")

    # https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in FILE_EXTENSIONS

    if request.method == "POST":
        # if an option is selected, get its value, otherwise get value from input
        caption = request.form.get("caption")
        if request.form.get("dropdown") == "new album":
            album = request.form.get("album")
        else:
            album = request.form.get("dropdown")

        cover = request.form.get("set_cover")
        if cover == None:
            cover = "false"

        # if no file, flash error
        if 'file' not in request.files:
            flash("No file part", "danger")
            return redirect("/upload")

        # get file and save it to static uploads
        file = request.files["file"]

        if file.filename == "":
            flash("No file selected", "warning")
            return redirect("/upload")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            # add the image file path to the database
            with engine.begin() as conn:
                album_id = None
                # get the album id for the selected album, if it exists
                check_album_sql = select(album_table.c.album_id).where(
                    album_table.c.user_id == session["user_id"],
                    album_table.c.album_name == album
                    )
                check_albums = conn.execute(check_album_sql)
                result = check_albums.fetchone()

                    # if album exists, get and set album id
                if result:
                    album_id = result[0]

                else:
                # if album does not exist, create it and add to table
                    conn.execute(insert(album_table).values(
                        user_id=session["user_id"],
                        album_name=album
                        ))
                    new_album = conn.execute(select(album_table.c.album_id).where(
                        album_table.c.user_id == session["user_id"],
                        album_table.c.album_name == album
                        ))
                    # get and set the id for the new album
                    for col in new_album:
                        album_id = col[0]

                # check if the photo will replace another cover photo, and set it to false
                if cover == "true":
                    conn.execute(update(photo_table).where(
                        photo_table.c.user_id == session["user_id"],
                        photo_table.c.photo_album_id == album_id,
                        ).values(album_cover = "false"))

                # add photo to database
                photo_sql = insert(photo_table).values(
                    user_id=session["user_id"],
                    image_link=os.path.join(UPLOAD_FOLDER, filename),
                    caption=caption,
                    photo_album_id=album_id,
                    album_cover=cover
                    )

                conn.execute(photo_sql)

        return redirect("/")
    else:
        album_names = []
        with engine.begin() as conn:
            for row in conn.execute(select(album_table.c.album_name).where(
                album_table.c.user_id == session["user_id"]
                )):
                    album_names.append(row[0])
        return render_template("upload.html", albums=album_names)
