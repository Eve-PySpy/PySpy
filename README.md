# PySpy - A simple EVE Online character intel tool using CCP's ESI API

## Background

PySpy was born out of frustration over the *death* of [Pirate's Little Helper](http://eve-plh.com/#/home),
a great [EVE Online](https://www.eveonline.com/) third-party tool to gather useful information on character names from the in-game *local chat* window.

PySpy connects to [CCP's ESI API](https://esi.evetech.net/ui/) and
[zKillboard's API](https://github.com/zKillboard/zKillboard/wiki) and is available on Windows and macOS.

## How to use PySpy

1. Open PySpy, position the window and adjust transparency (bottom left slider). PySpy will stay on top of the EVE client so long as the game runs in *window mode*.
2. In your EVE client, select a list of characters and copy them to the clipboard (Mac: `⌘+C` / Windows: `CTRL+C`)
3. Wait until PySpy is done and inspect the results.
4. Double-click a name to open the respective zKillboard in your browser.

## Information Provided by PySpy

<p align="center">
  <img alt="PySpy in action" src="https://github.com/WhiteRusssian/PySpy/blob/master/assets/v0.1_screenshot.png?raw=true">
</p>

* **Character**: Character name.
* **Corporation**: Corporation of character.
* **Alliance**: Alliance of Character's Corporation, if any.
* **K**: Total number of kills.
* **B**: Number of Black Ops Battleships (BLOPS) killed.
* **H**: Number of lost Heavy Interdiction Cruisers (HIC).

**Note**: Characters that have killed BLOPS or have lost HICs are high-lighted *orange*.

## Installation

PySpy comes as a single-file executable both in Windows and macOS. On both platforms, you can run PySpy from any folder location you like.

You can download the latest version here:
* **Windows**:
* **macOS**:

## How to uninstall

Delete the PySpy executable and remove the following files manually:

* **Windows**: PySpy saves preference and log files in a folder called  `PySpy` located at `%LocalAppData%`.
* **macOS**: PySpy creates `pyspy.log` under `~/Library/Logs` and `pyspy.cfg` under `~/Library/Preferences`.

## Bug Reporting

Despite PySpy's simplicity and relatively extensive testing, you may encounter the odd bug. If so, please check if an existing [issue](https://github.com/WhiteRusssian/PySpy/issues) describes your bug. If not, feel free to [create a new issue](https://github.com/WhiteRusssian/PySpy/issues/new?template=bug_report.md) for your bug.

## License

Licensed under the [MIT](LICENSE.txt) License.

## CCP Copyright Notice

EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. CCP is in no way responsible for the content on or functioning of this website, nor can it be liable for any damage arising from the use of this website.