# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['screen_ocr.py'],
             pathex=['D:\\个人文件\\学习\\过去\\图像文字识别\\repos\\发布环境\\src'],
             binaries=[],
             datas=[('Tesseract-OCR', 'Tesseract-OCR'), ('config.ini', './')],
             hiddenimports=[],
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
          name='KEYI-RTIS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='KEYI-RTIS')
