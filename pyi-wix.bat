rem *** Harvest files
heat.exe dir pyi-build-cc-1.2.1\ConsumerCheck -gg -srd -sreg -scom -cg CcFiles -dr CCROOTDIR -ke -generate components -out pyi-cc-files.wxs

rem *** Run compiler
candle pyi-cc-files.wxs pyi-wix-cc-instinfo.wxs

rem *** Run linker
light -b pyi-build-cc-1.2.1\ConsumerCheck pyi-cc-files.wixobj pyi-wix-cc-instinfo.wixobj -ext WixUIExtension -out pyi-cc-install-1.2.1.msi
