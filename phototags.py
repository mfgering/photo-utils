from iptcinfo3 import IPTCInfo
import exifread
import configparser
import argparse, os, sys
import logging

class PhotoTags(object):
	def __init__(self):
		self.error_count = 0
		self.tags_allowed = []
		self.tags_required = []
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument('targ_arg', help="File or directory to check")
		self.parser.add_argument('--config', default="phototags.ini", help="Configuration file")
		self.parser.add_argument('--check_allowed', type=bool, default=True, help="Check that each tag is required or allowed")
		self.parser.add_argument('--check_required', type=bool, default=True, help="Check that each image has required tags")
		self.parser.add_argument('--frequency', type=bool, default=True, help="Tally tag frequencies")
		self.parser.add_argument('--check_exif', type=bool, default=True, help="Check for old EXIF tags")
		self.args = self.parser.parse_args()
		if self.args.targ_arg is None:
			self.parser.print_help()
			sys.exit(1)
		self.init_logging()
		self.init_config()
		self.tag_stats = Tag_Stats(self.tags_allowed, self.tags_required)
	
	def init_config(self):
		self.config_parser = configparser.ConfigParser()
		config_ini = self.args.config
		if os.path.isfile(config_ini):
			self.config_parser.read(config_ini)
			if self.config_parser.has_section("Tags"):
				option = self.config_parser.get("Tags", "required")
				self.tags_required = self.option2tags(option)
				option = self.config_parser.get("Tags", "allowed")
				self.tags_allowed = self.option2tags(option)
			else:
				self.logger.warn("Configuration is missing a [Tags] section")
		else:
			self.config = None
			if self.args.check_allowed or self.args.check_required:
				self.logger.error("Missing config file '%s'", config_ini)
				self.error_count += 1
				self.args.check_allowed = False
				self.args.check_required = False

	def option2tags(self, option):
		arr = option.split("\n")
		result = []
		for t in arr:
			t_trim = t.strip()
			if len(t_trim) > 0:
				result.append(t_trim)
		return result

	def process_target(self, target=None):
		if target is None:
			target = self.args.targ_arg
		if os.path.isdir(target) or os.path.isfile(target):
			for dir_name, subdir_list, file_list in os.walk(target):
				for fn in file_list:
					fn_full = os.path.join(dir_name, fn)
					tags = self.tag_stats.get_tags(fn_full)
					self.logger.info("File '%s' tags: %s", fn, ", ".join(tags))
					if self.args.frequency:
						self.tag_stats.add_tag_info(fn_full, tags)
					if self.args.check_allowed:
						self.tag_stats.check_allowed(fn_full, tags)
					if self.args.check_required:
						self.tag_stats.check_required(fn_full, tags)
			if self.args.frequency:
				self.tag_stats.print_frequency(self.logger)
			if self.args.check_allowed:
				self.tag_stats.print_allowed(self.logger)
			if self.args.check_required:
				self.tag_stats.print_required(self.logger)
			if self.args.check_exif:
				self.tag_stats.print_exif_keyword_files(self.logger)
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

	def get_error_count(self):
		return self.tag_stats.get_error_count() + self.error_count

class Tag_Stats(object):
	def __init__(self, tags_allowed, tags_required):
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
		#TODO: Check for config is None
		for tag in tags:
			if tag not in self.tags_allowed and tag not in self.tags_required:
				self.bad_tags.append((fn, tag))

	def check_required(self, fn, tags):
		#TODO: Check for config is None
		for tag_required in self.tags_required:
			if tag_required not in tags:
				self.missing_tags.append((fn, tag_required))
	
	def print_frequency(self, logger):
		logger.info("Tag frequencies:")
		for tag in sorted(self.freq_dict.keys()):
			logger.info("\t%s: %s", tag, str(self.freq_dict[tag]))

	def print_allowed(self, logger):
		logger.info("Unallowed tags:")
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

def main():
	photo_tags = PhotoTags()
	photo_tags.logger.setLevel(logging.DEBUG)
	error_count = photo_tags.process_target()
	if error_count > 0:
		label = "errors"
		if error_count == 1:
			label = "error"
		photo_tags.logger.error("%s %s", error_count, label)
	else:
		photo_tags.logger.info("No errors")
	return error_count

if __name__ == '__main__':
	error_count = main()
	if error_count == 0:
		sys.exit(0)
	sys.exit(1)
