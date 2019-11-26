"""
Check what moved or not between directories.
"""

"""
File properties: 
  name
  size
  hash
"""
import argparse, hashlib, logging, os, sys

def initArgParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--max_files', type=int, default=-1, help="Max number of files (-1 for all of them)")
	parser.add_argument('--debug', default=False, dest='debug', action='store_true', help="Enable debugging")
	parser.add_argument('--no-debug', dest='debug', action='store_false', help="Do not enable debugging")
	return parser

class MoveChecker(object):
	def __init__(self, dir_old, dir_new, callback=None, args=None):
		self.stop = False
		self.error_count = 0
		self.total_files = 0
		self.args = args
		self.callback = callback
		self.init_logging()

	def init_logging(self):
		self.logger = logging.getLogger("movedem")
		self.logger.setLevel(logging.INFO)
		self.logger.addHandler(logging.StreamHandler(sys.stderr))

	def stop_processing(self):
		self.stop = True

	def get_error_count(self):
		return self.tag_stats.get_error_count() + self.error_count
	
	def do_callback(self, name, data):
		if self.callback is not None:
			self.callback(name, data)

	def debug(self):
		dd1 = DirData(self.args.dir_old, self.callback)
		dd1.probe_dir(self.args.dir_old)
		pass

	def do_check(self):
		pass #TODO: FIX THIS
		return self.error_count


class DirData(object):
	def __init__(self, dir_name, callback=None, total_files=0, max_files=-1):
		self.dir_name = dir_name
		self.callback = callback
		self.stop = False
		self.error_count = 0
		self.total_files = total_files
		self.max_files = max_files
		self.file_data = []

	def do_callback(self, name, data):
		if self.callback is not None:
			self.callback(name, data)

	def probe_dir(self, dir_name):
		if not os.path.isdir(dir_name):
			raise ValueError("Not a directory")
		for dir_name, _, file_list in os.walk(dir_name):
			if self.stop:
				break
			for fn in file_list:
				if self.stop:
					break
				self.probe_file(dir_name, fn)

	def probe_file(self,  dir_name, fn):
		self.do_callback("file", {"dir_name": dir_name, "fn": fn})
		self.total_files += 1
		self.file_data.append(FileData(dir_name, fn))
		if self.total_files % 100 == 0:
			self.logger.info("%s files processed...", str(self.total_files))
		if self.max_files > 0 and self.total_files >= self.max_files:
			self.logger.info("%s maximum files reached", str(self.max_files))
			self.stop = True

class FileData(object):
	def __init__(self, dir_name, fn):
		self.file_hash = None
		self.dir_name = dir_name
		self.fn = fn
		self.stats = os.stat(self.get_full_fn())

	def get_size(self):
		return os.stat_result(self.stats).st_size

	def get_fn(self):
		return self.fn

	def get_dir_name(self):
		return self.dir_name

	def get_full_fn(self):
		return os.path.join(self.dir_name, self.fn)

	def get_hash(self):
		if self.file_hash is None:
			block_size = 65536
			file_hash = hashlib.sha256()
			with open(self.get_full_fn(), 'rb') as f:
				fb = f.read(block_size)
				while len(fb) > 0:
					file_hash.update(fb)
					fb = f.read(block_size)
			self.file_hash = file_hash.hexdigest()
		return self.file_hash
	
	def __str__(self):
		s = "%s: dir: %s size: %s hash: %s" % (self.get_fn(), self.get_dir_name(), self.get_size(), self.get_hash())
		return s

def main():
	error_count = 0
	try:
		parser = initArgParser()
		parser.add_argument('--dir-old', required=True, help="Directory with old files")
		parser.add_argument('--dir-new', required=True, help="Directory with new files")
		args = parser.parse_args()
		checker = MoveChecker(dir_old=args.dir_old, dir_new=args.dir_new, args=args)
		if args.debug:
			checker.logger.setLevel(logging.DEBUG)
			checker.debug()
		error_count = checker.do_check()
		checker.logger.info("%s files processed", str(checker.total_files))
		if error_count > 0:
			label = "errors"
			if error_count == 1:
				label = "error"
			checker.logger.error("%s %s", error_count, label)
		else:
			checker.logger.info("No errors")
	except Exception as exc:
		logging.getLogger().exception(exc)
		error_count = error_count + 1
	return error_count

	def debug(self):
		pass

if __name__ == '__main__':
	error_count = main()
	if error_count == 0:
		sys.exit(0)
	sys.exit(1)
