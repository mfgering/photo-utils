"""
Check what moved or not between directories.
"""

"""
File properties: 
  name
  size
  hash
"""
import argparse, logging, os, sys

def initArgParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--config', default="phototags.ini", help="Configuration file")
	parser.add_argument('--file-tags', default=False, dest='print_file_tags', action='store_true', help="Print tags for each file")
	parser.add_argument('--no-file-tags', dest='print_file_tags', action='store_false', help="Do not print tags for each file")
	parser.add_argument('--check-allowed', default=False, dest='check_allowed', action='store_true', help="Check that each tag is required or allowed")
	parser.add_argument('--no-check-allowed', dest='check_allowed', action='store_false', help="Do not check that each tag is required or allowed")
	parser.add_argument('--check-required', default=False, dest='check_required', action='store_true', help="Check that each image has required tags")
	parser.add_argument('--no-check-required', dest='check_required', action='store_false', help="No check that each image has required tags")
	parser.add_argument('--frequency', default=False, action='store_true', help="Tally tag frequencies")
	parser.add_argument('--no-frequency', action='store_false', help="Do not tally tag frequencies")
	parser.add_argument('--check-exif', default=False, dest='check_exif', action='store_true', help="Check for old EXIF tags")
	parser.add_argument('--no-check-exif', dest='check_exif', action='store_false', help="Do not check for old EXIF tags")
	parser.add_argument('--max_files', type=int, default=-1, help="Max number of files (-1 for all of them)")
	parser.add_argument('--debug', default=False, dest='debug', action='store_true', help="Enable debugging")
	parser.add_argument('--no-debug', dest='debug', action='store_false', help="Do not enable debugging")
	return parser

class MoveChecker(object):
	def __init__(self, dir_old, dir_new, callback=None, args=None):
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

	def probe_dir(dir):
		if not os.path.isdir(dir):
			raise ValueError("Not a directory")

	"""
			if os.path.isdir(target) or os.path.isfile(target):			
				for dir_name, _, file_list in os.walk(target):
					if self.stop:
						break
					for fn in file_list:
						if self.stop:
							break
						bad_tags = []
						missing_tags =[]
						fn_full = os.path.join(dir_name, fn)
						tags = self.tag_stats.get_tags(fn_full)
						if self.args.print_file_tags:
							self.logger.info("File '%s' tags: %s", fn, ", ".join(tags))
						if self.args.frequency:
							self.tag_stats.add_tag_info(fn_full, tags)
						if self.args.check_allowed:
							bad_tags = self.tag_stats.check_allowed(fn_full, tags)
						if self.args.check_required:
							missing_tags = self.tag_stats.check_required(fn_full, tags)
						self.doCallback("tags", {"filename": fn_full, "tags": tags, "missingTags": missing_tags,
										"badTags": bad_tags})					
						self.total_files += 1
						if self.total_files % 100 == 0:
							self.logger.info("%s files processed...", str(self.total_files))
						if self.args.max_files > 0 and self.total_files >= self.args.max_files:
							self.logger.info("%s maximum files reached", str(self.args.max_files))
							break
			else:
				self.logger.error("Target %s is neither a file or directory", target)
				return 1
	"""

if __name__ == '__main__':
	error_count = main()
	if error_count == 0:
		sys.exit(0)
	sys.exit(1)
