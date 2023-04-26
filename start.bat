chcp 65001
cd "%~dp0"
python3 main.py start
start /MIN cmd /k python3 bot_handler.py
java -Xmx1024M -Xms1024M -jar spigot-1.19.4.jar nogui
python3 main.py stop
pause
exit

