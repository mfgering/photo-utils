import sqlite3

def make_schema(cursor):
	stmt = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `p_encoding` (
	`image_id`	INTEGER NOT NULL,
	`encoding`	BLOB NOT NULL,
	PRIMARY KEY(`image_id`),
	FOREIGN KEY(`image_id`) REFERENCES `image_info`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS `image_info` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`path`	TEXT NOT NULL,
	`filename`	TEXT NOT NULL,
	`filesize`	INTEGER,
	`md5`	INTEGER
);
CREATE INDEX IF NOT EXISTS `image_pk` ON `image_info` (
	`path`,
	`filename`
);
COMMIT;
"""
	result = cursor.executescript(stmt)
	print(stmt)

def main():
	#conn = sqlite3.connect(':memory:')
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	make_schema(c)
	conn.commit()
	conn.close()	

if __name__ == '__main__':
	main()