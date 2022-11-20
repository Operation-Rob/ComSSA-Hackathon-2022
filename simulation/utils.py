from math import *
from consts import *

# Util functions
def angle_from_dhm(degrees, hours, minutes):
	"""
	Calculates angle from degrees, hours, minutes
	"""
	return degrees + (hours + minutes / 60) / 60

def darken(colour, factor):
	"""
	Darkens a hexadecimal colour by factor
	"""
	b = colour % 256
	colour //= 256
	g = colour % 256
	colour //= 256
	r = colour
	assert r < 256
	b *= factor
	g *= factor
	r *= factor
	colour = round(min(r, 256))
	colour *= 256
	colour += round(min(g, 256))
	colour *= 256
	colour += round(min(b, 256))
	return colour

def hex_to_rgb(colour):
	b = int(colour % 256)
	colour //= 256
	g = int(colour % 256)
	colour //= 256
	r = int(colour)
	assert r < 256
	return (r, g, b)

def get_year(years_passed):
	return START_YEAR + floor(years_passed)
def get_month(years_passed):
	return MONTH_NAMES[floor((years_passed % 1) * 12)]


def orbit_on_screen(x, y, w, h, size):
	count = 0
	if x <= w and x >= 0 and y <= h and y >= 0: # If the centre is on the screen
		if x**2 + y**2 >= size**2: # Distance to edge is larger than distance to orbit
			count += 1
		if (x - w)**2 + (y - h)**2 >= size**2:
			count += 1
		if (x - w)**2 + y**2 >= size**2:
			count += 1
		if x**2 + (y - h)**2 >= size**2:
			count += 1
		if count != 0:
			return True
		return False
	else:
		if x**2 + y**2 <= size**2: # Distance to edge is larger than distance to orbit
			count += 1
		if (x - w)**2 + (y - h)**2 <= size**2:
			count += 1
		if (x - w)**2 + y**2 <= size**2:
			count += 1
		if x**2 + (y - h)**2 <= size**2:
			count += 1
		if count % 4 != 0:
			return True
		if x >= 0 and x <= w and (abs(y - h) <= size or abs(y) <= size):
			return True
		if y >= 0 and y <= h and (abs(x - w) <= size or abs(x) <= size):
			return True
		return False
