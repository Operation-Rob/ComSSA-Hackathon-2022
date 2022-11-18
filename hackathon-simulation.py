import pygame as pg
from math import *
from consts import *


# Any object we'll be considering in the physics simulation
class SpaceObject(object):
	def __init__(self, name="UFO", x_pos=0, y_pos=0, x_vel=0, y_vel=0, mass=1e24, radius=1e7, cam=None, colour=0xffff00, au_mag=0, angle=0, period_days=0):
		self.name = name
		if x_pos or y_pos:
			self.pos = [ x_pos, y_pos ] # In meters
		else:
			self.pos = [ au_mag * AU * cos(angle), au_mag * AU * sin(angle) ]
		self.vel = [ x_vel, y_vel ]     # In meters/sec
		self.mass = mass                # In kg
		self.radius = radius            # In meters
		self.colour = colour
		assert cam is not None
		self.cam = cam
		if period_days > 0:
			v = 2 * pi * au_mag / (period_days * SECS_IN_A_DAY)
			self.vel = [ v * cos(angle + 90 % 360), v * sin(angle + 90 % 360) ] # Tangent line to point on circle

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

	def update_pos(self, time, accel=[0,0]):
		"""
		Updates the position of the SpaceObject after time `time`, potentially with acceleration (a_x, a_y) changing velocity
		"""
		# v = u + at
		# s = ut + 0.5at^2 (???)
		self.pos[0] += self.vel[0] * time + accel[0] * time**2 / 2
		self.pos[1] += self.vel[1] * time + accel[0] * time**2 / 2
		self.vel[0] += accel[0] * time
		self.vel[1] += accel[1] * time
		#self.pos[0] += time * self.vel[0]
		#self.pos[1] += time * self.vel[1]

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
		if r == 0: # Shouldn't occur
			if DEBUG:
				print(f"{self.name} has collided with {object2.name}")
			return 0 # Just say there's no force acting on it
		return G * (self.mass * object2.mass) / (r**2)
	
	def accel_to(self, object2):
		"""
		Acceleration from self towards some other SpaceObject caused by gravitational pull (m/s^2)
		"""
		r = self.dist_to(object2)
		if r == 0: # Shouldn't occur
			if DEBUG:
				print(f"{self.name} has collided with {object2.name}")
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
				a[0] += 0
				a[1] += 0
			else:
				a[0] += accel / dist * self.coords_rel_to(so)[0] # TODO: verify
				a[1] += accel / dist * self.coords_rel_to(so)[1] #
		return a

	# Pygame related functions
	@property
	def pos_on_screen(self):
		w, h = pg.display.get_surface().get_size()
		factor = min(w, h) * self.cam.zoom / (AU * MAX_AU)
		return ((factor * (self.pos[0] - self.cam.pos[0]) + w) // 2, (factor * (self.pos[1] - self.cam.pos[1]) + h) // 2) # FIXME: make it fit the screen, and have nothing negative of course
	@property
	def on_screen(self):
		return True #self.pos_on_screen[0] <= w and self.pos_on_screen[0] >= 0 and self.pos_on_screen[1] <= h and self.pos_on_screen[1] >= 0
	@property
	def size_on_screen(self):
		return (self.cam.zoom * self.radius)**(1/8)
	def draw(self):
		w, h = pg.display.get_surface().get_size()
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
	global space_objects

	#                      name      x_pos, y_pos, x_vel, y_vel, mass,    radius,      colour,  au_mag,  angle,                         period_days
	sun =     SpaceObject("Sun",     0,     0,     0,     0,     1.99e30, 6.96e8, cam, 0xffdd59)
	mercury = SpaceObject("Mercury", 0,     0,     0,     0,     3.30e23, 2.44e6, cam, 0xad8866, 0.309,  angle_from_dhm(129, 15, 25.9), 87.97)
	venus =   SpaceObject("Venus",   0,     0,     0,     0,     4.87e24, 6.05e6, cam, 0xd88200, 0.728,  angle_from_dhm(23, 19, 30.1),  224.70)
	earth =   SpaceObject("Earth",   0,     0,     0,     0,     5.97e24, 6.37e6, cam, 0x46b1db, 0.983,  angle_from_dhm(0, 0, 0),       365.25)
	moon =    SpaceObject("Moon",    0,     0,     0,     0,     7.35e22, 1.74e6, cam, 0xd7d7d7, 0,      0,                             1) # Earth's moon, positioned a bit differently (TODO)
	mars =    SpaceObject("Mars",    0,     0,     0,     0,     6.42e23, 3.40e6, cam, 0xd64f0c, 1.564,  angle_from_dhm(18, 47, 52.7),  686.98)
	jupiter = SpaceObject("Jupiter", 0,     0,     0,     0,     1.90e27, 7.15e7, cam, 0xe8bfa7, 4.951,  angle_from_dhm(11, 19, 21.1),  4332.82)
	saturn =  SpaceObject("Saturn",  0,     0,     0,     0,     5.68e26, 6.03e7, cam, 0xe5c97e, 9.836,  angle_from_dhm(3, 52, 37.2),   10755.70)
	uranus =  SpaceObject("Uranus",  0,     0,     0,     0,     8.68e25, 2.56e7, cam, 0x5d94e2, 19.670, angle_from_dhm(2, 20, 17.0),   30687.15)
	neptune = SpaceObject("Neptune", 0,     0,     0,     0,     1.02e26, 2.48e7, cam, 0x3768d3, 29.912, angle_from_dhm(1, 48, 6.7),    60190.03)

	rocket = Rocket("Rocket", 0, 0, 0, 0, ROCKET_MASS + INIT_FUEL_MASS, ROCKET_HEIGHT // 2, cam, 0x999999) # Since the rocket isn't spherical, will just have to approximate the effect of gravity

	space_objects = [ sun, jupiter, saturn, uranus, neptune, earth, venus, mars, mercury, moon, rocket ] # All objects we'll consider which will/may have some impact on gravitational forces acting on the rocket

def angle_from_dhm(degrees, hours, minutes):
	"""
	Calculates angle from degrees, hours, minutes
	"""
	return degrees + hours / 60 + minutes / 3600


# Simulation
def simulate(delta_t_ms, total_ms, so_list, cam):
	"""
	Make all of the objects accelerate each other
	"""
	num_objs = len(so_list)
	time_passed = delta_t_ms / 1000
	total_time_passed = total_ms / 1000

	accelerations = [ [ 0, 0 ] ] * num_objs
	for	i in range(num_objs):
		accelerations[i] = so_list[i].net_accel_from(so_list)
	# Update positions
	for i in range(num_objs):
		so_list[i].update_pos(time_passed, accelerations[i])

	rocket.update_mass(total_time_passed) # Update rocket's fuel

	cam.goto(earth.pos)

def run():
	camera = Camera()
	window = pg.display.set_mode((INIT_WIN_WIDTH, INIT_WIN_HEIGHT), pg.RESIZABLE)
	pg.display.set_caption("Slingshot Simulation")

	init_space_objects(camera)

	clock = pg.time.Clock()
	running = True
	while running:
		clock.tick(FPS)
		window.fill(0x000000)

		simulate(clock.get_time(), pg.time.get_ticks(), space_objects, camera)
		for so in space_objects:
			so.draw()

		if camera.zoom < 15: # Zoom in initially
			camera.zoom_by(1.01)

		pg.display.update()
	
		for event in pg.event.get():
			if event.type == pg.QUIT:
				if DEBUG:
					print(venus.pos)
				running = False
	quit()

if __name__ == "__main__":
	run()
