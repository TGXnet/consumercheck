rem *** Harvest files
heat.exe dir consumercheck-0.6.5 -gg -srd -sreg -scom -cg CcFiles -dr CCROOTDIR -ke -v -generate components -out ccfiles.wxs

rem *** Run compiler
candle -v ccfiles.wxs consumercheck.wxs

rem *** Run linker
light -b consumercheck-0.6.5 -v ccfiles.wixobj consumercheck.wixobj -out consumercheck.msi
