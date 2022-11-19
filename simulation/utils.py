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
