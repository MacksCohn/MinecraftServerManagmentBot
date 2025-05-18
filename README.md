# Minecraft Server Management Discord Bot

Hello! This is a project I made so that I could manage my personal minecraft server remotely using a discord bot.
Features:
* Status button lists whether the server is online, its IP, and lists the players online
* Get Logs button that lists the last few lines of the log file, to allow the user to see what is going on including recent chat messages
* Start Server button that will run the Executable path from the config

Advanced Features:
* Can send minecraft commands in the bot channel, and they will actually run on the server. 
For now, this requires wsl on Windows and an executable that runs the following:
> ```cmd.exe /c start cmd.exe /c wsl.exe screen -S "minecraft-server-screen" ./run.sh``` 
Where `run.sh` and the executable are in the server directory and `run.sh` contains the usual server start instructions. i.e. "java server.jar" 

* Send 'clear' or 'Clear' (without quotes) in order to clear the bot's channel's text
