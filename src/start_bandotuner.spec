# -*- mode: python -*-

block_cipher = None


a = Analysis(['start_bandotuner.py'],
             pathex=['C:\\Users\\behinger\\cloud\\Privat\\bandoneon\\bandotuner'],
             binaries=[('libportaudio64bit.dll', '_sounddevice_data/portaudio-binaries/.'),
	     ('streamer_v2.py','.'),
	     ('download.js','.')],
             datas=[],
             hiddenimports=['sounddevice'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='start_bandotuner',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='start_bandotuner')
