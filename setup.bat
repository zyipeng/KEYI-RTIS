@ECHO OFF
echo "===�����ʼ"
set log_name="installer_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
installer.bat > log\%log_name% | type log\%log_name%
echo "===�������"
pause