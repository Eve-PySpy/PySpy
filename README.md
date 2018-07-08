<!--- // cSpell:words killboard, blops, hics, killboard's, cynos, ccp's, pyspy, psf's, pyperclip, pyinstaller, executables, jojo, unported --->

# PySpy - A simple EVE Online character intel tool using CCP's ESI API

## Background

PySpy was born out of frustration over the *death* of [Pirate's Little Helper](http://eve-plh.com/#/home),
a great [EVE Online](https://www.eveonline.com/) third-party tool for gathering useful information on character names from the in-game *local chat* window.

PySpy connects to [CCP's ESI API](https://esi.evetech.net/ui/) and the
[zKillboard API](https://github.com/zKillboard/zKillboard/wiki) and is available on Windows and macOS.

## How to use PySpy

1. Open PySpy.
2. In your EVE client, select a list of characters and copy them to the clipboard (`CTRL+C` on Windows *or* `⌘+C` on macOS).
3. Wait until PySpy is done and inspect the results.
4. Double-click a name to open the respective zKillboard in your browser.

**Note**: PySpy will save its window location, size, column sizes and transparency (slider on bottom right) settings automatically and restore them the next time you launch it. PySpy will stay on top of the EVE client so long as the game runs in *window mode*.

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

**Current Limitations**: To avoid undue strain on zKillboard's API, PySpy will run the *K-B-H* analysis only for the first 20 characters in the list.

## Installation

You can download the latest release for your operating system [here](https://github.com/WhiteRusssian/PySpy/tree/master/download).

PySpy comes as a single-file executable both in Windows and macOS. On both platforms, you can run PySpy from any folder location you like.

**Note**: PySpy automatically checks for updates on launch.

## Uninstalling PySpy

Delete the PySpy executable and remove the following files manually:

* **Windows**: PySpy saves preference and log files in a folder called  `PySpy` located at `%LocalAppData%`.
* **macOS**: PySpy creates `pyspy.log` under `~/Library/Logs` and `pyspy.cfg` under `~/Library/Preferences`.

## Future Features

Below is a non-exhaustive list of additional features I plan to add to PySpy as and when the ESI and zKillboard APIs support them:

* **Standings**: Only show characters that are non-blue, i.e. neutral or hostile.
* **Cynos**: Indicate if a character has in the past lost ships fitted with regular or covert cynos.
* **Improved GUI**: The current GUI is very basic and while it works, I do appreciate that it is not ideal for people who cannot use it on a second screen but actually have to overlay it on-top of their EVE client.

Please feel free to add a [feature request](https://github.com/WhiteRusssian/PySpy/issues/new?template=pyspy-feature-request.md) for any improvements you would like to see in future releases.

## Bug Reporting

Despite PySpy's simplicity and extensive testing, you may encounter the odd bug. If so, please check if an existing [issue](https://github.com/WhiteRusssian/PySpy/issues) already describes your bug. If not, feel free to [create a new issue](https://github.com/WhiteRusssian/PySpy/issues/new?template=pyspy-bug-report.md) for your bug.

## Dependencies & Acknowledgements

* PySpy is written in [Python 3](https://www.python.org/) (v3.6.5), licensed under [PSF's License Agreement](https://docs.python.org/3/license.html#psf-license-agreement-for-python-release).
* For API connectivity, PySpy relies on [Requests](http://docs.python-requests.org/) (v2.19.1), licensed under the [Apache License, Version 2.0](http://docs.python-requests.org/en/master/user/intro/#requests-license).
* Clipboard monitoring is implemented with the help of [pyperclip](https://github.com/asweigart/pyperclip) (v1.6.2), licensed under the [3-Clause BSD License](https://github.com/asweigart/pyperclip/blob/master/LICENSE.txt).
* The GUI is powered by [wxPython](https://www.wxpython.org/) (v4.0.3), licensed under the [wxWindows Library Licence](https://wxpython.org/pages/license/index.html).
* The Windows and macOS executables are built using [pyinstaller](https://www.pyinstaller.org/), licensed under [its own modified GPL license](https://raw.githubusercontent.com/pyinstaller/pyinstaller/develop/COPYING.txt).
* PySpy's icon was created by Jojo Mendoza and is licensed under [Creative Commons (Attribution-Noncommercial 3.0 Unported)](https://creativecommons.org/licenses/by-nc/3.0/). It is available on https://www.iconfinder.com/icons/1218719/cyber_hat_spy_undercover_user_icon.

## License

PySpy is licensed under the [MIT](LICENSE.txt) License.

## CCP Copyright Notice

EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. CCP is in no way responsible for the content on or functioning of this website, nor can it be liable for any damage arising from the use of this website.
