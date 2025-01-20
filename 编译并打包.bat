Pyinstaller -i=".\icon\icon.ico" -F Simulacrum.py
Python Packer.py
rd /s /q .\dist
rd /s /q .\build
del .\Simulacrum.spec
pause