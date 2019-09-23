from iptcinfo3 import IPTCInfo
import exifread
import argparse, os, sys
import logging
import settings

class PhotoTags(object):
	def __init__(self):
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument('targ_arg', help="File or directory to check")
		self.args = self.parser.parse_args()
		if self.args.targ_arg is None:
			self.parser.print_help()
			sys.exit(1)
		self.init_logging()
		self.target = self.args.targ_arg
	
	def process_target(self, target):
		pass

	def init_logging(self):
		self.logger = logging.getLogger("phototags")
		self.logger.setLevel(logging.ERROR)
		self.logger.addHandler(logging.StreamHandler(sys.stderr))
		# Fix iptcinfo logging to avoid stupid warnings
		iptcinfo_logger = logging.getLogger('iptcinfo')
		iptcinfo_logger.setLevel(logging.ERROR)

	def get_tags(self, fn):
		iptc_info = IPTCInfo(fn)
		try:
			tags = [t.decode('utf-8') for t in iptc_info["keywords"]]
		except Exception:
			tags = []
		self.logger.info("File '%s' tags: %s", fn, ", ".join(tags))
		return tags

def main():
	photo_tags = PhotoTags()
	fn = "images/don-elaine.jpg"
	photo_tags.logger.setLevel(logging.DEBUG)
	tags = photo_tags.get_tags(fn)



def main_old():
	parser = argparse.ArgumentParser()
	parser.add_argument('google', help="Google contacts in csv file input")
	parser.add_argument('--postbox', help="Postbox csv file output")
	parser.add_argument('--csv-format', help="CSV file format (google or outlook)")
	args = parser.parse_args()
	with open(args.google, newline='', encoding="utf-8") as google_csvfile:
		post_file = sys.stdout
		if args.postbox:
			post_file = open(args.postbox, "w", newline='', encoding="utf-8")
		csv_format = 'google'
		if args.csv_format == 'outlook':
			csv_format = 'outlook'
		wrtr = csv.DictWriter(post_file, postbox_map.postbox_fields,)
		wrtr.writeheader()
		rdr = csv.DictReader(google_csvfile,  delimiter=',', quotechar='"')
		#rdr = csv.reader(google_csvfile, delimiter=',', quotechar='"')
		#hdr = next(rdr)
		for google_contact in rdr:
			postbox_contact = google_map.handle_google_contact(csv_format, google_contact)
			if 'Primary Email' in postbox_contact and len(postbox_contact['Primary Email']) > 0:
				wrtr.writerow(postbox_contact)

if __name__ == '__main__':
	main()