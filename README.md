SummonerTracker Overlay
======================
How to use it
------------
Press the hotkey (default: ^) to open the Setter Window in game and start timing summoner spells.
The summoner spell buttons will assume that the spell has been used 7 seconds ago. 
The "-1min" Buttons will assume the spell has been used 1 minute ago.
To remove a spell timer press the button again.

"reload" will update the positions of the Champions in the Setter Window according to the in game scoreboard.

If another summoner on your team uses the overlay as well you will share information with each other.

When you start the overlay it will create a tray icon (next to the time and date in the windows tool bar).
From there you can set your prefered hotkey (examples include: ^; space; shift+s) and move the Information Display Window and the Setter Window.

The overlay is not visible if you play in fullscreen mode.

[Download here](https://github.com/CodeIsJustLikeMagic/SummonerTrackerClientP/releases/latest)

This Tracker DOES NOT track spells automatically. You have to start the timers yourself.

How it works
------------
The riot live game api is used to find current game information to set the champions and spells in the Setter Overlay.
(Please be aware that the ulimate cooldows are currently not loaded via api. They are allways tracked with 110 seconds cooldown regardless of champion)

Information is shared via mqtt. Your team information (summoner names and teamid) is used to create the topic. All your team members listen and publish to the same topic.

The positions of the windows and the hotkey are saved in `%Appdata%\SummonerTrackerOverlay` after you have started the overlay once.
This is also where you can find a log file. The log gets cleared every 7 days.

--------
This project isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends.
