-- Create the posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    upvotes INTEGER DEFAULT 0,
    title TEXT NOT NULL,
    link TEXT,
    username TEXT NOT NULL
);

-- Create the comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    upvotes INTEGER DEFAULT 0,
    text TEXT NOT NULL,
    username TEXT NOT NULL
);
