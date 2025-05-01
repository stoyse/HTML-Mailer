pyinstaller \                                
  --windowed \
  --icon="icon.icns" \
  --add-data "template.html:." \
  --add-data "key.key:." \
  --add-data "settings.json:." \
  --name HTMLMailer \
  main.py