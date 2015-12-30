# -*- mode: python -*-

block_cipher = None


a = Analysis(['axiom-runner.py'],
             pathex=['.'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries +  [('oraociei11.dll','./software/instantclient_11_2/oraociei11.dll','BINARY')],
          a.zipfiles,
          a.datas,
          name='axiom',
          debug=False,
          strip=None,
          upx=True,
          console=True )
