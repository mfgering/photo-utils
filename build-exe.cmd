@echo off
For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
@powershell -Command "get-content version_template.txt | %%{ $_ -replace '{date}', $env:mydate }" > version.py
pyinstaller --add-binary app-icon.jpg;. -i app-icon.ico -F --noconsole movedem_gui.py
pyinstaller --add-binary app-icon.jpg;. -i app-icon.ico -F --noconsole movedem.py
pyinstaller --add-binary app-icon.jpg;. -i app-icon.ico -F --noconsole phototags-gui.py
pyinstaller --add-binary app-icon.jpg;. -i app-icon.ico -F --noconsole phototags.py