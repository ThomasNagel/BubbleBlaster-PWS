# BubbleBlaster-PWS
In this game a player competes with an AI for bubbles. We made this game for a school project (Profiel Werkstuk). We used NEAT Python to create the AI (evolution based). 
In this repository you can find the code for the game and the training software.

Our code uses seperate files for the configuration of the game (json format). This makes it possible to change the settings of the game without changing the source code. 
Do you want to go faster? Go ahead! Just changes the settings. Do you want more powerups? Why not! Have some fun with experementing. You could even changes the animations. 
Just place the images of the new animation in the right folder and name them in the order they need to play (1.png, 2.png, 3.png, ect.). 
You have excess to the source code, so you can even changes the game itself. Anyway, sales pitch is over. Let's download the software!

The folder 'Method 1' contains the code that has a working AI, Method 2 works to, but Method 3 is unfortunately a bit jank.
The file BubbleBlaster sprites based.py contains the game, the training file contains the code for teh training procedure.

This is a guide to downloading python and the nessecery libraries (Scroll down for the dutch guide).

English guide:
#The project is due in two days so I don't have time left for the english guide.I hope that you can read dutch...


Nederlandse uitleg:
We moeten eerst python installeren (dit is de programmeertaal waarop onze software draait)
1) Download Python: https://www.python.org/downloads/ (Voor extra hulp: https://www.youtube.com/watch?v=IDo_Gsv3KVk)

Vervolgens moeten we twee libraries installeren, voor extra hulp: https://www.youtube.com/watch?v=nuufiNScK4s (Deze video laat nog een keer zien hoe je python moet downloaden, begin op tijdstip 0:58 om te zien hoe je de libraries moet downloaden)
2) Open Opdrachtprompt (Druk windows toest in en type cmd) 
3) Type in Opdrachtprompt: pip install pygame
4) Nadat pygame gedownload is type: pip install neat-python

Software draaien:
Download de bestanden in deze repository die je wil draaien. 
Om deze bestanden te runnen moet je Idle openen
1) Open idle (Druk windows toets in en type idle)
2) Klik in idle op "file" en vervolgens op "openen"
3) Selecteer het bestand dat je wil draaien en open het (Als het goed is kan je nu de source code zien)
4) Druk op F5 (nu begint het programma te draaien)

###WARINING: THE TRAINING PROGRAM WRITES IT'S PROGRESS TO THE HARD DISK, WHEN YOU TRAIN THE AI FOR MORE THEN A NIGHT YOU CAN HAVE MULTIPLE GB'S WORTH OF AI'S###

