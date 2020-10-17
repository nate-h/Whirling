Whirling - music visualization with a bit of AI
===============================================

Intro
-----

Whirling is a music visualizer that tries to intelligently understand as much about the song that's playing so it could create more representative visuals. It currently has 6 visuals that can be sorted into debug visualizers and fun attempts. This is a project I did for the pure fun of coding and great learning experience!

[View demo on Vimeo](https://vimeo.com/454955980)

![Whirling Visuals](snapshots/tiled_image.png "Whirling Visuals" )

How it works and some background
--------------------------------

All songs played have to undergo a two step preprocessing algorithm that runs a source separator and a feature extractor on each of the generated sources. This is accomplished using Spleeter and Librosa. Spleeter is able to separate the drums, vocals, bass and other for each track. Librosa can separate the percussion and harmonics. For feature extracting, I use Librosa exclusively.

I haven't worked extensively with python for GUI/game development so I decided to use pygame and opengl for creating the visualizer. I thought it would be a good learning experience to gauge the python based gui/game development tools out there. What it turned into was a good understanding on how to use numpy for large array manipulation and opengl for VAO  rendering.

Brief description of each visualizer
------------------------------------

I have 6 visualizers that can be cycled through. Visualizers 1, 4 and 6 make heavy use of moving averages, thresholds and other heuristics to get the colors to render just right. Visualizers 1 and 4->6 use the same colors to represent the separated source that's heard. See color key below for color mappings.

1. combo_board: Uses both spectrograms and features to render a grid of squares. Each illuminated square represents a certain frequency range heard. Squares near the top right of the screen map to higher frequencies. The color of that square represents what source it came from.
2. debug: Shows all features generated for current source separation plan.
3. spectrogram: Shows all spectrograms generated for current source separation plan.
4. concentric_squares: Uses the source separated spectrograms to render concentric square rings that represent what frequency is being played. The bigger the ring, the higher the frequency. Ring color matches source heard. This visualizer combines colors if 2+ sources are playing the same frequency.
5. stacked_equalizers: Show all frequencies heard with no adjustments.
6. checkerboard: same as combo_board but with no use of features and much less filtering.

How to get project up and running.
----------------------------------

```sh
    # Needed for librosa
    sudo apt-get install vlc ffmpeg

    # Install env and activate it.
    virtualenv -p python3 Whirling
    source ./Whirling/bin/activate

    # Install python dependencies
    pip install -e .

    # Initialize data folder with sample tracks file.
    ./bin/initialize_project.sh

    # Preprocess all songs in tracks file.
    run_cache_tracks

    # Give it a whirl!
    run_whirling --use-cache

    # Misc: How I run the program.
    run_whirling --use-cache --move-window --plan default_plan
```