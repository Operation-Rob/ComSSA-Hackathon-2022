DEBUG = 0

# Awaiting data from Conor/Jack
ROCKET_MASS = 2e6    # In kilograms
ROCKET_HEIGHT = 100  # In meters
INIT_FUEL_MASS = 2e6 # In kilograms
FUEL_PER_SEC = 5     # In kilograms/sec
G = 6.674e-11        # Gravitational constant
AU = 149597870700    # Astronomical unit in meters
SECS_IN_A_DAY = 60*60*24

DAYS = 10                         # Number of days to simulate
TIME_LIMIT = SECS_IN_A_DAY * DAYS # Formula for the time limit
FPS = 60                          # Frames per second of the animation
ANIMATION_SECONDS = 30            # How many seconds the animation will last for

TIME_CHANGE = (TIME_LIMIT / FPS) / ANIMATION_SECONDS # Delta t
# TIME_LIMIT / FPS is enough to make the animation last one second

INIT_WIN_WIDTH = 1000
INIT_WIN_HEIGHT = 800
MAX_AU = 32
