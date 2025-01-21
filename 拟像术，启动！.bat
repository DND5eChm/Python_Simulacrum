@echo off
title 帮你搞搞果园格式的拟像术
:START
python Simulacrum.py
if %ERRORLEVEL% NEQ 0 goto ERROR

:FINE
goto END

:ERROR
echo 发现错误，请点击以重复运行？
pause >nul
goto START

: END
EXIT