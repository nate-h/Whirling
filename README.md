# README.md

## How to get project up and running.
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