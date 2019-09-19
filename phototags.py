import argparse, csv, sys

def main():
    pass

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