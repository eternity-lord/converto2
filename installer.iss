#define AppName "EDIUS Booster"
#define AppVersion "7.0.0"
#define AppPublisher "Mohammad Irani"

[Setup]
AppId={{8D1F672C-4B92-4C79-9F3E-6F2569FE8A7B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=EdiusBooster-Setup-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\EdiusBooster.exe
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\EdiusBooster\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\EdiusBooster.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\EdiusBooster.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\EdiusBooster.exe"; Description: "Launch EDIUS Booster"; Flags: nowait postinstall skipifsilent
