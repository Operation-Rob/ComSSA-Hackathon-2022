# Assumptions
# Orbits are circular
# There's no other objects in solar system which may impact gravitational fields
# Simulation isn't perfect since velocity and acceleration are really only updated after heaps of seconds
# Relativity doesn't exist

import pygame as pg
from math import *
from consts import *


# For the rings
class Orbit(object):
	def __init__(self, name="UFO orbit", au_mag=0, colour=0xffff00, centre=None, cam=None):
		assert centre is not None
		assert cam is not None
		self.centre = centre
		self.cam = cam
		self.name = name
		self.radius = au_mag * AU
		self.colour = darken(colour, ORBIT_DARKEN)

	@property
	def pos_on_screen(self):
		"""
		Shifts position of the SpaceObject to somewhere on (or off) the screen
		"""
		w, h = pg.display.get_surface().get_size()
		factor = min(w, h) * self.cam.zoom / (AU * MAX_AU)
		return ((factor * (self.centre.pos[0] - self.cam.pos[0]) + w) // 2, # FIXME: readjust
		        (factor * (self.centre.pos[1] - self.cam.pos[1]) + h) // 2) #

	@property
	def on_screen(self):
		return True #self.pos_on_screen[0] <= w and self.pos_on_screen[0] >= 0 and self.pos_on_screen[1] <= h and self.pos_on_screen[1] >= 0
	@property
	def size_on_screen(self):
		w, h = pg.display.get_surface().get_size()
		factor = min(w, h) * self.cam.zoom / (AU * MAX_AU)
		return self.radius * factor / 2

	def draw(self):
		"""
		Draws the orbit line to the PyGame screen
		"""
		if self.on_screen:
			pg.draw.circle(pg.display.get_surface(), self.colour, self.pos_on_screen, self.size_on_screen, width=ORBIT_WIDTH)


# Any object we'll be considering in the physics simulation
class SpaceObject(object):
	def __init__(self, name="UFO", x_pos=0, y_pos=0, x_vel=0, y_vel=0, mass=1e24, radius=1e7, colour=0xffff00, cam=None, au_mag=0, angle=0, period_days=0):
		assert cam is not None
		self.cam = cam
		self.name = name
		self.vel = [ x_vel, y_vel ]     # In meters/sec
		self.mass = mass                # In kg
		self.radius = radius            # In meters
		self.colour = colour

		if au_mag != 0:
			r = au_mag * AU
			self.pos = [ r * cos(radians(angle)), r * sin(radians(angle)) ]
		else:
			self.pos = [ x_pos, y_pos ] # In meters

		if period_days > 0 and au_mag != 0: # TODO: take into account effect of all planets
			# Calculation to work out initial velocity
			r = au_mag * AU
			v = 0
			if False: # Incorrect method
				v = 2 * pi * r / (period_days * SECS_IN_A_DAY) # v = (2*pi*r)/T
			else:
				v = sqrt(G * SUN_M / r) # From both F_g = G(m1m2/r^2) and a = v^2/r
			self.vel = [ v * cos(radians((angle + 90) % 360)), v * sin(radians((angle + 90) % 360)) ]

	@property
	def coords(self):
		return self.pos
	@property
	def velocity(self):
		return self.vel
	@property
	def speed(self):
		return sqrt(self.vel[0]**2 + self.vel[1]**2)

	def coords_rel_to(self, object2):
		"""
		Coordinates of self relative to object2
		"""
		return [ object2.pos[0] - self.pos[0], object2.pos[1] - self.pos[1] ]
	def vel_rel_to(self, object2):
		"""
		Velocity of self relative to object2
		"""
		return [ object2.vel[0] - self.vel[0], object2.vel[1] - self.vel[1] ]
	def speed_rel_to(self, object2):
		"""
		Speed of self relative to object2 (absolute value of difference)
		"""
		return abs(self.speed, object2.speed)

	def update_pos(self, time, accel=[ 0, 0 ]):
		"""
		Updates the position of the SpaceObject after time `time`, potentially with acceleration (a_x, a_y) changing velocity
		"""
		# s = ut + 0.5at^2
		# v = u + at
		self.pos[0] += self.vel[0] * time + accel[0] * time**2 / 2
		self.pos[1] += self.vel[1] * time + accel[1] * time**2 / 2
		self.vel[0] += accel[0] * time
		self.vel[1] += accel[1] * time

	def dist_to(self, object2):
		"""
		Distance from self to some other SpaceObject
		"""
		#assert type(self) == type(object2)
		return sqrt(self.coords_rel_to(object2)[0]**2 + self.coords_rel_to(object2)[1]**2)

	def pull_to(self, object2):
		"""
		Gravitational pull from self to some other SpaceObject (force; Newtons)
		"""
		r = self.dist_to(object2)
		if r < DIST_THRESHOLD: # Shouldn't occur
			if DEBUG:
				print(f"{self.name} has essentially collided with {object2.name}")
			return 0 # Just say there's no force acting on it
		return G * (self.mass * object2.mass) / (r**2) # F_G = G(m1m2/r^2)
	
	def accel_to(self, object2):
		"""
		Acceleration from self towards some other SpaceObject caused by gravitational pull (acceleration; m/s^2)
		"""
		r = self.dist_to(object2)
		if r < DIST_THRESHOLD: # Shouldn't occur
			if DEBUG:
				print(f"{self.name} has essentially collided with {object2.name}")
			return 0 # Just say there's no force acting on it
		return G * object2.mass / (r**2) # a=F/m
	
	def net_accel_from(self, object_list):
		"""
		Net acceleration caused by all SpaceObjects in object_list
		"""
		a = [ 0, 0 ]
		for so in object_list: # For each (distinct) space object,
			if so.name == self.name:
				continue

			dist = self.dist_to(so)
			accel = self.accel_to(so)
			if dist == 0: # This shouldn't occur
				a = [ None, None ]
				break
			else:
				a[0] += accel / dist * self.coords_rel_to(so)[0] # Accel/dist normalises it, then multiply by x-distance or y-distance
				a[1] += accel / dist * self.coords_rel_to(so)[1] #
		return a


	# Pygame related functions
	@property
	def pos_on_screen(self):
		"""
		Shifts position of the SpaceObject to somewhere on (or off) the screen
		"""
		w, h = pg.display.get_surface().get_size()
		factor = min(w, h) * self.cam.zoom / (AU * MAX_AU)
		return ((factor * (self.pos[0] - self.cam.pos[0]) + w) // 2, # FIXME: readjust
		        (factor * (self.pos[1] - self.cam.pos[1]) + h) // 2) #

	@property
	def on_screen(self):
		return True #self.pos_on_screen[0] <= w and self.pos_on_screen[0] >= 0 and self.pos_on_screen[1] <= h and self.pos_on_screen[1] >= 0
	@property
	def size_on_screen(self):
		return (self.cam.zoom * self.radius)**(1/8) # Just some flimsy calculation to make the sun not incredibly larger than the others. TODO will improve later

	def draw(self):
		"""
		Draws the SpaceObject to the PyGame screen
		"""
		if self.on_screen:
			pg.draw.circle(pg.display.get_surface(), self.colour, self.pos_on_screen, self.size_on_screen)



# Sub-class of SpaceObject, adds functions related to rocket (depletion of fuel)
class Rocket(SpaceObject):
	def __init__(self, *args):
		super().__init__(*args)
		
	def fuel_mass(self, time):
		"""
		Mass of the fuel after some time
		"""
		assert time >= 0
		return INIT_FUEL_MASS - time * FUEL_PER_SEC # FIXME: do actual function

	def total_rocket_mass(self, time):
		"""
		Rocket mass and fuel mass after some time
		"""
		#assert time >= 0
		return ROCKET_MASS + self.fuel_mass(time)

	def update_mass(self, time):
		"""
		Changes the rocket class's mass property. Will need to be run each time `time` changes
		"""
		self.mass = self.total_rocket_mass(time)


# Data about the camera
class Camera(object):
	def __init__(self, x=0, y=0, angle=0, zoom=1):
		self.pos = [ x, y ]
		self.angle = angle
		self.zoom = zoom
	
	@property
	def rotation(self):
		return self.angle
	def goto(self, pos):
		assert len(pos) == 2
		self.pos = pos
	def set_rot(self, rot):
		self.angle = rot
	def rotate(self, rot):
		self.angle += rot
	def set_zoom(self, zoom):
		self.zoom = zoom
	def zoom_by(self, zoom_factor):
		"""
		Zooms in by factor of `zoom_factor`
		"""
		self.zoom *= zoom_factor



# TODO: all SpaceObjects
# Awaiting data from Conor
def init_space_objects(cam):
	global sun, mercury, venus, earth, moon, mars, jupiter, saturn, uranus, neptune, rocket
	global mercury_orbit
	global space_objects, orbit_objects

	#                      name      x_pos, y_pos, x_vel, y_vel, mass,    radius, colour,        au_mag,  angle,                         period_days
	sun =     SpaceObject("Sun",     0,     0,     0,     0,     SUN_M,   6.96e8, 0xffdd59, cam)
	mercury = SpaceObject("Mercury", 0,     0,     0,     0,     3.30e23, 2.44e6, 0xad8866, cam, 0.309,  angle_from_dhm(129, 15, 25.9), 87.97)
	venus =   SpaceObject("Venus",   0,     0,     0,     0,     4.87e24, 6.05e6, 0xd88200, cam, 0.728,  angle_from_dhm(23, 19, 30.1),  224.70)
	earth =   SpaceObject("Earth",   0,     0,     0,     0,     5.97e24, 6.37e6, 0x46b1db, cam, 0.983,  angle_from_dhm(0, 0, 0),       365.25)
	moon =    SpaceObject("Moon",    0,     0,     0,     0,     7.35e22, 1.74e6, 0xd7d7d7, cam, 0,      0,                             1) # Earth's moon, positioned a bit differently (TODO)
	mars =    SpaceObject("Mars",    0,     0,     0,     0,     6.42e23, 3.40e6, 0xd64f0c, cam, 1.564,  angle_from_dhm(18, 47, 52.7),  686.98)
	jupiter = SpaceObject("Jupiter", 0,     0,     0,     0,     1.90e27, 7.15e7, 0xe8bfa7, cam, 4.951,  angle_from_dhm(11, 19, 21.1),  4332.82)
	saturn =  SpaceObject("Saturn",  0,     0,     0,     0,     5.68e26, 6.03e7, 0xe5c97e, cam, 9.836,  angle_from_dhm(3, 52, 37.2),   10755.70)
	uranus =  SpaceObject("Uranus",  0,     0,     0,     0,     8.68e25, 2.56e7, 0x5d94e2, cam, 19.670, angle_from_dhm(2, 20, 17.0),   30687.15)
	neptune = SpaceObject("Neptune", 0,     0,     0,     0,     1.02e26, 2.48e7, 0x3768d3, cam, 29.912, angle_from_dhm(1, 48, 6.7),    60190.03)

	#                      name,           au_mag, colour,   centre
	mercury_orbit = Orbit("Mercury orbit", 0.309,  0xad8866, sun,   cam)
	venus_orbit   = Orbit("Venus orbit",   0.728,  0xd88200, sun,   cam)
	earth_orbit   = Orbit("Earth orbit",   0.983,  0x46b1db, sun,   cam)
	#moon_orbit    = Orbit("Moon orbit",    0,      0xd7d7d7, earth, cam) # TODO
	mars_orbit    = Orbit("Mars orbit",    1.564,  0xd64f0c, sun,   cam)
	jupiter_orbit = Orbit("Jupiter orbit", 4.951,  0xe8bfa7, sun,   cam)
	saturn_orbit  = Orbit("Saturn orbit",  9.836,  0xe5c97e, sun,   cam)
	uranus_orbit  = Orbit("Uranus orbit",  19.670, 0x5d94e2, sun,   cam)
	neptune_orbit = Orbit("Neptune orbit", 29.912, 0x3768d3, sun,   cam)

	rocket = Rocket("Rocket", 0, 0, 0, 0, ROCKET_MASS + INIT_FUEL_MASS, ROCKET_HEIGHT // 2, 0x999999, cam) # Since the rocket isn't spherical, will just have to approximate the effect of gravity
	
	space_objects = [ sun, jupiter, saturn, uranus, neptune, earth, venus, mars, mercury, moon, rocket ] # All objects we'll consider which will/may have some impact on gravitational forces acting on the rocket
	orbit_objects = [ mercury_orbit, venus_orbit, earth_orbit, mars_orbit, jupiter_orbit, saturn_orbit, uranus_orbit, neptune_orbit ] # TODO: add moon_orbit

def angle_from_dhm(degrees, hours, minutes):
	"""
	Calculates angle from degrees, hours, minutes
	"""
	return degrees + hours / 60 + minutes / 3600

def darken(colour, factor):
	"""
	Darkens a hexadecimal colour by factor
	"""
	b = colour % 256
	colour //= 256
	g = colour % 256
	colour //= 256
	r = colour
	assert r < 255
	b *= factor
	g *= factor
	r *= factor
	colour = round(r)
	colour *= 256
	colour += round(g)
	colour *= 256
	colour += round(b)
	return colour


# Simulation
def simulate(delta_t_ms, total_ms, so_list, cam):
	"""
	Make all of the objects accelerate each other
	"""
	num_objs = len(so_list)
	time_passed = delta_t_ms / 1000 * SECS_IN_A_DAY * DAYS_PER_FRAME / ITERATIONS_PER_FRAME     # (Real-world) time which will pass in this one frame (divided by ITERATIONS_PER_FRAME)
	total_time_passed = total_ms / 1000 * SECS_IN_A_DAY * DAYS_PER_FRAME / ITERATIONS_PER_FRAME # Total (real-world) time which has passed since the start of the program (divided by ITERATIONS_PER_FRAME)
	accelerations = [ [ 0, 0 ] ] * num_objs

	# Rather than doing time_passed = delta_t_ms / 1000 * SECS_IN_A_DAY, execute it second-by-second so it's more accurate
	for iteration_num in range(ITERATIONS_PER_FRAME):
		for i in range(num_objs):
			accelerations[i] = so_list[i].net_accel_from(so_list)
			#accelerations[i] = so_list[i].net_accel_from([ sun ])

		# Update positions
		for i in range(num_objs):
			if accelerations[i] == [ None, None ]: # Attempt to make it not slingshot if it gets too close
				so_list[i].vel = [ 0, 0 ] # Null velocity
			else:
				so_list[i].update_pos(time_passed, accelerations[i])

		rocket.update_mass(total_time_passed) # Update rocket's fuel

	#cam.goto(earth.pos)
	cam.goto(sun.pos)

def draw_stats(window, font):
	dist = font.render(f"Distance: {earth.dist_to(sun) // 1000} kMs" , True, BLUE)
	days = font.render(f"Days Elapsed : {days} days" , True, BLUE)
	window.blit(dist, (20, 20))

def run():
	pg.init()
	font = pg.font.SysFont(None, 24)
	camera = Camera()
	window = pg.display.set_mode((INIT_WIN_WIDTH, INIT_WIN_HEIGHT), pg.RESIZABLE)
	pg.display.set_caption("Slingshot Simulation")

	init_space_objects(camera)

	clock = pg.time.Clock()
	running = True
	while running:
		clock.tick(FPS)
		window.fill(BLACK)

		simulate(clock.get_time(), pg.time.get_ticks(), space_objects, camera)
		for orbit in orbit_objects:
			orbit.draw()
		for so in space_objects:
			so.draw()

		draw_stats(window, font)

		if camera.zoom < 10: # Zoom in initially
			camera.zoom_by(1.01)

		pg.display.update()

		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
	quit()

if __name__ == "__main__":
	run()