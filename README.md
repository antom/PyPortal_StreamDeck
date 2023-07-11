# PyPortal StreamDeck

A project to use an [Adafruit PyPortal](https://www.adafruit.com/product/4116) as a 'StreamDeck' - aka. a customisable control pad for a variety of purposes.

## Features

- Buttons can trigger single or multiple keypresses.
- Multiple pages of buttons.
- Different button grid sizes across pages (e.g. 12 buttons in a 4x3 grid on one page, 6 buttons in a 2x3 grid on another etc).
- Page navigation (previous / next / specific).
- Transitions between pages (cut / fade / etc).
- JSON configuration of button mappings, layouts, pages, etc.
- Button states for untouched/touching.
- Optional, customisable splash screen.
- Optional 'Idle' mode (turns off display after a customisable period of inactivity).

## To Do

- Toggle buttons (e.g. Microphone muted/unmuted)
- Further integrations where possible.

## Parts

- [Adafruit PyPortal](https://www.adafruit.com/product/4116)
- [PyPortal StreamDeck 3D Printed Case](https://www.thingiverse.com/thing:5900616) (optional)

## Getting Started

1\. Update the PyPortal to the latest stable release of [CircuitPython](https://circuitpython.org/board/pyportal).

2\. Ensure that the `lib` folder on your PyPortal contains the following [libraries](https://circuitpython.org/libraries):

- **adafruit_touchscreen**
- **adafruit_hid**

3\. Copy the `config` folder to the PyPortal (this contains a `demo` theme by default).

4\. Add the following values to `secrets.py`:

```
    'streamDeckDebug': 0,      # Turn console logs on/off
    'streamDeckUsesWiFi': 1,   # Connect to WiFi if required (e.g. for triggering URL requests)
    'streamDeckTheme': 'demo', # Which theme to use (a corresponding folder needs to exist in `/config`)
```

5\. Copy `streamdeck.py` to the PyPortal.

6\. Rename `streamdeck.py` to `code.py` or copy the supplied `code.py` bootstrap file over to your PyPortal (really handy if you have multiple projects on your PyPortal & want to quick change between them).

## Themes

Themes are used to configure the appearance of the buttons on screen & what they do.

### img folder

This folder holds bitmap files used throughout the theme. Examples of this are:

- `Splash.bmp` - used for the splash screen (filename can be customised).
- `WxH.bmp` - used for the button faces for a particular grid size (`W` = button width, `H` = button height)

As an example, if you want to have a page of buttons on a 4x3 grid, put them in a file called `80x80.bmp`. This is based on the PyPortal's 320x240 display (320 / 4 = 80 & 240 / 3 = 80). They can be positioned as you want & will get a tile index from top-left to bottom-right to use in the settings.

e.g. Having 2x4 button faces in the file:

```
[0][1]
[2][3]
[4][5]
[6][7]
```

### settings.json

This file sets up various customisations for your theme, such as the button faces, pages, layouts & what each button does.

#### Button Faces

Button faces are grouped into button size (`WxH`) & specify what tile index to use for their untouched & touched states. These can then be referred to in the Pages section.

e.g.

```
"buttons": {
	"160x120": {
		"firstButton": [0, 1],
		"secondButton": [2, 3],
		"nextButton": [4, 5]
	},

	"320x60": {
		"button": [0, 1]
	}
},
```

#### Pages

Pages define how to arrange the button faces & what they will control.

Primarily these will be used to trigger:
- Single or multiple `keyCodes` for key presses.
- Changing `page` (next / previous / specific number).
- A HTTP POST `request` to a specific `url` with a `json` request body.

By default, key presses will only be sent once but they can by set to `repeatAfter` a specified number of seconds. If `repeatAfter` is set at the root, it will apply to all buttons but can be overridden by button.

e.g.

```
"pages": [
	[
		[
			{
				"button": "firstButton",
				"keyCodes": "1"
			},
			{
				"button": "firstButton",
				"keyCodes": ["SHIFT", "1"]
			}
		],
		[
			{
				"button": "secondButton",
				"keyCodes": "2",
				"repeatAfter": 2
			},
			{
				"button": "nextPageButton",
				"page": "next"
			}
		],
		[
			{
				"button": "firstButton"
				"request": {
					"url": "https://api.funtranslations.com/translate/yoda.json",
					"json": {
						"text": "The first button on this page was pressed"
					}
				}
			},

			{
				"button": "secondButton"
				"request": {
					"url": "https://api.funtranslations.com/translate/yoda.json",
					"json": {
						"text": "The second button on this page was pressed"
					}
				}
			}
		]
	]
]
```

#### Page

Shared setting for all pages. Specifies what `transition` to use for a page `change` and what to use for the `initial` page shown.

e.g.

```
"page": {
	"transition": {
		"initial": "fade",
		"change": "fade"
	}
},
```

#### Transitions

Allows values for the transitions to be customised - e.g. `step` specifies how much it changes for every update & `speed` defines how quickly each update takes to be made.

e.g.

```
"transitions": {
	"fade": {
		"step": 0.1,
		"speed": 0.05
	}
},
```

#### Splash Screen

Optionally set to display a splash screen when the PyPortal boots up. Can be set to transition in/out for a custom duration.

e.g.

```
"splash": {
	"image": "splash.bmp",
	"duration": 2,
	"transition": "fade"
},
```

#### Idle Mode

Optionally set to transition in/out from displaying anything on the screen if inactive for a specified amount of time. Can also be set to trigger a key press on `enter` or `exit`.

e.g.

```
"idle": {
	"duration": 300,
	"transition": "fade",
	"keyCodes": {
		"exit": "ESCAPE"
	}
},
```
