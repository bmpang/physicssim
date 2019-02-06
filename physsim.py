import math
import Tkinter
import time as clock

#This is a 2d physics simulator made using python default libraries

#CLASSES
#####################################
class Body:
	def __init__(self, mass, velocityArray, positionArray):
		self.mass = mass
		self.mass = mass
		self.velocityArray = velocityArray
		self.positionArray = positionArray

class CelestialBody(Body):
	def __init__(self, mass, velocityArray, positionArray, radius):
		Body.__init__(self, mass, velocityArray, positionArray)
		self.radius = radius

#GLOBAL CONSTANTS
#####################################
#Gravitational Constant
gc = 0.00000000006674

#Start at the beginning
time = 0

#dt for the physics, more granular = more accurate but more complex
tickrate = .0001

#If you want to trace the ships path
TraceShip = False

#If you want console log of bodies data
DataLog = False

#Resolution of the square view frame in px
resolution = 750

#Used to determine if a ship has landed or left the screen (for the animation to continue or not)
lc = 0

#OBJECTS IN ANIMATION
#####################################
planet = CelestialBody(9999999999999999999999, [0, 0], [0, 0], 200)

moon = CelestialBody(33333333333333333, [0, 0], [500, 0], 40)

ship1 = Body(50, [-15000, 0], [0, 1000])

ship2 = Body(50, [15000, 0], [0, -1000])

ship3 = Body(50, [0, 15000], [1000, 0])

ship4 = Body(50, [0, -15000], [-1000, 0])

#This array will set the objects present at runtime.
#The ship and planet objects as defined above will produce four symmetric
#slingshot orbits. You can set whatever you want as the objects! The display
#class has been designed to scale the object size to the resolution so that
#everything will fit on the screen. Be aware that if there is a big disparity
#in orders of magnitude between the size of objects, one might appear to not
#be present because it's scaled too small on the screen. Note that because of
#that, ships will always be drawn at a fixed 5px to ensure they're visible,
#regardless of their encoded size
bodies = [planet, ship1, ship2, ship3, ship4]
#Calculate the distance between two bodies

def distanceBetweenBodies(body1, body2):
	positionOfBody1 = body1.positionArray
	positionOfBody2 = body2.positionArray
	xDelta = positionOfBody2[0] - positionOfBody1[0]
	yDelta = positionOfBody2[1] - positionOfBody1[1]
	hypotenuse = xDelta*xDelta + yDelta*yDelta
	distance = math.sqrt(hypotenuse)

	return distance

#calculate the angle of the vector from body 1 to body 2
def angleBetweenBodies(body1, body2):
	positionOfBody1 = body1.positionArray
	positionOfBody2 = body2.positionArray
	xDelta = positionOfBody2[0] - positionOfBody1[0]
	yDelta = positionOfBody2[1] - positionOfBody1[1]
	angle = math.atan2(yDelta, xDelta)

	return angle

#Take a scalar force and the angle of the vector, convert to an array representation
def getForceVectorFromScalarAndAngle(forceAngle, forceScalar):
	forceRatioForX = math.cos(forceAngle)
	forceRatioForY = math.sin(forceAngle)
	x = forceRatioForX*forceScalar
	y = forceRatioForY*forceScalar
	forceVector = [x, y]

	return forceVector

#Get the gravitational force between two bodies, returns one for each direction
def instantaneousGravitationalForcesBetweenTwoBodies(body1, body2):
	global gc

	distance = distanceBetweenBodies(body1, body2)
	gravitationalForceScalar = gc*body1.mass*body2.mass/(distance*distance)
	angleFromBody1 = angleBetweenBodies(body1, body2)
	angleFromBody2 = angleBetweenBodies(body2, body1)

	listOfForceVectors = [getForceVectorFromScalarAndAngle(angleFromBody1, gravitationalForceScalar), getForceVectorFromScalarAndAngle(angleFromBody2, gravitationalForceScalar)]

	return listOfForceVectors

#C A L C U L U S
#Given a current body the net force acting on it and dt, calculate the new body data
#Adapted for arbitrary dimensions
def update(body, force, timeDelta):
	velocity = body.velocityArray

	for i in xrange(len(velocity)):
		positionDelta = velocity[i]*timeDelta + .5*(force[i]/body.mass)*timeDelta*timeDelta
		body.positionArray[i] += positionDelta
		velocityDelta = (force[i]/body.mass)*timeDelta
		body.velocityArray[i] += velocityDelta

#Given a list of force vectors, calculate the net force
#Adapted for arbitrary dimensions
def netforce(forces):
	netforce = [0 for i in xrange(len(forces[0]))]

	for force in forces:
		for i in xrange(len(force)):
			netforce[i] += force[i]

	return netforce

#Calculate the next frame of the engine
def tick(bodies):
	global tickrate

	forcesActingOnEachBody = {}

	for i in xrange(len(bodies) - 1):
		for j in xrange(i + 1, len(bodies)):
			forcesBetweenCurrentTwoBodies = instantaneousGravitationalForcesBetweenTwoBodies(bodies[i], bodies[j])
			if i in forcesActingOnEachBody:
				forcesActingOnEachBody[i].append(forcesBetweenCurrentTwoBodies[0])
			else:
				forcesActingOnEachBody[i] = [forcesBetweenCurrentTwoBodies[0]]
			if j in forcesActingOnEachBody:
				forcesActingOnEachBody[j].append(forcesBetweenCurrentTwoBodies[1])
			else:
				forcesActingOnEachBody[j] = [forcesBetweenCurrentTwoBodies[1]]	

	for i in xrange(len(bodies)):
		update(bodies[i], netforce(forcesActingOnEachBody[i]), tickrate)

	return bodies

#Determine if the ship has landed or not given current data
def landcheck(ship, celestialBody):
	if distanceBetweenBodies(ship, celestialBody) < celestialBody.radius:
		return True
	else:
		return False

#Get the drawing coordinates for the planet given the planets data and info about
#the frame
def getDrawingCoordinatesForCelestialBody(celestialBody, centerOfCanvas, scaleFactor):
	center = centerOfCanvas[:]
	center[0] += scaleFactor*celestialBody.positionArray[0]
	center[1] += scaleFactor*celestialBody.positionArray[1]
	x1 = int(center[0] - scaleFactor*celestialBody.radius)
	x2 = int(center[0] + scaleFactor*celestialBody.radius)
	y1 = int(center[1] - scaleFactor*celestialBody.radius)
	y2 = int(center[1] + scaleFactor*celestialBody.radius)

	return [x1, y1, x2, y2]

#Get the drawing coordinates for the ship given the ships data and info about the 
#frame
def getDrawingCoordinatesForBody(body, centerOfCanvas, scaleFactor):
	center = centerOfCanvas[:]
	center[0] += scaleFactor*body.positionArray[0]
	center[1] += scaleFactor*body.positionArray[1]
	x1 = int(center[0] - 5)
	x2 = int(center[0] + 5)
	y1 = int(center[1] - 5)
	y2 = int(center[1] + 5)

	return [x1, y1, x2, y2]

#Animation of the engine
def main():
	global resolution
	global TraceShip
	global time
	global bodies

	#Create The Canvas
	root = Tkinter.Tk()
	widthc = resolution
	heightc = resolution
	w = Tkinter.Canvas(root, width = widthc, height = heightc)
	w.grid()
	w.pack()

	zero = [int(widthc/2), int(heightc/2)]

	#Scale factor is so the ship is 90% of the way to the edge of the screen from 
	#the planet, so that the animation always fits in the screen
	scaleFactor = distanceBetweenBodies(bodies[0], bodies[1])
	scaleFactor = (widthc*9/20)/scaleFactor

	drawings = []
	drawingCoordinates = []

	for i in xrange(len(bodies)):
		if isinstance(bodies[i], CelestialBody):
			drawingCoordinates.append(getDrawingCoordinatesForCelestialBody(bodies[i], zero, scaleFactor))
		else:
			drawingCoordinates.append(getDrawingCoordinatesForBody(bodies[i], zero, scaleFactor))

	for drawingCoordinate in drawingCoordinates:
		drawings.append(w.create_oval(drawingCoordinate[0], drawingCoordinate[1], drawingCoordinate[2], drawingCoordinate[3]))
	
	shipHasNotLandedOrFlownOff = True

	while shipHasNotLandedOrFlownOff:
		#graphic.create_circle()
        
		bodies = tick(bodies)
		time += tickrate

		if DataLog:
			print "time: " + str(time) + ", data: " + str(bodies)

		# Sleeping off the tickrate makes animations go way too fast for nontrace
		# clock.sleep(tickrate)
	
		# Tracing the ship adds a lot of clock time already to store all the points
		if not TraceShip:
			clock.sleep(.001)

		#delete planets
		for i in xrange(len(bodies)):
			if isinstance(bodies[i], CelestialBody):
				w.delete(drawings[i])
			else:
				if not TraceShip:
					w.delete(drawings[i])

		drawingCoordinates = []

		for i in xrange(len(bodies)):
			if isinstance(bodies[i], CelestialBody):
				drawingCoordinates.append(getDrawingCoordinatesForCelestialBody(bodies[i], zero, scaleFactor))
			else:
				drawingCoordinates.append(getDrawingCoordinatesForBody(bodies[i], zero, scaleFactor))

		for i in xrange(len(drawings)):
			info = drawingCoordinates[i]
			drawings[i] = w.create_oval(info[0], info[1], info[2], info[3])

		w.update()

		for i in xrange(len(bodies)):
			if not isinstance(bodies[i], CelestialBody):
				bodyCoordinates = drawingCoordinates[i]
				if ((abs((bodyCoordinates[0] + bodyCoordinates[2])/2) > widthc) or (abs((bodyCoordinates[1] + bodyCoordinates[3])/2) > heightc)) or ((abs((bodyCoordinates[0] + bodyCoordinates[2])/2) < 0) or (abs((bodyCoordinates[1] + bodyCoordinates[3])/2) < 0)):
					shipHasNotLandedOrFlownOff = False
					print "goodbye ship"

		for i in xrange(len(bodies)):
			for j in xrange(i + 1, len(bodies)):
				if isinstance(bodies[i], CelestialBody):
					if not isinstance(bodies[j], CelestialBody):
						if landcheck(bodies[j], bodies[i]):
							shipHasNotLandedOrFlownOff = False
							print
							print "The ship has landed on the planet, which is now at "
							print str(planet[2])[1:-1]
				else:
					if isinstance(bodies[j], CelestialBody):
						if landcheck(bodies[i], bodies[j]):
							shipHasNotLandedOrFlownOff = False
							print
							print "The ship has landed on the planet, which is now at "
							print str(planet[2])[1:-1]
				
	root.mainloop()

main()
