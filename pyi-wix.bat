rem *** Harvest files
heat.exe dir pyi-dist-1.4.0\ConsumerCheckWin32 -gg -srd -sreg -scom -cg CcFiles -dr CCROOTDIR -ke -generate components -out pyi-cc-files.wxs

rem *** Run compiler
candle pyi-cc-files.wxs pyi-wix-cc-instinfo.wxs

rem *** Run linker
light -b pyi-dist-1.4.0\ConsumerCheckWin32 pyi-cc-files.wixobj pyi-wix-cc-instinfo.wixobj -ext WixUIExtension -out cc-install-1.4.0.msi
