import adafruit_touchscreen
import board
import displayio
import gc
import json
import math
import time
import adafruit_imageload
import usb_cdc

from secrets import secrets

debugging = secrets.get('streamDeckDebug', 0)

# Theme Configuration
theme = secrets.get('streamDeckTheme', 'Default')

with open('/config/{}/settings.json'.format(theme)) as themeJSON:
	themeConfig = json.load(themeJSON)

pageLayout = themeConfig.get('page', {}).get('layout', {})

# Keyboard Configuration
hasKeyCodes = 0

if themeConfig.get('keyCodes', None) is not None:
	hasKeyCodes = 1

	import usb_hid

	from adafruit_hid.keyboard import Keyboard
	from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
	from adafruit_hid.keycode import Keycode

# Image Configuration
imgPath = '/config/{}/img/'.format(theme)

# Functions
def log(value):
	if debugging:
		print(str(value))

def sendMsg(type, value):
	usb_cdc.data.write(type + ': ' + str(value) + "\r\n")

def hasElapsedSince(duration, time):
	return int(duration is not None and currentTime >= (time + duration))

def loadImage(filePath, loadFromDisk = 1):
	gc.collect()

	if loadFromDisk:
		img = displayio.OnDiskBitmap(
			imgPath + filePath
		)
		pixelShader = img.pixel_shader
	else:
		img, pixelShader = adafruit_imageload.load(
			imgPath + filePath
		)

	return {
		'img': img,
		'pixelShader': pixelShader
	}

def getCurrentTouch():
	time.sleep(0.05)
	touch = touchScreen.touch_point

	if touch:
		return {
			'x': math.floor(touch[0] / (board.DISPLAY.width / getPageColumns(currentPage))),
			'y': math.floor(touch[1] / (board.DISPLAY.height / getPageRows(currentPage)))
		}
	else:
		return {
			'x': None,
			'y': None
		}

def getCurrentButton():
	return pageLayout[currentPage][currentTouch['y']][currentTouch['x']]

def getKeyCode(value):
	return getattr(Keycode, value)

def sendKeyCodes(keyCodes):
	if keyCodes is None:
		return
	elif type(keyCodes) is list:
		keyboard.send(
			*map(getKeyCode, keyCodes)
		)
	elif type(keyCodes) is str:
		keyboard.send(
			getKeyCode(keyCodes)
		)

def getPageRows(page):
	return len(pageLayout[page])

def getPageColumns(page):
	return len(pageLayout[page][0])

def getTileWidth(page):
	return math.floor(board.DISPLAY.width / getPageColumns(page))

def getTileHeight(page):
	return math.floor(board.DISPLAY.height / getPageRows(page))

def setBacklight(value: float):
	value = max(0, min(1.0, value))
	board.DISPLAY.brightness = value
	log(
		'setBacklight({0})'.format(board.DISPLAY.brightness)
	)

def transitionIn(transitionType):
	if transitionType is None:
		return

	if transitionType is 'cut':
		setBacklight(1)

	if transitionType is 'fade':
		fadeTo(1)

def transitionOut(transitionType):
	if transitionType is None:
		return

	if transitionType is 'cut':
		setBacklight(0)

	if transitionType is 'fade':
		fadeTo(0)

def fadeTo(value, startFrom = None):
	transitionStep = themeConfig.get('transitions', {}).get('fade', {}).get('step', 0.1)
	transitionSpeed = themeConfig.get('transitions', {}).get('fade', {}).get('speed', 0.05)

	if startFrom is None:
		startFrom = board.DISPLAY.brightness

	if startFrom != board.DISPLAY.brightness:
		startFrom = float(startFrom)
		setBacklight(startFrom)
		time.sleep(transitionSpeed)

	if value > startFrom:
		while board.DISPLAY.brightness < value:
			setBacklight(board.DISPLAY.brightness + transitionStep)
			time.sleep(transitionSpeed)
	elif value < startFrom:
		while board.DISPLAY.brightness > value:
			setBacklight(board.DISPLAY.brightness - transitionStep)
			time.sleep(transitionSpeed)

def getBtnTileGrid(tileWidth, tileHeight):
	log(
		'getBtnTileGrid({0}, {1})'.format(tileWidth, tileHeight)
	)

	btns = loadImage(
		'{0}x{1}.bmp'.format(tileWidth, tileHeight),
		themeConfig.get('page', {}).get('loadFromDisk', 1)
	)

	return displayio.TileGrid(
		btns['img'],
		pixel_shader = btns['pixelShader'],
		width = math.floor(board.DISPLAY.width / tileWidth),
		height = math.floor(board.DISPLAY.height / tileHeight),
		tile_width = tileWidth,
		tile_height = tileHeight
	)

def setTile(touch, state = 0):
	if type(touch['x']) is int and type(touch['y']) is int:
		size = '{0}x{1}'.format(getTileWidth(currentPage), getTileHeight(currentPage))
		btn = pageLayout[currentPage][touch['y']][touch['x']]
		displayGroup[0][touch['x'], touch['y']] = themeConfig['image'][size][btn][state]

def setPage(index):
	global currentPage

	pageLayout = themeConfig.get('page', {}).get('layout', {});

	if index < 0 or index >= len(pageLayout):
		return

	previousPage = currentPage
	currentPage = index

	if previousPage is None:
		displayGroup.append(
			getBtnTileGrid(
				getTileWidth(currentPage),
				getTileHeight(currentPage)
			)
		)
	elif getPageRows(currentPage) != getPageRows(previousPage) or getPageColumns(currentPage) != getPageColumns(previousPage):
		displayGroup[0] = getBtnTileGrid(
			getTileWidth(currentPage),
			getTileHeight(currentPage)
		)

		gc.collect()

	log('setPage({})'.format(currentPage))

	refreshAfterTileUpdate = int(themeConfig.get('page', {}).get('transition', {}).get('change', None) == 'tile')

	for tileY in range(0, getPageRows(currentPage)):
		for tileX in range(0, getPageColumns(currentPage)):
			setTile({
				'x': tileX,
				'y': tileY
			})

			if refreshAfterTileUpdate:
				board.DISPLAY.refresh()

	if not refreshAfterTileUpdate:
		board.DISPLAY.refresh()

def prevPage():
	if currentPage > 0:
		setPage(currentPage - 1)
	else:
		setPage(len(pageLayout) - 1)

def nextPage():
	if currentPage < len(pageLayout) - 1:
		setPage(currentPage + 1)
	else:
		setPage(0)

def displaySplashScreen():
	if themeConfig.get('splash', None) is None:
		return

	log('displaySplashScreen()')

	setBacklight(0)

	splash = loadImage(
		themeConfig.get('splash', {}).get('image', 'Splash.bmp'),
		themeConfig.get('splash', {}).get('loadFromDisk', 1)
	)

	splashGrid = displayio.TileGrid(
		splash['img'],
		pixel_shader = splash['pixelShader']
	)

	displayGroup.append(
		splashGrid
	)

	board.DISPLAY.refresh()

	transitionIn(
		themeConfig.get('splash', {}).get('transition', 'fade')
	)

	time.sleep(
		themeConfig.get('splash', {}).get('duration', 3)
	)

	transitionOut(
		themeConfig.get('splash', {}).get('transition', 'fade')
	)

	displayGroup.remove(
		splashGrid
	)

	board.DISPLAY.refresh()

# Turn off display auto refreshing
board.DISPLAY.auto_refresh = 0

# Initialise touchscreen
touchScreen = adafruit_touchscreen.Touchscreen(
	board.TOUCH_XL,
	board.TOUCH_XR,
	board.TOUCH_YD,
	board.TOUCH_YU,
	calibration = (
		(5200, 59000),
		(5800, 57000)
	),
	size = (
		board.DISPLAY.width,
		board.DISPLAY.height
	)
)

# Initialise keyboards (if acting as a keyboard)
if hasKeyCodes:
	keyboard = Keyboard(usb_hid.devices)
	keyboard_layout = KeyboardLayoutUS(keyboard)

# Initialise display group
displayGroup = displayio.Group()

board.DISPLAY.root_group = displayGroup

# Show splash image on startup
displaySplashScreen()

# Turn backlight off
if board.DISPLAY.brightness > 0:
	setBacklight(0)

# Configure initial values
currentPage = None
currentTouch = getCurrentTouch()
previousTouch = currentTouch
currentButton = None
previousButton = None
timeTouched = None
idleMode = 0
idleDuration = themeConfig.get('idle', {}).get('duration', None)

setPage(0)

initialPageTransition = themeConfig.get('page', {}).get('transition', {}).get('initial', 'cut')

if initialPageTransition == 'tile':
	initialPageTransition = 'cut'

transitionIn(
	initialPageTransition
)

timeStateChanged = time.monotonic()

# main loop
while True:
	currentTime = time.monotonic()

	# make a note of the previous touch state
	previousTouch = currentTouch

	# get the current touch state
	currentTouch = getCurrentTouch()

	# check & handle entering/exiting idle state
	if hasElapsedSince(idleDuration, timeStateChanged):
		if not idleMode and currentTouch['x'] is None and currentTouch['y'] is None:
			log('idleEnter')

			idleMode = 1

			transitionOut(
				themeConfig.get('idle', {}).get('transition', 'fade')
			)

			sendKeyCodes(
				themeConfig.get('keyCodes', {}).get('idleEnter', None)
			)

			sendMsg(
				'idle',
				'enter'
			)

			continue
		elif idleMode and type(previousTouch['x']) is int and type(previousTouch['y']) is int:
			log('idleExit')

			idleMode = 0

			sendKeyCodes(
				themeConfig.get('keyCodes', {}).get('idleExit', None)
			)

			sendMsg(
				'idle'
				'exit'
			)

			transitionIn(
				themeConfig.get('idle', {}).get('transition', 'fade')
			)

			currentTime = time.monotonic()
			timeStateChanged = currentTime

			continue

	# check button up - reset stuff when the touch has been released
	if previousTouch != currentTouch and type(previousTouch['x']) is int and type(previousTouch['y']) is int:
		timeStateChanged = currentTime

		setTile(
			previousTouch
		)

		board.DISPLAY.refresh()

		# if a previously-touched button is used for pagination, trigger it
		if previousButton and currentTouch['x'] is None and currentTouch['y'] is None:
			buttonPage = themeConfig.get('button', {}).get('pageNavigation', {}).get(previousButton, None)

			if buttonPage is not None:
				transitionOut(
					themeConfig.get('page', {}).get('transition', {}).get('change', None)
				)

				# perform a pagination action if pagination is enabled
				if buttonPage in ['prev', 'previous']:
					prevPage()
				elif buttonPage == 'next':
					nextPage()
				elif type(buttonPage) is int:
					setPage(buttonPage)

				transitionIn(
					themeConfig.get('page', {}).get('transition', {}).get('change', None)
				)

				currentTime = time.monotonic()
				timeStateChanged = currentTime

		previousButton = None
		timeTouched = None

	# check button down - trigger actions when current/previous touches match (helps to filter out inconsistencies)
	elif previousTouch == currentTouch and type(currentTouch['x']) is int and type(currentTouch['y']) is int:
		timeStateChanged = currentTime

		if timeTouched is None:
			timeTouched = currentTime

		# get the current button
		currentButton = getCurrentButton()

		# unless specified to repeat after a defined delay, skip triggering the button if we've previously triggered it
		if currentButton == previousButton:
			repeatAfter = themeConfig.get('button', {}).get('repeatAfter', {}).get(previousButton, None)

			if hasElapsedSince(repeatAfter, timeTouched):
				timeTouched = currentTime
			else:
				continue


		# set the tile for the button currently being touched
		setTile(
			currentTouch,
			1
		)

		board.DISPLAY.refresh()

		# send communication (as serial message or keycodes)
		sendsMsg = currentButton in themeConfig.get('button', {}).get('sendMsg', [])

		if sendsMsg:
			sendMsg(
				'btn',
				currentButton
			)
		else:
			sendKeyCodes(
				themeConfig.get('keyCodes', {}).get(currentButton, None)
			)

		# make a note of what button we've just used
		previousButton = currentButton
