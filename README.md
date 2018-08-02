<!--- // cSpell:words killboard, blops, hics, killboard's, cynos, ccp's, pyspy, psf's, pyperclip, pyinstaller, executables, jojo, unported, killmails --->

# PySpy - A simple EVE Online character intel tool using CCP's ESI API

<p align="left">
  <a href=https://github.com/WhiteRusssian/PySpy/releases/latest>
    <img alt="Current Version" src="https://img.shields.io/github/release/whiterusssian/pyspy.svg">
  </a>
  <a href=https://github.com/WhiteRusssian/PySpy/releases/latest>
    <img alt="Number of releases downloaded" src="https://img.shields.io/github/downloads/WhiteRusssian/PySpy/total.svg">
  </a>
</p>

**Download the latest release [here](https://github.com/WhiteRusssian/PySpy/releases/latest).**

## Background

PySpy was born out of frustration over the *death* of [Pirate's Little Helper](http://eve-plh.com/#/home),
a great [EVE Online](https://www.eveonline.com/) third-party tool for gathering useful information on character names from the in-game *local chat* window.

PySpy connects to [CCP's ESI API](https://esi.evetech.net/ui/) and the
[zKillboard API](https://github.com/zKillboard/zKillboard/wiki) and is available on Windows, macOS and Linux.

## How to use PySpy

1. Open PySpy.
2. In your EVE client, select a list of characters and copy them to the clipboard (`CTRL+C` on Windows *or* `⌘+C` on macOS).
3. Wait until PySpy is done and inspect the results.
4. Double-click a name to open the respective zKillboard in your browser.

**Note**: PySpy will save its window location, size, column sizes, sorting order and transparency (slider on bottom right) and any other settings automatically and restore them the next time you launch it. If selected in the _View Menu_, PySpy will stay on top of the EVE client so long as the game runs in *window mode*.

## Information Provided by PySpy

### New Dark Mode
<p align="center">
  <img alt="PySpy in action" src="https://github.com/WhiteRusssian/PySpy/blob/master/assets/v0.3_dark_screenshot.png?raw=true">
</p>

### Traditional Normal Mode
<p align="center">
  <img alt="PySpy in action" src="https://github.com/WhiteRusssian/PySpy/blob/master/assets/v0.3_light_screenshot.png?raw=true">
</p>

* **Character**: Character name.
* **Security**: Concord security status.
* **Corporation**: Corporation of character.
* **Alliance**: Alliance of character's Corporation, if any.
* **Faction**: Faction of character, if any.
* **Kills**: Total number of kills.
* **Losses**: Total number of losses.
* **Last Wk**: Number of kills over past 7 days.
* **Solo**: Ratio of solo kills over total kills.
* **BLOPS**: Number of Black Ops Battleships (BLOPS) killed.
* **HICs**: Number of lost Heavy Interdiction Cruisers (HIC).

**Current Limitations**: To avoid undue strain on zKillboard's API, PySpy will run the *Kills*, *Losses*, *Last Wk*, *Solo*, *BLOPS* and *HICs* analyses only for the first 30 characters in the list.

## Ignore Certain Entities

PySpy allows you to specify a list of ignored characters, corporations and alliances. To add entities to that list, right click on a search result. You can remove entities from this list under _Options_->_Review Ignored Entities_

## Ignore all Members of your NPSI Fleet

For anyone using PySpy in no-purple-shoot-it (NPSI) fleets, you can tell PySpy to temporarily ignore your fleet mates by first running PySpy on all characters in your fleet chat and the selecting _Options_->_Set NPSI Ignore List_. Once the fleet is over, you can clear the list under _Options_->_Clear NPSI List_. Your custom ignore list described above will not be affected by this action.

## Installation

You can download the latest release for your operating system [here](https://github.com/WhiteRusssian/PySpy/releases/latest).

PySpy comes as a single-file executable both in Windows and macOS. On both platforms, you can run PySpy from any folder location you like.

On Linux, you can run PySpy like any other Python3 script. PySpy was developed on Python 3.6.5 but should run on any other Python3 version, so long as you install the required packages listed in [requirements.txt](https://github.com/WhiteRusssian/PySpy/blob/master/requirements.txt).

**Note**: PySpy automatically checks for updates on launch and will notify you if a new version is available.

## Uninstalling PySpy

Delete the PySpy executable and remove the following files manually:

* **Windows**: PySpy saves preference and log files in a folder called  `PySpy` located at `%LocalAppData%`.
* **macOS**: PySpy creates `pyspy.log` under `~/Library/Logs` and `pyspy.cfg` as well as `pyspy.pickle` under `~/Library/Preferences`.
* **Linux**: PySpy creates `pyspy.log` under `~/Library/Logs` and `pyspy.cfg` as well as `pyspy.pickle` under `~/.config/pyspy`.

## Future Features

Below is a non-exhaustive list of additional features I plan to add to PySpy as and when the ESI and zKillboard APIs support them:

* **Cynos**: Indicate if a character has in the past lost ships fitted with regular or covert cynos. I am currently putting together the underlying database of killmails and expect to add this feature in August.
* **Average Attackers**: Average number of attackers across all kills a character has been involved in.
* **Abyssal Losses**: Show number of losses in abyssal sites.
* **Custom Highlighting**: Choose a list of characters, corproations or alliances to highlight.
* **Standings**: Only show characters that are non-blue, i.e. neutral or hostile.
* **Highlight New Pilots**: Highlight any pilots that have entered system since last PySpy run.
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
* PySpy's icon was created by Jojo Mendoza and is licensed under [Creative Commons (Attribution-Noncommercial 3.0 Unported)](https://creativecommons.org/licenses/by-nc/3.0/). It is available on [IconFinder](https://www.iconfinder.com/icons/1218719/cyber_hat_spy_undercover_user_icon).

## License

PySpy is licensed under the [MIT](LICENSE.txt) License.

## CCP Copyright Notice

EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. CCP is in no way responsible for the content on or functioning of this website, nor can it be liable for any damage arising from the use of this website.

## Collection of Usage Statistics

To help improve PySpy further, PySpy reports usage statistics comprising certain anonymous information such as the number of characters analysed, duration of each analysis, operating system, version of PySpy, and any active GUI features. For full disclosure, a randomly generated identifier is being sent with each data set to allow me to track how many people are actually using PySpy over any given period. If you would like to see for yourself what is being collected, have a look at the source code of module `reportstats.py`.