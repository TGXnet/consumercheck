#! /bin/sh
# --log-level=TRACE, DEBUG, INFO, WARN, ERROR, CRITICAL
# --debug --onedir --onefile --windowed --console
# --osx-bundle-identifier='no.tgxnet.nofima.consumercheck' \
# --icon='osx-cc.icns' \
pyinstaller --noconfirm \
	--log-level=INFO \
	--onefile \
	--windowed \
	--name=ConsumerCheck \
	--add-data="ConsumerCheck/*.png:." \
	--add-data="ConsumerCheck/*.svg:." \
	--add-data="ConsumerCheck/graphics:graphics" \
	--add-data="ConsumerCheck/VERSION.txt:." \
	--add-data="ConsumerCheck/about.tmpl:." \
	--additional-hooks-dir=pyi-hooks \
	--runtime-hook=pyi-rthook_pyqt4.py \
	--paths="ConsumerCheck" \
	--paths="pyi-specs" \
	--icon='osx-cc.icns' \
	--osx-bundle-identifier='no.tgxnet.nofima.consumercheck' \
	ConsumerCheck/cc_start.py


# productbuild?
# xcodebuild?
# COMPONENT PROPERTY LIST?
# pkgutil
# installer
# --install-location
# 
# --root
# --identifier no.tgxnet.nofima.consumercheck
# --version 2.0.0
# --analyze

# FIXME: This is not working, Application is not to be found.
# pkgbuild --install-location /Applications --identifier no.tgxnet.nofima.consumercheck --version 2.0.0 --root dist cc-osx-2.0.0.pkg
# pkgbuild --analyze --root pyi-specs/pyi-dist-1.4.0 cc-osx-1.4.0.plist

# This is working
# rm dist/ConsumerCheck
# -verbose
# hdiutil create ConsumerCheck_2.0.0_MacOSX.dmg -volname "ConsumerCheck package" -srcfolder dist
