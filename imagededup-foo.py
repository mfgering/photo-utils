from imagededup.methods import PHash
import contextlib, hashlib, logging, os, sqlite3

class DeDupe(object):
    def __init__(self):
        self.init_db()
        self.p_hasher = PHash()

    def __del__(self):
        self.close_db()

    def init_db(self):
        self.db_conn = sqlite3.connect('imagededup.db')
        #self.cursor = self.db_conn.cursor()
        self.make_schema()
        #self.db_conn.commit()
        #self.db_conn.close()	

    def close_db(self):
        if self.db_conn is not None:
            self.db_conn.close()
            self.db_conn = None

    def make_schema(self):
        stmt = """
    BEGIN TRANSACTION;
    CREATE TABLE IF NOT EXISTS `p_encoding` (
        `image_id`	INTEGER NOT NULL,
        `encoding`	TEXT NOT NULL,
        PRIMARY KEY(`image_id`),
        FOREIGN KEY(`image_id`) REFERENCES `image_info`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
    );
    CREATE TABLE IF NOT EXISTS `image_info` (
        `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `path`	TEXT NOT NULL,
        `filename`	TEXT NOT NULL,
        `filesize`	INTEGER,
        `md5`	BLOB
    );
    CREATE INDEX IF NOT EXISTS `image_pk` ON `image_info` (
        `path`,
        `filename`
    );
    COMMIT;
    """
        result = self.db_conn.executescript(stmt)

    def encode_dir(self, target, replace = True):
        if os.path.isdir(target):
            for dir_name, _, file_list in os.walk(target):
                for fn in file_list:
                    self.encode_file(dir_name, fn, replace)
        else:
            logging.logger().error("Target '%s' is not a directory", target)
    
    def encode_file(self, dir_name, fn, replace=True):
        fn_full = os.path.join(dir_name, fn)
        with contextlib.closing(self.db_conn.cursor()) as cursor:
            if os.path.isfile(fn_full):
                image_id = None
                is_different = True
                stat_info = os.stat(fn_full)
                with open(fn_full, 'rb') as image_file:
                    buff = image_file.read()
                    md5_hasher = hashlib.md5()
                    md5_hasher.update(buff)
                    digest = md5_hasher.digest()
                cursor.execute("SELECT * FROM image_info i where i.filename = ? and i.path = ?", (fn, dir_name))
                r = cursor.fetchone()
                if r is not None:
                    image_id, _, _, filesize, md5 = r
                    is_different = stat_info.st_size != filesize or digest != md5
                if is_different or replace:
                    # insert or update image_info
                    stmt = '''REPLACE INTO image_info(id, path, filename, filesize, md5)
                                VALUES(?, ?, ?, ?, ?)'''
                    result = cursor.execute(stmt, (image_id, dir_name, fn, stat_info.st_size, digest))
                    image_id = result.lastrowid                  
                    # insert or update p_encoding
                    encoding = self.p_hasher.encode_image(fn_full)
                    stmt = '''REPLACE INTO p_encoding (image_id, encoding)
                                VALUES(?, ?)'''
                    result = cursor.execute(stmt, (image_id, encoding))
                    self.db_conn.commit()


    def foo(self):
        self.encode_dir('images-dedup', replace=True)
        return
        phasher = PHash()

        # Generate encodings for all images in an image directory
        encodings = phasher.encode_images(image_dir='images-dedup')

        # Find duplicates using the generated encodings
        duplicates = phasher.find_duplicates(encoding_map=encodings)

        # plot duplicates obtained for a given file using the duplicates dictionary
        from imagededup.utils import plot_duplicates
        plot_duplicates(image_dir='images-dedup',
                        duplicate_map=duplicates,
                        filename='dog.jpg')

def main():
    dedupe = DeDupe()
    dedupe.foo()

if __name__ == '__main__':
    main()
