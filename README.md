# SummonerTrackerClientP
SummonerTracker Overlay

Press the hotkey (default ^) to open the Setter Window in game and start tracking summoner spells.

If another summoner on your team uses the overlay you will share information with oneanother.

When you start the overlay it will create a tray icon (next to the time and date in the windows tool bar).
From there you can set your prefered hotkey (examples include: ^; space; shift+s) and move the Information Display Window and the Setter Window.

How it works:
The riot live game api is used to find current game information to set the Champions and Spells in the Setter Overlay.
(Please be aware that the ulimate cooldows are not loaded via api. They are allways tracked with 110 seconds cooldown regardless of champion)
Information is shared via mqtt. Your team information (Summonernames and teamid) is used to create the topic. All your teammembers listen to the same topic and get the same information.

The positions of the Windows and the hotkey are saved in %Appdata%\SummonerTrackerOverlay after you have started the Overlay once.
