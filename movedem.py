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
	parser.add_argument('--max-files', type=int, default=-1, help="Max number of files (-1 for all of them)")
	parser.add_argument('--old-dir', type=str, default=-1, help="Old directory")
	parser.add_argument('--new-dir', type=str, default=-1, help="New directory")
	parser.add_argument('--compare', default=True, dest='compare', action='store_true', help="Compare old and new directories")
	parser.add_argument('--no-compare', dest='compare', action='store_false', help="Do not compare old and new directories")
	parser.add_argument('--debug', default=False, dest='debug', action='store_true', help="Enable debugging")
	parser.add_argument('--no-debug', dest='debug', action='store_false', help="Do not enable debugging")
	return parser

class MoveChecker(object):
	def __init__(self, dir_old, dir_new, callback=None, args=None):
		self.stop = False
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

	def do_callback(self, name, data):
		if self.callback is not None:
			self.callback(name, data)

	def probe_callback(self, name, data):
		self.do_callback(name, data)
		if name == "file":
			self.total_files = self.total_files + 1
			if self.total_files % 100 == 0:
				self.logger.info("%s files processed...", str(self.total_files))
			if self.args.max_files > 0 and self.total_files >= self.args.max_files:
				self.logger.info("%s files processed; max files reached!", str(self.total_files))
				return False
			return True
	
	def debug(self):
		pass

	def do_checks(self):
		if self.args.compare:
			self.do_compare()
	
	def do_compare(self):
		dir_data_old = DirData(self.args.dir_old, self.probe_callback)
		dir_data_old.probe_dir(self.args.dir_old)
		dir_data_new = DirData(self.args.dir_new, self.probe_callback)
		dir_data_new.probe_dir(self.args.dir_new)

		# Init multi-dicts for the name and size fields
		mdict_size_new = {}
		for file_data in dir_data_new.file_data:
			self.multi_dict_save(mdict_size_new, file_data.get_size(), file_data)

		same_files = []
		no_matches = []
		name_changes = []
		file_count = 0
		for file_data_old in dir_data_old.file_data:
			file_count = file_count + 1
			if file_count % 50 == 0:
				self.logger.info("Processed %s files..." % (str(file_count)))
			is_matched = False
			if file_data_old.get_size() in mdict_size_new:
				new_files = mdict_size_new[file_data_old.get_size()]
				if type(new_files) != list:
					new_files = [new_files]
				for file_data_new in new_files:
					if file_data_new.get_hash() == file_data_old.get_hash():
						old_new = (file_data_old, file_data_new)
						same_files.append(old_new)
						is_name_changed = file_data_old.get_fn() != file_data_new.get_fn()
						if is_name_changed:
							name_changes.append(old_new)
						is_matched = True
						self.do_callback("file_check", {"is_matched": is_matched, 
								"is_name_changed": is_name_changed, "file_count": file_count, 
								"old_file": file_data_old, "new_file": file_data_new})
			if not is_matched:
				no_matches.append(file_data_old)
				self.do_callback("file_check", {"is_matched": is_matched, "file_count": file_count, 
						"old_file": file_data_old, "new_file": None})
		self.logger.info("Found %s matching (includes %s name changes), %s not matching" % 
			(str(len(same_files)), str(len(name_changes)), str(len(no_matches))))

	def multi_dict_save(self, dictionary, key, value):
		if key in dictionary:
			curr_val = dictionary[key]
			if type(curr_val) != list:
				value = [curr_val, value]
			else:
				curr_val.append(value)
				value = curr_val
		dictionary[key] = value


class DirData(object):
	def __init__(self, dir_name, callback=None):
		self.dir_name = dir_name
		self.callback = callback
		self.stop = False
		self.total_files = 0
		self.file_data = []

	def do_callback(self, name, data):
		if self.callback is not None:
			return self.callback(name, data)

	def probe_dir(self, dir_name):
		if not os.path.isdir(dir_name):
			raise ValueError("Not a directory")
		for dir_name, _, file_list in os.walk(dir_name):
			if self.stop:
				break
			for fn in file_list:
				if self.stop:
					break
				if not self.probe_file(dir_name, fn):
					break

	def probe_file(self,  dir_name, fn):
		self.total_files += 1
		file_data = FileData(dir_name, fn)
		self.file_data.append(file_data)
		should_continue = self.do_callback("file", {"file_data": file_data})
		return should_continue


class FileData(object):
	def __init__(self, dir_name, fn):
		self.file_hash = None
		self.dir_name = dir_name
		self.fn = fn
		stats = os.stat(self.get_full_fn())
		self.file_size = os.stat_result(stats).st_size

	def get_size(self):
		return self.file_size

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
	try:
		parser = initArgParser()
		parser.add_argument('--dir-old', required=True, help="Directory with old files")
		parser.add_argument('--dir-new', required=True, help="Directory with new files")
		args = parser.parse_args()
		checker = MoveChecker(dir_old=args.dir_old, dir_new=args.dir_new, args=args)
		if args.debug:
			checker.logger.setLevel(logging.DEBUG)
			checker.debug()
		checker.do_checks()
		checker.logger.info("%s files processed", str(checker.total_files))
	except Exception as exc:
		logging.getLogger().exception(exc)

	def debug(self):
		pass

if __name__ == '__main__':
	main()
	sys.exit(0)
