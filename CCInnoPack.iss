; -- CCInnoPack.iss --
; Inno Setup packaging script for ConsumerCheck

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=ConsumerCheck
AppVersion=0.4.1
DefaultDirName={pf}\ConsumerCheck
DefaultGroupName=ConsumerCheck
UninstallDisplayIcon={app}\consumercheck.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:ConsumerCheck
SourceDir=consumercheck-0.4.1

[Files]
Source: "*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\ConsumerCheck"; Filename: "{app}\consumercheck.exe"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\R-2.11.1\bin";
