; -- CCInnoPack.iss --
; Inno Setup packaging script for ConsumerCheck

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=ConsumerCheck
AppVersion=0.6.0
DefaultDirName={pf}\ConsumerCheck
DefaultGroupName=ConsumerCheck
UninstallDisplayIcon={app}\consumercheck.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=setup-ConsumerCheck-0_6_0
OutputDir=..\CCWinPack
SourceDir=consumercheck-0.6.0

[Files]
Source: "*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\ConsumerCheck"; Filename: "{app}\consumercheck.exe"
