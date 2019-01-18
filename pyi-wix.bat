rem *** Harvest files
heat.exe dir dist\ccwin -gg -srd -sreg -scom -cg CcFiles -dr CCROOTDIR -ke -generate components -out pyi-cc-files.wxs

rem *** Run compiler
candle pyi-cc-files.wxs pyi-wix-cc-instinfo.wxs

rem *** Run linker
light -b dist\ccwin pyi-cc-files.wixobj pyi-wix-cc-instinfo.wixobj -ext WixUIExtension -out cc-install-2.2.0.msi
