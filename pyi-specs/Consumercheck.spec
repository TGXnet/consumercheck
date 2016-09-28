# -*- mode: python -*-

block_cipher = None

added_files = [
    ('../ConsumerCheck/*.png', '.'),
    ('../ConsumerCheck/*.svg', '.'),
    ('../ConsumerCheck/graphics', 'graphics'),
    ('../docs-user/build/html', 'help-docs'),
    ]

a = Analysis(['../ConsumerCheck/cc_start.py'],
             pathex=['ConsumerCheck', 'pyi-specs'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=['pyi-hooks'],
             runtime_hooks=['pyi-rthook_pyqt4.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Consumercheck',
          debug=False,
          strip=False,
          upx=True,
          console=False )

app = BUNDLE(exe,
             name='Consumercheck.app',
             icon='osx-cc.icns',
             bundle_identifier='no.tgxnet.nofima.consumercheck',
             info_plist={
                 'NSHighResolutionCapable': 'True',
                 'CFBundleVersion': '1.4.2',
                 },
             )
