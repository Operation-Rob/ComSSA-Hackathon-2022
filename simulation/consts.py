DEBUG = 0

# Awaiting data from Conor/Jack
# Constants relating to the logistics
ROCKET_MASS = 1e4    # In kilograms
ROCKET_HEIGHT = 150  # In meters
INIT_FUEL_MASS = 1e4 # In kilograms
FUEL_PER_SEC = 5     # In kilograms/sec

# Constants
G = 6.674e-11        # Gravitational constant
AU = 149597870700    # Astronomical unit in meters
SECS_IN_A_DAY = 60*60*24
DIST_THRESHOLD = 1e5 # No two SpaceObjects should be closer than this to each other (hopefully)
SUN_M = 1.99e30      # Mass of sun (kg)

# Animation things
FPS = 60                   # Frames per second of the animation
ITERATIONS_PER_FRAME = 100 # How many times the physics is calculated per frame. The higher, the more accurate, but the slower the program will run
DAYS_PER_FRAME = 10        # How many (Earth) days pass in one second of the animation

# Deprecated time-animation things
#DAYS = 10                         # Number of days to simulate
#TIME_LIMIT = SECS_IN_A_DAY * DAYS # Formula for the time limit
#ANIMATION_SECONDS = 30            # How many seconds the animation will last for
#TIME_CHANGE = (TIME_LIMIT / FPS) / ANIMATION_SECONDS # Delta t
# TIME_LIMIT / FPS is enough to make the animation last one second

# Window stuff
INIT_WIN_WIDTH = 1000
INIT_WIN_HEIGHT = 800
MAX_AU = 32 # Used for sizing the screen
ORBIT_WIDTH = 1

# Colours
ORBIT_DARKEN = 0.6
BLACK = 0x000000
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Time
START_YEAR = 2030
MONTH_NAMES = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]
