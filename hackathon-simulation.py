import pygame
from math import *


DEBUG = 0

# Awaiting data from Conor/Jack
ROCKET_MASS = 2e6    # In kilograms
ROCKET_HEIGHT = 100  # In meters
INIT_FUEL_MASS = 2e6 # In kilograms
FUEL_PER_SEC = 5     # In kilograms/sec
G = 6.67e-11         # Gravitational constant

# Any object we'll be considering in the physics simulation
class SpaceObject(object):
	def __init__(self, name="UFO", x_coord=0, y_coord=0, vel_x=0, vel_y=0, mass=1e24, radius=1e7):
		self.name = name
		self.pos = [ x_coord, y_coord ] # In meters
		self.vel = [ vel_x, vel_y ]     # In meters/sec
		self.mass = mass                # In kg
		self.radius = radius            # In meters

	def coords(self):
		return self.pos
	def velocity(self):
		return self.vel

	def update_pos(self, time, a_x=0, a_y=0):
		"""
		Updates the position of the SpaceObject after time `time`, potentially with acceleration (a_x, a_y) changing velocity
		"""
		self.vel[0] += a_x
		self.vel[1] += a_y
		self.pos[0] += time * self.vel[0]
		self.pos[1] += time * self.vel[1]

	def dist_to(self, object2):
		"""
		Distance from self to some other SpaceObject
		"""
		#assert type(self) == type(object2)
		return sqrt((self.pos[0] - object2.pos[0])**2 + (self.pos[1] - object2.pos[1])**2)

	def pull_to(self, object2):
		"""
		Gravitation pull from self to some other SpaceObject (force; Newtons)
		"""
		r = self.dist_to(object2)
		if r == 0: # Shouldn't occur
			if DEBUG:
				print(f"{self.name} has collided with {object2.name}")
			return 0 # Just say there's no force acting on it
		return G * (self.mass * object2.mass) / (r**2)
	
	def acceleration_to(self, object2):
		"""
		Acceleration from self towards some other SpaceObject caused by gravitational pull (m/s^2)
		"""
		r = self.dist_to(object2)
		if r == 0: # Shouldn't occur
			if DEBUG:
				print(f"{self.name} has collided with {object2.name}")
			return 0 # Just say there's no force acting on it
		return G * object2.mass / (r**2) # a=F/m


# Sub-class of SpaceObject, adds functions related to rocket (depletion of fuel)
class Rocket(SpaceObject):
	def __init__(self, *args):
		super().__init__(*args)
		
	def fuel_mass(self, time):
		"""
		Mass of the fuel after some time
		"""
		assert time >= 0
		return INIT_FUEL_MASS - time * FUEL_PER_SEC

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



# TODO: all SpaceObjects
# Awaiting data from Conor
#                      name      x_pos, y_pos, x_vel, y_vel, mass,    radius
sun = SpaceObject("Sun",         0,     0,     0,     0,     1.99e30, 6.96e8)
mercury = SpaceObject("Mercury", 0,     0,     0,     0,     3.30e23, 2.44e6)
venus = SpaceObject("Venus",     0,     0,     0,     0,     4.87e24, 6.05e6)
earth = SpaceObject("Earth",     0,     0,     0,     0,     5.97e24, 6.37e6)
moon = SpaceObject("Moon",       0,     0,     0,     0,     7.35e22, 1.74e6) # Earth's moon
mars = SpaceObject("Mars",       0,     0,     0,     0,     6.42e23, 3.40e6)
jupiter = SpaceObject("Jupiter", 0,     0,     0,     0,     1.90e27, 7.15e7)
saturn = SpaceObject("Saturn",   0,     0,     0,     0,     5.68e26, 6.03e7)
uranus = SpaceObject("Uranus",   0,     0,     0,     0,     8.68e25, 2.56e7)
neptune = SpaceObject("Neptune", 0,     0,     0,     0,     1.02e26, 2.48e7)

rocket = Rocket("Rocket", 0, 0, 0, 0, ROCKET_MASS + INIT_FUEL_MASS, ROCKET_HEIGHT // 2) # Since the rocket isn't spherical, will just have to approximate the effect of gravity

space_objects = [ rocket, sun, mercury, venus, earth, moon, mars, jupiter, saturn, uranus, neptune ] # All objects we'll consider which will/may have some impact on gravitational forces acting on the rocket



# Simulation
DAYS = 10                  # Number of days to simulate
TIME_LIMIT = 60*60*24*DAYS # Formula for the time limit
FPS = 60                   # Frames per second of the animation
ANIMATION_SECONDS = 30     # How many seconds the animation will last for

TIME_CHANGE = (TIME_LIMIT / FPS) / ANIMATION_SECONDS # Delta t

time_s = 0
while time_s < TIME_LIMIT:
	# TODO: core simulation

	# Make all of the objects accelerate each other
	accelerations = [[0,0]] * len(space_objects)
	for i in range(len(space_objects)):
		for j in range(len(space_objects)):
			if i == j:
				continue

			dist = space_objects[i].dist_to(space_objects[j])
			accel = space_objects[i].acceleration_to(space_objects[j])
			if dist == 0: # This shouldn't occur
				accelerations[i][0] = 0
				accelerations[i][1] = 0
			else:
				accelerations[i][0] = accel / dist * (space_objects[j].pos[0] - space_objects[i].pos[0]) # TODO: verify
				accelerations[i][1] = accel / dist * (space_objects[j].pos[1] - space_objects[i].pos[1]) #

	# Update positions
	for i in range(len(space_objects)):
		space_objects[i].update_pos(TIME_CHANGE, accelerations[i][0], accelerations[i][1])
	rocket.update_mass(time_s) # Update rocket's fuel

	# TODO: graph new positions

	time_s += TIME_CHANGE # TIME_LIMIT / FPS is enough to make the animation last one second