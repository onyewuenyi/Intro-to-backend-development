CREATE TABLE users(
-- 	Potential scaling issue: SERIAL ties the ID generation to the database instance, which could lead to conflicts if you replicate databases globally.
--  Suggestion: Consider using a globally unique identifier (e.g., UUID) to avoid conflicts. Postgres has a built-in extension for this:
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	name text not null check(char_length(name) <= 255), 
	username text not null unique,
	balance numeric(12, 2) default 0,
	updated_at timestamp default CURRENT_TIMESTAMP,
	created_at date default CURRENT_TIMESTAMP,
	deleted_at TIMESTAMP DEFAULT NULL
);

-- Keeps your application logic clean by offloading timestamp management to the database.
-- The trigger for updated_at and deleted_at automates the management of timestamps in your database, which is critical for maintaining accurate records of when rows are modified or soft-deleted. 

-- Update `updated_at` on UPDATE
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Soft delete by setting `deleted_at` on DELETE
CREATE OR REPLACE FUNCTION set_deleted_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER soft_delete
BEFORE DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION set_deleted_at();


