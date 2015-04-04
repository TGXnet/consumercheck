# -*- mode: python -*-
import os

block_cipher = None

def Datafiles(*filenames, **kw):

    def datafile(path, strip_path):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    pdir = kw.get('proj_dir')
    return TOC(
        datafile(pdir+'/'+filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(pdir+'/'+filename))


# Graphics
imgs = Datafiles('ConsumerCheckLogo.png',
                 'reset_xy.svg',
                 'save.svg',
                 'x_down.svg',
                 'x_up.svg',
                 'y_down.svg',
                 'y_up.svg',
                 proj_dir='ConsumerCheck')

imgs += Tree(os.path.join('ConsumerCheck', 'graphics'), prefix='graphics', excludes=[])


# R stuff
renv = Tree(os.path.join('Rdist', 'R-3.0.2'), prefix='R-3.0.2')


a = Analysis([os.path.join('ConsumerCheck', 'cc_start.py')],
             pathex=['ConsumerCheck'],
             hiddenimports=[],
             hookspath=['pyi-hooks'],
             runtime_hooks=['pyi-rthook_pyqt4.py'],
             excludes=None,
             cipher=block_cipher)


pyz = PYZ(a.pure,
             cipher=block_cipher)

runopts = [
    # ('v', None, 'OPTION'),
    # ('W ignore', None, 'OPTION'),
    ]

exe = EXE(pyz,
          a.scripts,
          runopts,
          exclude_binaries=True,
          name='consumercheck.exe',
          debug=True,
          strip=None,
          upx=False,
          console=True )


a.datas += imgs
a.datas += renv

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=False,
               name='ConsumerCheck')
