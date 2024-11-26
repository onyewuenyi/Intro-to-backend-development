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
                port=DB_PORT,
                # returns a list of dicts. This simplifies code of man mapping, converting each row into a dict,
                # auto ensures that the correct mapping of col names to vals 
                cursor_factory=psycopg2.extras.DictCursor
            )
        except psycopg2.OperationalError as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            return None
    return g.conn



@app.route('/api/users', methods=['GET'])
@with_db_connection
def get_users(cursor):
    cursor.execute('''SELECT * from users WHERE deleted_at IS NULL''')
    # cursor.fetchall() with DictCursor already returns a list of dictionarie
    users = cursor.fetchall()
    # auto serialization for jsonify can directly handle the list of dicts returned by fetchall()
    # It takes Python data structures and converts them into a JSON-formatted HTTP response 
    # with the appropriate Content-Type header set to application/json
    return jsonify(users), 200

"""
Add optional query parameters with a default 
Update db query to use limit and offset 
"""
@app.route('/api/users', methods=['GET'])
@with_db_connection
def get_users(cursor):
    default_page_size = 5 
    default_page_number = 1 # 1-based indexing for user-friendliness

    # Get query parameters 
    try:
        page_size = int(request.args.get('pageSize', default_page_size))
        page_number = int(request.args.get('pageNumber', default_page_number))
        if page_size <= 0 or page_number <= 0:
            raise ValueError("pageSize and pageNumber must be positive integers")
    except ValueError as e:
        return jsonify({"error": "Invalid pagination parameters"}), 400
    
    offset = (page_number - 1) * page_size



    cursor.execute('''SELECT * from users WHERE deleted_at IS NULL LIMIT %s OFFSET %s''', (page_size, offset))
    # cursor.fetchall() with DictCursor already returns a list of dictionarie
    users = cursor.fetchall()
    cursor.execute('SELCT COUNT(*) FROM users WHERE deleted_at IS NULL')

    total_records = cursor.fetchone()['count']

    res = {
        "data": users,
        "pagination": {
            "pageNumber": page_number,
            "pageSize": page_size,
            "totalRecords": total_records
        }
    }
    # auto serialization for jsonify can directly handle the list of dicts returned by fetchall()
    # It takes Python data structures and converts them into a JSON-formatted HTTP response 
    # with the appropriate Content-Type header set to application/json
    return jsonify(res), 200
    





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

