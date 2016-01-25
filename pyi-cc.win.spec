# -*- mode: python -*-

block_cipher = None

added_files = [
    ('ConsumerCheck/ConsumerCheckLogo.png', ''),
    ('ConsumerCheck/reset_xy.svg', ''),
    ('ConsumerCheck/save.svg', ''),
    ('ConsumerCheck/x_down.svg', ''),
    ('ConsumerCheck/x_up.svg', ''),
    ('ConsumerCheck/y_down.svg', ''),
    ('ConsumerCheck/y_up.svg', ''),
    ('ConsumerCheck/graphics', 'graphics'),
    ('docs-user/build/html', 'help-docs'),
    ('Rdist/R-3.0.2', 'R-3.0.2'),
    ('ConsumerCheck/rsrc', 'rsrc'),
    ]
#d

rt_hooks = ['pyi-rthook_pyqt4.py']


a = Analysis([os.path.join('ConsumerCheck', 'cc_start.py')],
             pathex=['ConsumerCheck'],
             binaries=[('/usr/local/lib/python2.7/site-packages/pandas/lib.so', 'pandas.lib' )],
             datas=added_files,
             hiddenimports=[],
             hookspath=['pyi-hooks'],
             runtime_hooks=rt_hooks,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
#d



pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
#d


runopts = [
    # ('v', None, 'OPTION'),
    # ('W ignore', None, 'OPTION'),
    ]
#d



exe = EXE(pyz,
          a.scripts,
          runopts,
          exclude_binaries=True,
          name='consumercheck.exe',
          debug=True,
          strip=None,
          upx=False,
          console=True )
#d



coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=False,
               name='ConsumerCheck')
#d
