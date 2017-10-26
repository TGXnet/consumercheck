# -*- mode: python -*-

block_cipher = None

added_files = [
    ('ConsumerCheck/*.png', '.'),
    ('ConsumerCheck/*.svg', '.'),
    ('ConsumerCheck/graphics', 'graphics'),
    ('ConsumerCheck/VERSION.txt', '.'),
    ('ConsumerCheck/about.tmpl', '.'),
#    ('docs-user/build/html', 'help-docs'),
    ('Rdist/R-3.3.1', 'R-3.3.1'),
#    ('ConsumerCheck/rsrc', 'rsrc'),
    ]
a = Analysis(['ConsumerCheck\\cc_start.py'],
             pathex=['ConsumerCheck'],
             binaries=None,
             datas=added_files,
             hiddenimports=['configparser'],
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
          exclude_binaries=True,
          name='ccwin',
          debug=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='ConsumerCheckWin32')
#EOF