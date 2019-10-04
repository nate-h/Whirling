################################################################################
## Links.
################################################################################

List of visualizers:
https://github.com/willianjusten/awesome-audio-visualization


Javascript implementation from sonia:
https://github.com/soniaboller/soniaboller.github.io/tree/master/audible-visuals
Audio Visualizer built with THREE.js and Web Audio API

Detecting chorus in python:
https://towardsdatascience.com/finding-choruses-in-songs-with-python-a925165f94a8

Javascript library for working with sound:
https://p5js.org/reference/#/libraries/p5.sound

Hello triangle:
https://www.youtube.com/watch?v=Wyv5TnkFuxE

################################################################################
## Top libs to work with using python.
################################################################################

pyo - music creation library
pip install pychorus


################################################################################
## Ideas for visualizing sounds.
################################################################################

Random Ideas:
* Apply smoothing and interpolation methods to make visuals more orderly
  any signal I can extract won't be perfect
* Volume itself should be a dial for awesomeness
* Need way to visualize everything I can so I can extract patterns

Visual side:
* Colors represent type of sounds you hear
* hsv so can easily interpolate between colors.
* hue, saturation, brightness mean things.
* use 3d world and apply transforms to the objects to make them dance
* pulsing colors in and out
* exploit patterns in songs

Audio side:
* Break song up into frequency bands
* each frequency bands controls has consistent behavior
* Perform texture analysis?
* Attempt to classify song as rock/rap or some more fundamental classifiers?
* Isolate vocals or anything?

Ways to break up song:
Chorus vs non-chorus

################################################################################
## Theory/ terminology:
################################################################################

chromagram - the list of notes playing at any moment
octave - the interval between one musical pitch and another with _double_ its frequency
Chromatic Scale - series of 12 half steps 7 (abcdefg) + 5 (sharp/ flat notes)
piano frequency range - min 27.5 Hz, max 4186.01 Hz
human hearing frequency range - 20Hz to 20000Hz
Nyquist–Shannon sampling - Because of Nyquist–Shannon sampling theorem songs
    are sampled at a rate of 44100Hz so that frequencies up to 22050Hz can be reconstructed.

Chroma - Measures the energy in each pitch class
cqt    - Measures the energy in each pitch
spectral centroid - center of mass for sound
    calculated as the weighted mean of the frequencies
frequency -> mel scale: mel(f) = 2595*log(1+ f/700)


################################################################################
## Random good ideas.
################################################################################

Break song up into 12 notes (western scale)
Define similarity between two slices of time as: 1- ||v1-v2||/root(12)
Results function value of 1 means same notes playing, 0 as different
create a matrix M where M[x][y]=similarity(x, y)

Use matplot lib to graph every thing I want to use as a subplot. chunk up
plot domain into 10 second intervals.

################################################################################
## Feasible tools
################################################################################

Get bpm
Get tempo
Get eq
Get volume of sound
Harmonic-percussive source separation
Chroma vs cqt
chorus vs nonchrous
spectral centroid - center of mass for sound
zero crossing rate