import datetime, os, re, sys
import PyInstaller.__main__

def build_all():
	print("Building...")
	update_version()
	common_args = [
		"--add-binary", "app-icon.jpg;.", "-i",
		"app-icon.ico", "-F", "--noconsole",
	]
	run_pyinstaller(common_args, "movedem_gui.py")
	run_pyinstaller(common_args+["--console"], "movedem.py")
	run_pyinstaller(common_args, "phototags-gui.py")
	run_pyinstaller(common_args+["--console"], "phototags.py")
	print("Done")

def run_pyinstaller(common_args, script_name):
	args = common_args.copy()
	args.append(script_name)
	return PyInstaller.__main__.run(args)

def update_version():
	p = re.compile(r'{.*?}')
	with open("version_template.txt", "r") as in_file, open("version.py", "w") as out_file:
		for line in in_file:
			out_line = re.sub(r'{.*?}', tok_repl, line)
			out_file.write(out_line)
			print(out_line)

def tok_repl(match_obj):
	tok = match_obj.group(0)
	if tok == "{date}":
		today = datetime.date.today()
		tok_replacement = f"{today.year}-{today.month}-{today.day}"
		return tok_replacement
	raise AssertionError("Unkown version token: "+tok)

build_all()
