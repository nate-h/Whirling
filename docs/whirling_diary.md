My highs and lows while creating this
=====================================

What this program was supposed to be
------------------------------------

A music visualizer that's smart enough to build visuals based on what
instruments, vocals were present. Music visualizers typically operate on the
whole spectrogram of the song.

It turned into a learning opportunity with a side consequence of the goal

--------------------------------------------------------------------------------
-- Opengl + slowness of drawing checkboard
--------------------------------------------------------------------------------

Opengl
------

Wrote using pygame primitives and hit speed limit
Started rewriting in opengl
Iterated several times getting stuff to run faster till I figured out how to use vbos

Creating mini-library of opengl helpers.

## Spectrogram optimizing.

1. Originally took 1.7 seconds to generate vbo to render.
2. Cut it in half by caching the my modifications to the original spectrogram data.
3. After optimize indices -> .75 seconds
4. Perform log_db_s normalization outside of for loop -> .61 seconds
5. use numpy to generate entire color vertex array -> .32 seconds
6. Use 0->99 as indices into cmap -> .18 seconds
7. Remove rounding in rectangle generation -> 0.095 seconds


--------------------------------------------------------------------------------

Spectrogram
-----------

Multi-thread or multi-processor
Log axis stuff

Tools
-----

Explain a little bit about each of these technologies
librosa
spleeter
rxpy


What I've learned
-----------------

How to set up python packages
how to operate on sound
how to use all my knowledge
more mathy stuff
Don't blame the lib or framework, blame your bad code


Viridis slowness
----------------

Had to recreate viridis because using cmaps was slow.


Failing to realize extent of project
------------------------------------

Failed to realize what I was creating and built many features to do precisely
what I needed at the time. When more was needed, I had to rebuild that feature.


----------------------------------------------

Random thought:

Something that's distinct to your ears is not distinct to the data
I would love to create a visualizer that captures the vibrato of a voice or the decay on a cymbal