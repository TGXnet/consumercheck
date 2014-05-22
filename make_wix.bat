rem *** Harvest files
heat.exe dir consumercheck-1.0.2 -gg -srd -sreg -scom -cg CcFiles -dr CCROOTDIR -ke -generate components -out ccfiles.wxs

rem *** Run compiler
candle ccfiles.wxs consumercheck.wxs

rem *** Run linker
light -b consumercheck-1.0.2 ccfiles.wixobj consumercheck.wixobj -ext WixUIExtension -out consumercheck-1.0.2.msi
