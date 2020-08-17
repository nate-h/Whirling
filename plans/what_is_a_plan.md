A plan is
=========

A plan is a programmatic way of specifying what visualizers should be used
and what data should be generated for each visualizer/ track combination.

Running a plan
--------------

When Whirling is launched and a plan is specified like
`run_whirling --plan default_plan`,
this tells Whirling to look for a precached pickle that contains the extracted
features and segmented tracks for the current track. This pickle file
will be saved along side the track with the same basename but with the plan
name added and the `.p` pickle extension. If one doesn't exist, Whirling will
stop and generate the missing pickle file.

Note
----

When a plan is ran on a track, the resulting pickle file will be quite large
relative to the track. Things like spectrograms generated per each segmented
track take up a lot of space.
