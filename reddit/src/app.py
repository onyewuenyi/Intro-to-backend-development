import psycopg2
from flask import Flask, jsonify, request, g
from functools import wraps


app = Flask(__name__)

# Database connection details
# I needed to use localhost instead of host.docker.internal
DB_HOST = "localhost"  # e.g., 'localhost', 'host.docker.internal', or remote host IP
DB_NAME = "postgres" # this is the default name
DB_PORT = "55002" # you can specify a pport
DB_USER = "postgres"
DB_PASSWORD = "postgrespw"



def with_db_connection(f):
    """
    Managing the database connection correctly, including handling rollbacks on exceptions
    automatically commit after successful execution
    handles conn.commit() upon successful execution and performs conn.rollback() 
    in case of an error, if the update fails for any reason (e.g., a database error or invalid comment_id), 
    the decorator would automatically roll back the transaction. 
    This should prevent any partial or unintended updates from persisting in the database.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Could not connect to the database'}), 500
        cursor = conn.cursor()
        try:
            response = f(cursor, *args, **kwargs)
            conn.commit()  
            return response
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    return decorated_function


# Function to establish a database connection
def get_db_connection():
    """
    Summary of Usage
    Purpose: The primary purpose of get_db_connection() is to ensure that each request handler can access a valid database connection without repeatedly creating and closing connections unnecessarily.
    Connection Management: By using Flask’s g, the function manages the connection lifecycle effectively, creating a new connection only when needed and ensuring it is associated with the current request.
    Benefits
    Efficiency: This approach avoids the overhead of establishing a connection on every request, as it reuses the connection if it already exists.
    Thread Safety: The use of g ensures that connections are not shared between different requests, thus preventing potential concurrency issues.
    Simplified Code: Request handlers can focus on their logic without worrying about managing database connections directly.
    """
    # Check if a connection is already set for the current request
    if 'conn' not in g:
        try:
            g.conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
        except psycopg2.OperationalError as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            return None
    return g.conn


@app.teardown_appcontext
def close_db_connection(exception):
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/api/posts/', methods=['GET'])
@with_db_connection
def get_all_post(cursor):
    # APItoDBinterface(sql) 
    # ex http req over the network to the database 
    cursor.execute('''SELECT p.id, p.upvotes, p.title, p.link, p.username, 
                             c.id, c.upvotes, c.text, c.username 
                   FROM posts as p 
	            LEFT JOIN comments c ON p.id = c.post_id''')
    rows = cursor.fetchall()
    if not rows:
        return jsonify({"error": "No post not found"}), 404

    posts_dict = {}
    for row in rows:
        post_id = row[0]
        # Check if post is already in dictionary, if not, add it
        if post_id not in posts_dict:
            posts_dict[post_id] = {
                "id": post_id,
                "upvotes": row[1],
                "title": row[2],
                "link": row[3],
                "username": row[4],
                "comments": []
            }
        
        # If comment exists, add it to the post's comments
        if row[5]:  # row[5] is comment_id, only add if comment is present
            comment = {
                "id": row[5],
                "upvotes": row[6],
                "text": row[7],
                "username": row[8]
            }
            posts_dict[post_id]["comments"].append(comment)

    # Format the output to match the expected structure
    post_data = {
        "posts": list(posts_dict.values())
    }   

    # Return the JSON response with HTTP status code 200
    return jsonify(post_data), 200
    

@app.route('/api/posts/', methods=['POST'])
@with_db_connection
def create_post(cursor):
    # Get the payload, Content-Type: application/json, data from the http res body
    post_data = request.get_json()    
    title, username, link = post_data.get('title').strip(), post_data.get('username').strip(), post_data.get('link').strip()
    if not title or not username or not link:
        return jsonify({"error": "Title, link, username are required"}), 400
    
    
    # Create new post using SQL ane psycopg2 driver, which allows a prog lang to comm with N database 
    cursor.execute('''INSERT INTO posts (title, link, username) 
                    VALUES (%s, %s, %s) RETURNING id, upvotes''', (title, link, username))
    
    new_post_data = cursor.fetchone() 
     # Check if new_post_data has the expected length
    if new_post_data is None or len(new_post_data) < 2:
        return jsonify({"error": "Failed to create post, no data returned"}), 500

    new_post_id = new_post_data[0] # Get the ID of the newly created post
    new_post_upvotes = new_post_data[1] # Get the upvotes of the newly created post


    # Return res
    return jsonify({  # auto set the http header Content-Type: application/json and Content-Length
        "post" : {
            "id": new_post_id,
            "upvotes": new_post_upvotes,
            "title": title,
            "username": username,
            "link": link 
        }
    }) , 201


@app.route('/api/posts/<int:post_id>', methods=['GET'])
@with_db_connection
def get_post(cursor, post_id):
    cursor.execute('''SELECT p.id, p.upvotes, p.title, p.link, p.username, 
                         c.id, c.upvotes, c.text, c.username 
                  FROM posts as p  -- Corrected table name to "posts"
                  LEFT JOIN comments c ON p.id = c.post_id 
                  WHERE p.id = %s;''', (post_id,))  # post_id passed as a tuple
         
    rows = cursor.fetchall() # retrieves all the matching rows from the query.
    if not rows:
        return jsonify({"error": f"No post not found with id = {post_id}"}), 404

    posts_dict = {}
    for row in rows:
        post_id = row[0]
        # Check if post is already in dictionary, if not, add it
        if post_id not in posts_dict:
            posts_dict[post_id] = {
                "id": post_id,
                "upvotes": row[1],
                "title": row[2],
                "link": row[3],
                "username": row[4],
                "comments": []
            }
        
        # If comment exists, add it to the post's comments
        if row[5]:  # row[5] is comment_id, only add if comment is present
            comment = {
                "id": row[5],
                "upvotes": row[6],
                "text": row[7],
                "username": row[8]
            }
            posts_dict[post_id]["comments"].append(comment)

    # Format the output to match the expected structure
    post_data = {
        "posts": list(posts_dict.values())
    }   

    # Return the JSON response with HTTP status code 200
    return jsonify(post_data), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@with_db_connection
def delete_post(cursor, post_id):
    cursor.execute('''DELETE from posts WHERE id = %s;''', (post_id))

    # Check if a row was actually deleted
    if cursor.rowcount == 0:
        return jsonify({"error": "Post not found"}), 404

    return jsonify({"message": "Order deleted successfully"}), 200
 

# Get comments for a specific post 
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
@with_db_connection
def get_comments_for_post(cursor, post_id): 
    cursor.execute('''SELECT * from comments WHERE post_id = %s''', (post_id,))

    rows = cursor.fetchall()
    if not rows:
        return jsonify({"error": f"No comments with post_id = {post_id}"}), 404

    # Transform res payload data to send in req. Is three an abstraction to handle this.
    comments_data = []
    for row in rows:
        comment = {
            "id":row[0],
            "post_id":row[1],
            "upvotes":row[2],
            "text": row[3],
            "username": row[4]
        }
        comments_data.append(comment)
    return jsonify(comments_data), 200
 

# Post comment for specifc Post 
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@with_db_connection
def post_comment(cursor, post_id):
    comment_post_data = request.get_json() 
    text, username = comment_post_data.get('text'), comment_post_data.get('username') 
    if not text or not username:
        return jsonify({"error": "Text, or username field not provided"}), 400
    
    # sql query to create a comment for the given post_id and return the newely created comment id
    cursor.execute('''INSERT INTO comments (post_id, text, username) VALUES (%s, %s, %s) RETURNING id''', (post_id, text, username,))
    new_comment_id = cursor.fetchone()[0]
    if new_comment_id:
        return jsonify({
                "id": new_comment_id,
                "post_id": post_id,
                "upvotes": 0,
                "text": text,
                "username": username
        }), 201
    else:
        return jsonify({"error": "Failed to create comment."}), 500


# Edit Comment for specific Post 
@app.route('/api/posts/<int:post_id>/comments/<int:comments_id>', methods=['PUT'])
@with_db_connection
def edit_comment(cursor, post_id, comments_id):
    # Get payload fields
    comment_data = request.get_json()
    text = comment_data.get("text")
    if not text:
        return jsonify({"error" : "Text fields are required"})

    # sql query with return statement 
    cursor.execute(
        '''UPDATE comments 
        SET text = %s
        WHERE post_id = %s and id = %s
        RETURNING id, post_id, text, username, upvotes''', 
        (text, post_id, comments_id)
    )

    updated_comments = cursor.fetchone()
    if updated_comments:
        return jsonify({
            "id": updated_comments[0],
            "post_id": updated_comments[1],
            "text": updated_comments[2],
            "username": updated_comments[3],
            "upvotes": updated_comments[4]
        }), 200
    else:
        return jsonify({"error": "Comment not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

