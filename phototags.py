from iptcinfo3 import IPTCInfo
import datetime
import enum
import exifread
import configparser
import argparse, os, re, sys
import logging

class PhotoTags(object):
	def __init__(self, target_required=False, callback=None, args=None,
				tag_patterns=None):
		self.error_count = 0
		self.total_files = 0
		if tag_patterns is None:
			self.tag_patterns = []
		else:
			self.tag_patterns = tag_patterns
		self.args = args
		self.callback = callback
		self.init_logging()

	def process_target(self, target=None):
		self.stop = False
		self.tag_stats = Tag_Stats(self.tag_patterns, self.callback)
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
	def __init__(self, tag_patterns, callback):
		self.freq_dict = {}
		self.bad_tags = []
		self.missing_tags = []
		self.xpkeywords = []
		self.tag_patterns = tag_patterns

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
		if self.tag_patterns is not None:
			for tag in tags:
				if tag not in self.tag_patterns:
					self.bad_tags.append((fn, tag))
					bad_tags.append(tag)
		return bad_tags

	def check_required(self, fn, tags):
		missing_tags = []
		if self.tag_patterns is not None:
			for tagp in self.tag_patterns:
				if tagp.is_required:
					found = False
					for tag in tags:
						if tagp.matches(tag):
							found = True
							break
					if not found:
						self.missing_tags.append((fn, tagp))
						missing_tags.append(tagp)
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

def debug():
	p1 = TagPattern('asdf')
	p2 = TagPattern('xyz')
	tp1 = TagPatterns()
	tp1.add(p1)
	tp2 = TagPatterns(tp1)
	tp1.add(p2)
	patterns = ['a[b*c', 'ab?', 'a*', 'a\\nbc', 'a[bc]+']
	for p in patterns:
		tagp = TagPattern(p, TagKind.WILDCARD)
		r = tagp.get_regex()
		print(r.pattern)
	return
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
	try:
		parser = initArgParser()
		parser.add_argument('targ_arg', help="File or directory to check")
		args = parser.parse_args()
		if args.debug:
			debug()
			return
		config = PhotoTagsConfig()
		config.read_config(args.config)
		photo_tags = PhotoTags(args=args, tag_patterns=config.tag_patterns)
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
		self.tag_patterns = TagPatterns()

	def read_config(self, config_ini="phototags.ini"):
		self.config_ini = config_ini
		if os.path.isfile(config_ini):
			self.config_parser.read(config_ini)
			if self.config_parser.has_section("Tags"):
				option = self.config_parser.get("Tags", "required")
				tags_required = self.option2tags(option, True)
				option = self.config_parser.get("Tags", "allowed")
				tags_allowed = self.option2tags(option, False)
				self.tag_patterns = tags_required + tags_allowed
			else:
				raise PhotoTagsException("Configuration is missing a [Tags] section")
		else:
			raise PhotoTagsException("Missing config file '%s'" % (config_ini), config_ini)

	def option2tags(self, option, is_required):
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
				tag_pattern = TagPattern(t_trim, tag_kind, is_required)
				result.add(tag_pattern)
		return result

	def save_config(self):
		file = open(self.config_ini, "w")
		if not self.config_parser.has_section("Tags"):
			self.config_parser.add_section("Tags")
		tags_allowed = [t.ini_pattern() for t in self.tag_patterns if not t.is_required]
		tags_required = [t.ini_pattern() for t in self.tag_patterns if t.is_required]
		self.config_parser.set("Tags", "allowed", "\n".join(tags_allowed))
		self.config_parser.set("Tags", "required", "\n".join(tags_required))
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
	def __init__(self, tag_pattern:str, tag_kind:TagKind=TagKind.LITERAL, is_required=False):
		self.tag_kind = tag_kind
		self.tag_pattern = tag_pattern
		self.regex = None
		self.is_required = is_required

	def matches(self, tag_value):
		if self.tag_kind == TagKind.LITERAL:
			return tag_value == self.tag_pattern
		return self.get_regex().match(tag_value) is not None

	def is_pattern_valid(self):
		if self.tag_kind == TagKind.LITERAL:
			return True
		try:
			self.get_regex()
		except re.error:
			return False
		return True

	def get_regex(self):
		if self.regex is None:
			expr = self.tag_pattern
			if self.tag_kind == TagKind.WILDCARD:
				expr = self.wildcard2regex(self.tag_pattern)
			elif self.tag_kind == TagKind.LITERAL:
				pass #TODO: escape the metachars
			if expr[0] != "^":
				expr = "^"+expr+"$"
			self.regex = re.compile(expr)
		return self.regex

	def wildcard2regex(self, wildcard):
		map = {
			"*": ".*",
			"?": ".",
			"[": "\\[",
			"]": "\\]",
			"{": "\\{",
			"}": "\\}",
			"(": "\\(",
			")": "\\)",
			"^": "\\^",
			"|": "\\|",
			"\\": "\\\\",
		}
		s = ""
		for c in wildcard:
			d = map.get(c, c)
			s += d
		return s

	def __eq__(self, other):
		if not isinstance(other, TagPattern):
			return False
		return self.tag_kind == other.tag_kind and self.tag_pattern == other.tag_pattern and self.is_required == other.is_required

	def __str__(self):
		required_str = ""
		if self.is_required:
			required_str = "required"
		return "%s (%s) %s" % (self.tag_pattern, str(self.tag_kind), required_str)

	def ini_pattern(self):
		if self.tag_kind == TagKind.LITERAL:
			return self.tag_pattern
		if self.tag_kind == TagKind.WILDCARD:
			return "w/"+self.tag_pattern
		if self.tag_kind == TagKind.REGEX:
			return "r/"+self.tag_pattern
		raise AttributeError

class TagPatterns(object):
	def __init__(self, base_patterns=None):
		self.tag_patterns = []
		if base_patterns is not None:
			self.tag_patterns += base_patterns

	def __add__(self, other):
		if isinstance(other, TagPatterns):
			result = TagPatterns()
			result.tag_patterns = self.tag_patterns + other.tag_patterns
			return result;

	def __len__(self):
		return len(self.tag_patterns)

	def add(self, tag_pattern: TagPattern):
		self.tag_patterns.append(tag_pattern)
		
	def __contains__(self, value):
		for t in self:
			if t.matches(value):
				return True
		return False

	def __iter__(self):
		return iter(self.tag_patterns)

if __name__ == '__main__':
	error_count = main()
	if error_count == 0:
		sys.exit(0)
	sys.exit(1)
