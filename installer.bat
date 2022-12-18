@ECHO OFF
echo "===build start"
svn update src
cd src
rmdir /S/Q dist\KEYI-RTIS
echo "===remove directory %cd%\dist\KEYI-RTIS"
pyinstaller -D -w -i logo.ico screen_ocr.py -n KEYI-RTIS ^
	--add-data="Tesseract-OCR;Tesseract-OCR" ^
	--add-data="config.ini;./"
echo "===build end"
echo "===package end"
del /S/Q setup\keyi-rtis-setup.exe
echo "===delete file %cd%\setup\keyi-rtis-setup.exe"
cd "..\Inno Setup 6"
iscc "..\KEYI-RTIS.iss"
cd ..
svn commit -m "update ... " "src/setup/"
echo "===commit file %cd%\src\setup\keyi-rtis-setup.exe"
echo "===package end"