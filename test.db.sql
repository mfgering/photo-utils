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
