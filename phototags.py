from iptcinfo3 import IPTCInfo
import datetime
import enum
import exifread
import configparser
import argparse, os, re, sys
import logging

class PhotoTags(object):
	def __init__(self, target_required=False, callback=None, args=None,
				tags_allowed=[], tags_required=[]):
		self.error_count = 0
		self.total_files = 0
		self.tags_allowed = tags_allowed
		self.tags_required = tags_required
		self.args = args
		self.callback = callback
		self.init_logging()

	def process_target(self, target=None):
		self.stop = False
		self.tag_stats = Tag_Stats(self.tags_allowed, self.tags_required, self.callback)
		self.total_files = 0
		if target is None:
			target = self.args.targ_arg
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
			if self.args.frequency:
				self.tag_stats.print_frequency(self.logger)
			if self.args.check_allowed:
				self.tag_stats.print_allowed(self.logger)
			if self.args.check_required:
				self.tag_stats.print_required(self.logger)
			if self.args.check_exif:
				self.tag_stats.print_exif_keyword_files(self.logger)
			self.doCallback("done", {"errorCount": self.get_error_count(), "wasStopped": self.stop})
			return self.get_error_count()
		else:
			self.logger.error("Target %s is neither a file or directory", target)
			return 1

	def init_logging(self):
		self.logger = logging.getLogger("phototags")
		self.logger.setLevel(logging.INFO)
		self.logger.addHandler(logging.StreamHandler(sys.stderr))
		# Fix iptcinfo logging to avoid stupid warnings
		iptcinfo_logger = logging.getLogger('iptcinfo')
		iptcinfo_logger.setLevel(logging.ERROR)
		# Fix iptcinfo logging to avoid stupid warnings
		exifread_logger = logging.getLogger('exifread')
		exifread_logger.setLevel(logging.ERROR)

	def stop_processing(self):
		self.stop = True

	def get_error_count(self):
		return self.tag_stats.get_error_count() + self.error_count
	
	def doCallback(self, name, data):
		if self.callback is not None:
			self.callback(name, data)

class Tag_Stats(object):
	def __init__(self, tags_allowed, tags_required, callback):
		self.freq_dict = {}
		self.bad_tags = []
		self.missing_tags = []
		self.xpkeywords = []
		self.tags_allowed = tags_allowed
		self.tags_required = tags_required

	def get_tags(self, fn):
		iptc_info = IPTCInfo(fn)
		try:
			tags = [t.decode('utf-8') for t in iptc_info["keywords"]]
		except Exception:
			tags = []
		if len(tags) == 0:
			with open(fn, 'rb') as f:
				tag_exif = exifread.process_file(f)
				if "Image XPKeywords" in tag_exif:
					xpkeywords_raw = tag_exif['Image XPKeywords'].values
					tag_str = bytearray(xpkeywords_raw).decode("UTF16")
					if tag_str[-1] == '\x00':
						tag_str = tag_str[0:-1]
					tags = tag_str.split(';')
					self.xpkeywords.append((fn, tag_str))
		return tags

	def add_tag_info(self, fn, tags):
		for tag in tags:
			if tag not in self.freq_dict.keys():
				self.freq_dict[tag] = 0
			self.freq_dict[tag] += 1
	
	def check_allowed(self, fn, tags):
		bad_tags = []
		if self.tags_allowed is not None:
			for tag in tags:
				if tag not in self.tags_allowed and tag not in self.tags_required:
					self.bad_tags.append((fn, tag))
					bad_tags.append(tag)
		return bad_tags

	def check_required(self, fn, tags):
		missing_tags = []
		if self.tags_required is not None:
			for tag_required in self.tags_required:
				if tag_required not in tags:
					self.missing_tags.append((fn, tag_required))
					missing_tags.append(tag_required)
		return missing_tags
	
	def print_frequency(self, logger):
		logger.info("Tag frequencies:")
		for tag in sorted(self.freq_dict.keys()):
			logger.info("\t%s: %s", tag, str(self.freq_dict[tag]))

	def print_allowed(self, logger):
		logger.info("Tags not allowed:")
		for fn, tag in self.bad_tags:
			logger.info("\t%s: %s", fn, tag)

	def print_required(self, logger):
		logger.info("Missing required tags:")
		for fn, tag in self.missing_tags:
			logger.info("\t%s: %s", fn, tag)

	def print_exif_keyword_files(self, logger):
		logger.info("Files with EXIF/XPKeywords tags:")
		for fn, tag_str in self.xpkeywords:
			logger.info("\t%s: %s", fn, tag_str)

	def get_error_count(self):
		error_count = len(self.bad_tags) + len(self.missing_tags)
		return error_count

class PhotoTagsCallback(object):
	def __init__(self, name=None, data=None):
		self.name = name
		self.data = data

def foo(): #TODO: REMOVE THIS
	patterns = ['abc', 'ab?', 'a*', 'a\\nbc', 'a[bc]+']
	kinds = [TagKind.LITERAL, TagKind.WILDCARD, TagKind.REGEX]
	vals = ['abc', 'a\nbc', 'abbcc']
	tpats = TagPatterns()
	for k in kinds:
		for p in patterns:
			t = TagPattern(p, k)
			tpats.add(t)
	for v in ['abc', 'abd', 'ab?', 'a*']:
		found = v in tpats
		print("%s : %s: %s" % (str(t), v, found))

def main():
	#foo() #TODO: REMOVE THIS
	#return
	try:
		parser = initArgParser()
		parser.add_argument('targ_arg', help="File or directory to check")
		args = parser.parse_args()
		config = PhotoTagsConfig()
		config.read_config(args.config)
		photo_tags = PhotoTags(args=args, 
						tags_allowed=config.tags_allowed,
						tags_required=config.tags_required)
		if args.debug:
			photo_tags.logger.setLevel(logging.DEBUG)
		error_count = photo_tags.process_target()
		photo_tags.logger.info("%s files processed", str(photo_tags.total_files))
		if error_count > 0:
			label = "errors"
			if error_count == 1:
				label = "error"
			photo_tags.logger.error("%s %s", error_count, label)
		else:
			photo_tags.logger.info("No errors")
	except PhotoTagsException as exc:
		photo_tags.logger.exception(exc)
	return error_count

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

class PhotoTagsConfig(object):
	def __init__(self):
		self.config_parser = configparser.ConfigParser()
		self.config_ini = None
		self.tags_required = TagPatterns()
		self.tags_allowed = TagPatterns()

	def read_config(self, config_ini="phototags.ini"):
		self.config_ini = config_ini
		if os.path.isfile(config_ini):
			self.config_parser.read(config_ini)
			if self.config_parser.has_section("Tags"):
				option = self.config_parser.get("Tags", "required")
				self.tags_required = self.option2tags(option)
				option = self.config_parser.get("Tags", "allowed")
				self.tags_allowed = self.option2tags(option)
			else:
				raise PhotoTagsException("Configuration is missing a [Tags] section")
		else:
			raise PhotoTagsException("Missing config file '%s'" % (config_ini), config_ini)

	def option2tags(self, option):
		arr = option.split("\n")
		result = TagPatterns()
		for t in arr:
			t_trim = t.strip()
			tag_kind = TagKind.LITERAL
			if t_trim.startswith('w/'):
				tag_kind = TagKind.WILDCARD
				t_trim = t_trim[2:]
			elif t_trim.startswith('r/'):
				tag_kind = TagKind.REGEX
				t_trim = t_trim[2:]
			if len(t_trim) > 0:
				tag_pattern = TagPattern(t_trim, tag_kind)
				result.add(tag_pattern)
		return result

	def save_config(self):
		file = open(self.config_ini, "w")
		if not self.config_parser.has_section("Tags"):
			self.config_parser.add_section("Tags")
		self.config_parser.set("Tags", "allowed", "\n".join(self.tags_allowed))
		self.config_parser.set("Tags", "required", "\n".join(self.tags_required))
		time_str = datetime.datetime.now().strftime("%H:%M%p on %B %d, %Y")
		file.write("# This file was generated at %s\n\n" % (time_str))
		self.config_parser.write(file, False)
		file.close()

class PhotoTagsException(Exception):
	pass

class TagKind(enum.Enum):
	LITERAL = 0
	WILDCARD = 1
	REGEX = 2

class TagPattern(object):
	def __init__(self, tag_pattern:str, tag_kind:TagKind=TagKind.LITERAL):
		self.tag_kind = tag_kind
		self.tag_pattern = tag_pattern
		self.regex = None

	def matches(self, tag_value):
		if self.tag_kind == TagKind.LITERAL:
			return tag_value == self.tag_pattern
		if self.regex is None:
			self.create_regex()
		return self.regex.match(tag_value) is not None

	def create_regex(self):
		expr = self.tag_pattern
		if self.tag_kind == TagKind.WILDCARD:
			# convert the pattern from a wildcard to a regex expression
			for c in '.^$+{}[]\|()':
				expr = expr.replace(c, "\\"+c)
			expr = expr.replace('\\', '\\\\')
			expr = expr.replace ('*', '.*')
			expr = expr.replace('?', '.')
		expr = "^"+expr+"$"
		self.regex = re.compile(expr)

	def __str__(self):
		return "%s (%s)" % (self.tag_pattern, str(self.tag_kind))

class TagPatterns(object):
	def __init__(self):
		self.tag_literals = {}
		self.tag_regexes = []

	def add(self, tag_pattern: TagPattern):
		if tag_pattern.tag_kind == TagKind.LITERAL:
			self.tag_literals[tag_pattern.tag_pattern] = tag_pattern
		else:
			self.tag_regexes.append(tag_pattern)
		
	def __contains__(self, value):
		if value in self.tag_literals:
			return True
		for p in self.tag_regexes:
			if p.matches(value):
				return True
		return False

if __name__ == '__main__':
	error_count = main()
	if error_count == 0:
		sys.exit(0)
	sys.exit(1)
