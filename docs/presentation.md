Visuals

# Intro

Technologies
* numpy        fast array manipulation
* spleeter     music segmentation
* librosa      music and audio analysis tools + music segmentation
* PyOpenGL     OpenGL python bindings
* pygame       python game development modules
* python-vlc   media player backend
* rx           subject / observer implementation for handling events
* sklearn      machine learning lib
* jupyter      an interactive gui for writing python
* matplotlib   plotting
* schema       json validator

Learn audio
Data cached before hand
Demo

# Debug

onset_strength: spectral flux onset strength envelope
                Useful for determining the points in time where a sound starts
spectral centroid: average of frequencies you're hearing - center of mass of spectrum
spectral_flatness: a measure of how noisy a signal is
zero crossing rate: rate as which signal changes signs


# Spectrogram

What is a spectrogram

1. Originally took 1.7 seconds to generate vbo to render.
2. Cut it in half by precaching the creation of log y axis spectrogram
3. use np to generate rectangles indices -> .75 seconds
4. Perform log_db_s normalization outside of for loop -> .61 seconds
5. use numpy to generate entire color vertex array -> .32 seconds
6. Use 0->99 as indices into cmap -> .18 seconds
7. Remove rounding in rectangle generation -> 0.095 seconds

# Different filtering techniques

High passes to root out faint sounds
Rolling averages: tried simple unweighted ones and more complicated ones
Scaling up different audio segmentations - simple linear multiplier
keep_biggest - only showing nth loudest frequency bin * damper
keep_biggest round 2 - dynamic high pass calculated from loudest frequency * threshold

-------------------------------
Problem with each one of these filters


# Closing

Tambre
generalized audio segmentation