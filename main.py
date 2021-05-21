from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email
import requests

app = Flask(__name__)


class EditForm(FlaskForm):
    rating = StringField(label='Rating out of 10 eg 7.5',
                         validators=[DataRequired()])
    review = StringField(label='Review', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


class AddForm(FlaskForm):
    movie_title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


app.secret_key = "any-string-you-want-just-keep-it-secret"

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-list.db'

db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String(500))
    ranking = db.Column(db.Integer)
    rating = db.Column(db.Float)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


db.create_all()

# ___________-------------Adding Entry------------___________________
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()


movie_url = "https://api.themoviedb.org/3/search/movie?"
API_KEY = "1dd7b54edaa9afc2261c739760328ddd"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


@app.route("/")
def home():
    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    edit_form = EditForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if edit_form.validate_on_submit():
        rating = float(edit_form.rating.data)
        review = edit_form.review.data
        movie.rating = rating
        movie.review = review
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", movie=movie, form=edit_form)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = AddForm()
    if add_form.validate_on_submit():
        movie_title = add_form.movie_title.data

        response = requests.get(movie_url, params={"api_key": API_KEY, "query": movie_title})

        data = response.json()
        option = data["results"]

        return render_template("select.html", movies=option)
    return render_template("add.html", form=add_form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        # The language parameter is optional, if you were making the website for a different audience
        # e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        img_url = f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}"
        print(img_url)
        print(data["title"])
        new_movie = Movie(
            id=data["id"],
            title=data["title"],
            # The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"],
            ranking= 2 ,
            rating= 3,
            review=""
        )
        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for('edit',id = movie_api_id))


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
