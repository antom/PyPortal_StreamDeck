# PyPortal StreamDeck

A project to use an [Adafruit PyPortal](https://www.adafruit.com/product/4116) as a 'StreamDeck' - aka. a customisable control pad for a variety of purposes.

## Features

- Buttons can send a message via serial that the host can interpret.
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

#### Idle Mode

Optionally set to transition in/out from displaying anything on the screen if inactive for a specified amount of time.

e.g.

```
"idle": {
	"duration": 300,
	"transition": "fade"
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

#### Image

Images define how the button faces are grouped into button size (`WxH`) & specify what tile index to use for their untouched & touched states. These can then be referred to in the Page Layout section.

e.g.

```
"image": {
	"160x120": {
		"topLeftButton": [0, 1],
		"topRightButton": [2, 3],
		"bottomLeftButton": [4, 5],
		"bottomRightButton": [6, 7]
	},

	"320x60": {
		"button": [0, 1]
	}
},
```

#### Button

Defines what behaviour a button performs when triggered.

Button presses can trigger a `next`, `previous` or specific page number change if included in the `pageNavigation` section.

Buttons can be set to send a message to the host via serial if included in the `sendMsg` section. This message can them be interpreted by and acted upon by a suitable background process (e.g. Hammerspoon on Mac).

By default, button will only trigger their action once when  pressed, but they can by set to `repeatAfter` a specified number of seconds. If `repeatAfter` is set at the root, it will apply to all buttons but can be overridden by button.

e.g.

```
"buttons": [
	"pageNavigation": {
		"nextPageButton": "next",
		"previousPageButton": "previous",
		"goToFirstPageButton": 0
	},

	"sendMsg": [
		"firstAction",
		"secondAction"
	],

	"repeatAfter": {
		"repeatingButton": 2
	}
]
```

#### Page

Defines the layouts & shared setting for all pages. Specifies what `transition` to use for a page `change` and what to use for the `initial` page shown.

e.g.

```
"page": {
	"transition": {
		"initial": "fade",
		"change": "fade"
	},

	"layout": [
		[
			[
				"topLeftButton",
				"topRightButton"
			],

			[
				'bottomLeftButton',
				'bottomRightButton'
			]
		]
	]
},
```

#### Keyboard Key Codes

This section defines any single or multiple keyboard keycodes to send to the host for particular actions such as button presses or entering/exiting Idle Mode.

```
"keyCodes": {
	"idle": {
		"exit": "ESCAPE"
	},

	"buttons": {
		"oneButton": "1",
		"exclamationMarkButton": ["SHIFT", "1"]
	}
},
```
