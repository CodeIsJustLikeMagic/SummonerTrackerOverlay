# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['D:\\Eigene Dateien\\Dokumente\\Github\\SummonerTrackerClientP\\TrackerOverlay.py'],
             pathex=['D:\\Eigene Dateien\\Dokumente\\GitHub\\TrackerOverlayBuild\\OneFileBuild'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('./assets/trackerIcon.xpm', 'D:\\Eigene Dateien\\Dokumente\\Github\\SummonerTrackerClientP\\assets\\trackerIcon.xpm',  'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TrackerOverlay',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
		  icon='trackerIcon.ico')
