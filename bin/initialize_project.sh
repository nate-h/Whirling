#!/bin/bash

mkdir -p data/

echo "MUSIC_TRACKS = [
    'latch.mp3',
    'exit_music.mp3',
]

MUSIC_TRACKS = ['data/'+m for m in MUSIC_TRACKS]" > data/tracks.py