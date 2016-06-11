# FabulousToolsForNuke

This is and will hopefully continue to be a repository for Nuke tools that I've created.

-- TrackConnect.py
  - Creates a Nuke panel called TrackConnect that will create a new Roto or RotoPaint node with tracking attached to a new layer in the    node. Allows the individual selection of translation, rotation and scale with the option to bake or parent the tracking data into the   node.

-- RetimeCamera.py
  - Given Camera/Axis and OFlow/Kronos nodes, will retime the translation and rotation curve of the Camera node based on retime curve.
    Retimed Camera node will be a copy leaving original intact.
    Please note:
    If retime method is speed-based, the script will copy retime node and convert to frame-based before applying curve to camera. 
    This script has not been exhaustively tested. If any issues arise from usage, please leave a comment and I will address in a later version.
    At the moment, copied Camera and OFlow nodes may still have downstream connections. This is something I will address in ver1.3. In the meantime, either remove Camera and/or OFlow from tree before running script or place a dot directly downstream from the node.

  TrackConnect has been pretty extensively tested, mostly by myself, but I cannot vouch for it's overall stability. I will be updating this over time.
  RetimeCamera however is still being tested. It may prove overall somewhat finicky as I still need to make several updates to it.
  
  That is all for now!
