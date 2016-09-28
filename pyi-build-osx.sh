#! /bin/sh
# --debug --onedir --onefile --windowed --console --icon --specpath
#
pyinstaller --noconfirm --log-level=INFO \
	    --clean \
	    --workpath="pyi-workdir" \
	    --distpath="pyi-dist-1.4.1" \
	    pyi-specs/Consumercheck.spec

# From version 3.3.x
#	    --add-data="ConsumerCheck/*.png:." \
#	    --add-data="ConsumerCheck/*.svg:." \
#	    --add-data="ConsumerCheck/graphics:graphics" \
#	    --add-data="docs-user/build/html:help-docs" \

# pyi-makespec
# pyinstaller --noconfirm --log-level=INFO \
# 	    --clean --onefile --windowed \
# 	    --specpath="pyi-specs" \
# 	    --name="Consumercheck" \
# 	    --path="ConsumerCheck" \
# 	    --additional-hooks-dir="pyi-hooks" \
# 	    --runtime-hook=pyi-rthook_pyqt4.py \
#           --icon="osx-cc.icns" \
# 	    --osx-bundle-identifier="no.tgxnet.nofima.consumercheck" \
# 	    ConsumerCheck/cc_start.py

# pkgbuild --install-location /Applications --root pyi-specs/pyi-dist-1.4.0 cc-osx-1.4.0.pkg
# pkgbuild --analyze --root pyi-specs/pyi-dist-1.4.0 cc-osx-1.4.0.plist
hdiutil create ConsumerCheck_1.4.1_MacOSX.dmg -volname "CC dist" -srcfolder pyi-specs/pyi-dist-1.4.1
