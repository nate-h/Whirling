# Proposed visual

* Create 2d checkerboard shared by all tracks
* Each track is assigned a color
* The summation of all of these track colors should be white
* These colors may add up past white but will be clipped to white
* Each checkerboard cell will be used to visualize a certain frequency
* Lower frequencies will be visualized near the center of the board while
  higher frequencies near the edge


## RGB color mixing
1. Number of tracks should correspond to number of colors picked
2. The summation of these colors should at least add up to white
3. If colors add up beyond white, colors will be clipped when mixed
   to add up to white

### Algorithm
1. Start off with color
2. Choose 2,3,4th color by selecting colors 90, 180, 270 degrees on color wheel
3. 4 colors should add to (1,1,1) if not higher and get clipped to (1,1,1)


