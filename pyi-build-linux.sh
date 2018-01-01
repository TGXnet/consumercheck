#! /bin/sh
# --debug --onedir --onefile --windowed --console --icon --specpath
#
# --add-data="Rdist/R-3.3.1:R-3.3.1" \
pyinstaller --noconfirm \
	--log-level=DEBUG \
	--debug \
	--onedir \
	--console \
	--name=cclinux \
	--add-data="ConsumerCheck/*.png:." \
	--add-data="ConsumerCheck/*.svg:." \
	--add-data="ConsumerCheck/graphics:graphics" \
	--add-data="ConsumerCheck/VERSION.txt:." \
	--add-data="ConsumerCheck/about.tmpl:." \
	--additional-hooks-dir=pyi-hooks \
	--runtime-hook=pyi-rthook_pyqt4.py \
	--paths="ConsumerCheck" \
	ConsumerCheck/cc_start.py
