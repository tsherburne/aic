# AI Challenge (AIC)

## Magic Draw SysML Model Files

* [aic.mdzip](https://github.com/tsherburne/aic/blob/main/aic.mdzip) (**AIC Model** in Magic Draw Zip format)
  * [SysML Overview Tutorial](https://www.youtube.com/playlist?list=PLKz_xsS_duotA7ZA5QZ_sESHZQL-HWFym) (YouTube Video Series)
  * [Magic Systems of Systems Architect](https://docs.nomagic.com/display/MSOSA2024x)
* [aic.xml](https://github.com/tsherburne/aic/blob/main/aic.xml) (**AIC Model** in XMI format - XML Model Interchange)
  * See: https://www.omg.org/spec/XMI/

## Magic Draw Web Publish Model
https://tsherburne.github.io/aic/

---
![AIC ConOps](https://tsherburne.github.io/aic/index_files/_2024x_131803cf_1718126112750_459352_4368.jpg)


## What is the simulator used for

The simulator created for the purposes of allowing participants of the Trusted AI Challenge to interact with an environment represented of the problem they have been asked to solve.

The largest feature of the simulator is the interactable Hex Grid. These hexes are dynamically read in through a JSON file, and each tile represents equally sized spaces of land. Each
tile has a designated terrain type and can be traversed by the number of tools at the user's disposal. Clicking on a tile will select it as the current tile where information can be
viewed and obtained.

2 UAVs are available to survey these regions. Once surveyed, the user can query the AI associated with the surveyed UAV as well as gather a human estimate. These estimates resemble the
confidence that a mine is located on the given tile.

A UGV is also present which moves alongside a hypothetical troop of soldiers. The UGV is able to detect and clear mines, though doing so is costly.

The goal of the simulator is to get from the starting tile to the ending tile with the minimal cost.

## Running the Simulator
1. Begin by standing up a Python virtual environment
`python -m venv venv`

Windows:
`source ./venv/Scripts/activate`
Linux/macOs
`source ./venv/bin/activate`

`pip install -r requirements.txt`

2. Run the simulator
`cd minedetection`
`python renderer.py`

In order to reset the simulator, close the window and rerun the previous command.

### Simulator Notes

The simulator by default has the path to the example config file coded into renderer.py when the Mission object is created. This can be updated to reflect newly created scenarios as you wish.

The provided simulator is a starting point for the application. Feel free to alter the codebase as you see fit in order to complete the task at hand.