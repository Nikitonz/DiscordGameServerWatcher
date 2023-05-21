chcp 65001
set "sourceFolder=%CD%"
set "targetFolder=%CD%\SAVES_bak"
set "backupFolder=%CD%\SAVES_bak\SAVES_bak1"
@echo off
setlocal enabledelayedexpansion
if not exist "%targetFolder%" (
    mkdir "%targetFolder%"
    echo Created targetFolder: %targetFolder%
)
@echo off
if not exist "%backupFolder%" (
    mkdir "%backupFolder%"
    echo Created backupFolder: %backupFolder%
)
:optionality
cls
@echo Параметр запуска:
@echo 1) сервер + уведомления + бот
@echo 2) только сервер
@echo 3) только бот
@echo 4) создать бэкап миров
@echo 5) создать бэкап бэкапа миров
@echo 6) восстановить миры
@echo 0) выход
:optionality
set /p option="Введите числовую опцию: "
if "%option%"=="" set "option=1"


if "%option%"=="1" goto option1
if "%option%"=="2" goto option2
if "%option%"=="3" goto option3
if "%option%"=="4" goto option4
if "%option%"=="5" goto option5
if "%option%"=="6" goto option6
if "%option%">"6" OR "%option%"<"1" goto end
goto invalidOption

:option1
python3 bot_handler.py start
java -Xmx1024M -Xms1024M -jar spigot-1.19.4.jar nogui
python3 main.py stop
goto end

:option2
java -Xmx1024M -Xms1024M -jar spigot-1.19.4.jar nogui
goto end

:option3
Start PowerShell.exe -NoExit -Command "python bot_handler.py" 
goto end

:option4
set /p option="Вы хотите перезаписать последний сейв? (y/n): "
if "%option%"=="y" (
if "%option%"=="n" goto end )
else 
rem Копирование папок world, world-nether, world_the_end в папку SAVES_bak
xcopy /s /e /i /y "%sourceFolder%\world" "%targetFolder%\world"
xcopy /s /e /i /y "%sourceFolder%\world_nether" "%targetFolder%\world-nether"
xcopy /s /e /i /y "%sourceFolder%\world_the_end" "%targetFolder%\world_the_end"
goto end

:option5
set /p option="Вы хотите создать резервную копию резервной копии? (y/n): "
if "%option%"=="y" (
  for /D %%G in ("%targetFolder%\*") do (
    set "folderName=%%~nxG"
    if not "%folderName%"=="SAVES_bak1" (
        move /Y "%%G" "%backupFolder%\"
    )
  )
pause
) else (if "%option%"=="n" goto end )
else (if not "%option%"=="y" or  not "%option%"=="n" goto option5)

:option6
set /p option="Восстановить резервную копию? ("newest_bak"/"oldest_bak"): "
if "%option%"=="newest_bak" (
xcopy /s /e /i /y "%targetFolder%\world" "%sourceFolder%\world"
xcopy /s /e /i /y "%targetFolder%\world_nether" "%sourceFolder%\world-nether"
xcopy /s /e /i /y "%targetFolder%\world_the_end" "%sourceFolder%\world_the_end"
)
else (if "%option%"=="oldest_bak" 
(
xcopy /s /e /i /y "%backupFolder%\world" "%sourceFolder%\world"
xcopy /s /e /i /y "%backupFolder%\world_nether" "%sourceFolder%\world-nether"
xcopy /s /e /i /y "%backupFolder%\world_the_end" "%sourceFolder%\world_the_end")
)
else goto optionality

:invalidOption
echo Некорректная опция
goto optionality

:end
exit
