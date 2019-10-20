from imagededup.methods import PHash
import contextlib, hashlib, logging, os, sqlite3

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib import figure
from pathlib import Path, PosixPath
from typing import Dict, Union, List

import numpy as np
from PIL import Image
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

    def db2map(self, method="P"):
        map = {}
        with contextlib.closing(self.db_conn.cursor()) as cursor:
            if method == "P":
                for row in cursor.execute("SELECT * FROM p_encoding"):
                    map[row[0]] = row[1]
        return map

    def find_duplicates(self, method="P"):
        map = self.db2map(method)
        d = self.p_hasher.find_duplicates(encoding_map=map, max_distance_threshold=10, scores=False)
        reduced, set_seen = self.reduce_dups(d)
        return reduced, set_seen

    def reduce_dups(self, dups):
        result = []
        set_seen = set()
        for id, dup_arr in dups.items():
            if len(dup_arr) > 0 and id not in set_seen:
                set_seen.add(id)
                set_seen.update(dup_arr)
                new_dups = [id]+dup_arr
                result.append(new_dups)
        return (result, set_seen)

    def image_ids_2_filename(self, ids):
        dct = {}
        id_str = ','.join([str(i) for i in ids])
        cursor = self.db_conn.execute("SELECT id, path, filename from image_info where id in (%s)" % id_str)
        for id, path, filename in cursor:
            dct[id] = os.path.join(path, filename)
        return dct

    def plot_images(
        self,
        image_dups,
        id_map
        #image_dir: PosixPath,
        #orig: str,
        #image_list: List,
        #scores: bool = False,
        #outfile: str = None,
    ) -> None:
        """
        Plotting function for plot_duplicates() defined below.

        Args:
            image_dir: image directory where all files in duplicate_map are present.
            orig: filename for which duplicates are to be plotted.
            image_list: List of duplicate filenames, could also be with scores (filename, score).
            scores: Whether only filenames are present in the image_list or scores as well.
            outfile:  Name of the file to save the plot.
        """
        nrows = len(image_dups)
        ncols = max([len(x) for x in image_dups])
        #n_ims = len(image_list)
        #ncols = 4  # fixed for a consistent layout
        #nrows = int(np.ceil(n_ims / ncols)) + 1
        fig = figure.Figure(figsize=(10, 14))

        gs = gridspec.GridSpec(nrows=nrows, ncols=ncols)
        ax = plt.subplot(
            gs[0, 1:3]
        )  # Always plot the original image in the middle of top row
        ax.imshow(Image.open(image_dir / orig))
        ax.set_title('Original Image: {}'.format(orig))
        ax.axis('off')

        for i in range(0, n_ims):
            row_num = (i // ncols) + 1
            col_num = i % ncols

            ax = plt.subplot(gs[row_num, col_num])
            if scores:
                ax.imshow(Image.open(image_dir / image_list[i][0]))
                val = _formatter(image_list[i][1])
                title = ' '.join([image_list[i][0], f'({val})'])
            else:
                ax.imshow(Image.open(image_dir / image_list[i]))
                title = image_list[i]

            ax.set_title(title, fontsize=6)
            ax.axis('off')
        gs.tight_layout(fig)

        if outfile:
            plt.savefig(outfile)

        plt.show()


    def foo(self):
        #self.encode_dir('images-dedup', replace=True)
        images_dups, ids_seen = self.find_duplicates()
        id_map = self.image_ids_2_filename(ids_seen)
        self.plot_images(images_dups, id_map)
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
