#!/bin/bash

mkdir -p data/

echo "
MUSIC_TRACKS = [

    # Favorites.
    'Daft Punk - Musique/09 - Something About Us.mp3',
    'Daft Punk - Musique/07 - One More Time (Radio Edit).mp3',
    'Daft Punk - Musique/08 - Harder, Better, Faster, Stronger.mp3',
    'Shlohmo - Laid Out EP/Shlohmo - Laid Out EP - 02 Out Of Hand.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 13 Krone.mp3',
    'dont.mp3',
    'exit_music.mp3',
    'latch.mp3',
    'SHIGETO - Detroit Part 1.mp3',
    'Floating Points - Ratio (Full Mix).mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 12 Swim.mp3',
    'Shlohmo - Laid Out EP/Shlohmo - Laid Out EP - 01 Dont Say No ft. How To Dress Well.mp3',
    'Shlohmo - Laid Out EP/Shlohmo - Laid Out EP - 03 Later.mp3',
    'bad_guy.mp3',
    'everything_i_wanted.mp3',

    # Rock
    'rock/War_Pigs.mp3',
    'rock/Back_Door_Man.mp3',
    'Nobody_Speak.mp3',
    'Heavy_Balloon.mp3',
    'rock/Immigrant_Song.mp3',
    'rock/Dazed_and_Confused.mp3',
    'rock/Since_Ive_Been_Loving_You.mp3',
    'rock/The_Crystal_Ship.mp3',
    'rock/We_Are_The_Champions.mp3',
    'rock/We_Will_Rock_You.mp3',

    # Christian loffler
    'Christian Löffler - Mare/Christian Löffler - Mare - 01 Myiami.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 02 Haul (feat. Mohna).mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 03 Mosaics.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 04 Neo.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 06 Lid.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 08 Athlete.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 10 Silk.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 11 Nil.mp3',
    'Christian Löffler - Mare/Christian Löffler - Mare - 16 Wilderness (feat. Mohna).mp3',
    'Shlohmo - Laid Out EP/Shlohmo - Laid Out EP - 04 Put It.mp3',
    'Shlohmo - Laid Out EP/Shlohmo - Laid Out EP - 05 Without.mp3',

    # Daft
    'Daft Punk - Musique/02 - Da Funk.mp3',
    'Daft Punk - Musique/03 - Around the World (Radio Edit).mp3',
    'Daft Punk - Musique/05 - Alive.mp3',
    'Daft Punk - Musique/10 - Robot Rock.mp3',
    'Daft Punk - Musique/11 - Technologic (Radio Edit).mp3',
    'Daft Punk - Musique/15 - Digital Love.mp3',

    # Safe.
    'bensound-buddy.mp3',
    'bensound-tomorrow.mp3',
]

MUSIC_TRACKS = ['data/'+m for m in MUSIC_TRACKS]" > data/tracks.py