import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    try:
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        return connection
    except Exception as e:
        raise Exception("Unable to establish db connection: %s" %e)

# Function to get a post using its ID
def get_post(post_id):
    try:
        connection = get_db_connection()
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                            (post_id,)).fetchone()
        connection.close()
        return post
    except Exception as e:
        raise Exception("Unable to get posts: %s" %e)

def get_posts_count():
    try:
        connection = get_db_connection()
        posts_count = connection.execute('SELECT COUNT(*) FROM posts;').fetchone()[0]
        connection.close()
        return posts_count
    except Exception as e:
        raise Exception("Unable to get posts: %s" %e)

def get_db_connection_count():
    try:
        connection = get_db_connection()
        connection_count = connection.execute("SELECT 1").fetchall()[0][0]
        connection.close()
        return connection_count
    except Exception as e:
        raise Exception("Unable to get db connection count: %s" %e)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    return response

@app.route('/metrics')
def metrics():
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": get_db_connection_count(),"post_count":get_posts_count()}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Metrics request successfull')
    return response

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

def main():
    logging.basicConfig(filename='app.log', format='%(asctime)s - %(message)s', level=logging.INFO)
    app.run(host='0.0.0.0', port=3111)


if __name__ == "__main__":
    main()
