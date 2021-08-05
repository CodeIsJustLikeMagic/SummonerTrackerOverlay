SummonerTracker Overlay
======================

An Overlay intended for Tracking Summoner Spells and sharing them with teammates.

[**Download here**](https://github.com/CodeIsJustLikeMagic/SummonerTrackerClientP/releases/latest)

[Screenshots](https://imgur.com/a/R8PoPoN)

How to use it
------------

* Press the hotkey (default: ^) to open the Setter Window in game and start timing summoner spells.
* The summoner spell buttons will assume that the spell has been used 7 seconds ago. 
* The "-30 sec" Buttons will Modify existing Timers by subtracting 30 seconds.
* To remove a spell timer press the button again.
* "reload" will update the positions of the Champions in the Setter Window according to the in game scoreboard. Meaning you can rearrange the scoreboard in game and then "reload" to copy the new positions.

**If another summoner on your team uses the overlay as well you will share information with each other.**

When you start the overlay it will create a tray icon (next to the time and date in the windows tool bar).
From there you can move the Information Display Window and the Setter Window and set your prefered hotkey (examples include: ^; space; shift+s). 

The overlay is not visible if you play in fullscreen mode.

This Tracker DOES NOT track spells automatically. You have to start the timers yourself.

lol Patches and cdr
-------------
* summoner spell cooldowns, item ability haste, and ult cooldowns get loaded from [Community Dragon](https://www.communitydragon.org/) (a centralized League of Legends game data and asset provider run by the community)
  * All cooldows get updated once community dragen is up to date with a lol patch
  * The data gets saved in %Appdata%\SummonerTrackerOverlay\CDragon and reloaded every 7 days
  
* teleport cooldown gets calculated according to the level of the champion.
* ulimate cooldows are loaded from CDragon and set according to Champion and Level.
* uses ability haste from items and cdr from cloud drakes for ultimate (no blue buff, small rune or mythic passive)
* uses summoner spell haste from aram aura, insiration tree and boots of lucidity
   * I can only get the keystone, and the name of the primary tree and the secondary tree with the Live Game Api. So I'm currently assuming that whenever a player has the "Inspiration" Tree, he is running Cosmic Insight.

How it works
------------
* The riot [live game api](https://developer.riotgames.com/docs/lol#league-client-api) is used to find current game information to set the champions and spells in the Setter Overlay.
* Summoner Spell Cooldowns are loaded from [Community Dragon](https://www.communitydragon.org/).
* Information is shared via mqtt. Your team information (summoner names and teamid) is used to create the topic. All your team members listen and publish to the same topic.
* The Positions of the windows and the hotkey are saved in `%Appdata%\SummonerTrackerOverlay` after you have started the overlay once.
* This is also where you can find a log file. The log gets cleared every 7 days.

Legal Stuff
--------

The SummonerTracker has been reviewed and approved through the riot developer portal.

![image](https://user-images.githubusercontent.com/25256413/128340012-5537e164-a7ef-48a0-adc4-5a1156bb5a61.png)

Other Similar Applications (also reviewed and verified): 
* [LOL Tracker](https://www.loltracker.gg/)
* [Summoner](/github.com/4dams/Summoner)
* [Flash Track](http://flashtrack.webflow.io/)

Please note that all of these trackers are inferior to mine because they don't share information with teammates ;)
