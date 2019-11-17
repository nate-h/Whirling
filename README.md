# README.md

## How to get project up and running.
```console

# Needed for librosa
sudo apt-get install vlc ffmpeg

# Install env and activate it.
virtualenv -p python3 Whirling
source ./Whirling/bin/activate

# Install python dependencies
pip install -e .

# Initialize data folder with sample tracks file.
./bin/initialize_project.sh

# Give it a whirl!
run_whirling

# Misc.
# Audio features cache so start program with:
run_whirling --use-cache --move-window

```