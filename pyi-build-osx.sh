#! /bin/sh
# --onefile --windowed
# pyinstaller --log-level=INFO --clean --noconfirm --workpath=pyi-workdir --distpath=pyi-dist-1.4.0 pyi-cc-osx.spec
pyinstaller --noconfirm --log-level=INFO \
	--clean --onefile --windowed \
	--path=ConsumerCheck \
	--workpath=pyi-workdir \
	--distpath=pyi-dist-1.4.0 \
	--additional-hooks-dir=pyi-hooks \
	--runtime-hook=pyi-rthook_pyqt4.py \
	ConsumerCheck/cc_start.py
