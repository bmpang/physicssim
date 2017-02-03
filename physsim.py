import math
import Tkinter
import time as clock

#Array class: body
#Ship
	#array: [Mass, Vel Arr, position Arr]
#Planet
	#array: [Mass, Vel Arr, position Arr, Radius]

#Array class: forces
#array: [[F1x, F1y], [F2x, F2y], ... [FNx, FNy]]
		  #Big mass for good gravity			 
planet = [9999999999999999999999, [0, 0], [0, 0], 200]

moon = [33333333333333333, [0, 0], [500, 0], 40]

ship = [50, [-15000, 0], [0, 1000]]

ship2 = [50, [15000, 0], [0, -1000]]

ship3 = [50, [0, 15000], [1000, 0]]

ship4 = [50, [0, -15000], [-1000, 0]]

#This array will set the objects present at runtime.
#The ship and planet objects as defined above will produce four symmetric
#slingshot orbits. You can set whatever you want as the objects! The display
#class has been designed to scale the object size to the resolution so that
#everything will fit on the screen. Be aware that if there is a big disparity
#in orders of magnitude between the size of objects, one might appear to not
#be present because it's scaled too small on the screen
bodies = [planet, ship, ship2, ship3, ship4]

#Gravitational Constant
gc = 0.00000000006674

time = 0

#dt for the physics, more granular = more accurate but more complex
tickrate = .0001

#If you want to trace the ships path
TraceShip = False

#If you want console log of bodies data
DataLog = False

#Resolution of the square view frame in px
resolution = 750

lc = 0

#Calculate the distance between two bodies
def detdist(b1, b2):
	ps1 = b1[2]
	ps2 = b2[2]
	delt1 = ps2[0] - ps1[0]
	delt2 = ps2[1] - ps1[1]
	r = delt1*delt1 + delt2*delt2
	r = math.sqrt(r)
	return r

#calculate the angle of the vector from body 1 to body 2
def anglecalc(b1, b2):
	ps1 = b1[2]
	ps2 = b2[2]
	delt1 = ps2[0] - ps1[0]
	delt2 = ps2[1] - ps1[1]
	return math.atan2(delt2, delt1)

#Take a scalar force and the angle of the vector, convert to an array representation
def scal2arr(angle, force):
	xratio = math.cos(angle)
	yratio = math.sin(angle)
	x = xratio*force
	y = yratio*force
	return [x, y]

#Get the gravitational force between two bodies, returns one for each direction
def instgf(b1, b2):
	global gc
	r = detdist(b1, b2)
	scalf = gc*b1[0]*b2[0]/(r*r)
	angleb1 = anglecalc(b1, b2)
	angleb2 = anglecalc(b2, b1)
	return [scal2arr(angleb1, scalf), scal2arr(angleb2, scalf)]

#Given a current body the net force acting on it and dt, calculate the new body data
def update(body, force, time):
	velocity = body[1]
	for i in xrange(len(velocity)):
		delta = velocity[i]*time + .5*(force[i]/body[0])*time*time
		body[2][i] += delta
		veldel = (force[i]/body[0])*time
		body[1][i] += veldel
	return body

def netforce(forces):
	netforce = [0, 0]
	for i in forces:
		netforce[0] += i[0]
		netforce[1] += i[1]
	return netforce

#Calculate the next frame of the engine
def tick(bodies):
	global time
	global tickrate

	forces = {}

	for i in xrange(len(bodies)):
		for j in xrange(i + 1, len(bodies)):
			mforces = instgf(bodies[i], bodies[j])
			if i in forces:
				forces[i].append(mforces[0])
			else:
				forces[i] = [mforces[0]]
			if j in forces:
				forces[j].append(mforces[1])
			else:
				forces[j] = [mforces[1]]	

	# forces = instgf(b1, b2)
	# f1 = forces[0]
	# f2 = forces[1]

	#print forces

	for i in xrange(len(bodies)):
		bodies[i] = update(bodies[i], netforce(forces[i]), tickrate)

	return bodies

#Determine if the ship has landed or not given current data
def landcheck(b1, b2):
	if detdist(b1, b2) < b2[3]:
		return True
	else:
		return False

#Get the drawing coordinates for the planet given the planets data and info about
#the frame
def plntdc(planet, zero, sf):
	zero1 = zero[:]
	zero1[0] += sf*planet[2][0]
	zero1[1] += sf*planet[2][1]
	x1 = int(zero1[0] - sf*planet[3])
	x2 = int(zero1[0] + sf*planet[3])
	y1 = int(zero1[1] - sf*planet[3])
	y2 = int(zero1[1] + sf*planet[3])
	return [x1, y1, x2, y2]

#Get the drawing coordinates for the ship given the ships data and info about the 
#frame
def shpdc(ship, zero, sf):
	zero1 = zero[:]
	zero1[0] += sf*ship[2][0]
	zero1[1] += sf*ship[2][1]
	x1 = int(zero1[0] - 5)
	x2 = int(zero1[0] + 5)
	y1 = int(zero1[1] - 5)
	y2 = int(zero1[1] + 5)
	return [x1, y1, x2, y2]

#Animation of the engine
def main():
	global resolution
	global TraceShip
	global time
	global bodies

	root = Tkinter.Tk()
	widthc = resolution
	heightc = resolution
	w = Tkinter.Canvas(root, width = widthc, height = heightc)
	w.grid()
	w.pack()

	zero = [int(widthc/2), int(heightc/2)]

	#Scale factor is so the ship is 90% of the way to the edge of the screen from 
	#the planet, so that the animation always fits in the screen
	sf = detdist(bodies[0], bodies[1])
	sf = (widthc*9/20)/sf

	drawings = []
	dcs = []

	for i in xrange(len(bodies)):
		if len(bodies[i]) == 4:
			dcs.append(plntdc(bodies[i], zero, sf))
		else:
			dcs.append(shpdc(bodies[i], zero, sf))

	for j in dcs:
		drawings.append(w.create_oval(j[0], j[1], j[2], j[3]))
	
	lc = 0

	while lc < 1:
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
			if len(bodies[i]) == 4:
				w.delete(drawings[i])
			else:
				if not TraceShip:
					w.delete(drawings[i])

		dcs = []

		for i in xrange(len(bodies)):
			if len(bodies[i]) == 4:
				dcs.append(plntdc(bodies[i], zero, sf))
			else:
				dcs.append(shpdc(bodies[i], zero, sf))

		for i in xrange(len(drawings)):
			info = dcs[i]
			drawings[i] = w.create_oval(info[0], info[1], info[2], info[3])

		w.update()

		for i in xrange(len(bodies)):
			if len(bodies[i]) < 4:
				shpc = dcs[i]
				if ((abs((shpc[0] + shpc[2])/2) > widthc) or (abs((shpc[1] + shpc[3])/2) > heightc)) or ((abs((shpc[0] + shpc[2])/2) < 0) or (abs((shpc[1] + shpc[3])/2) < 0)):
					lc = 1
					print "goodbye ship"

		for i in xrange(len(bodies)):
			for j in xrange(i + 1, len(bodies)):
				if len(bodies[i]) == 4:
					if len(bodies[j]) < 4:
						if landcheck(bodies[j], bodies[i]):
							lc = 1
							print
							print "The ship has landed on the planet, which is now at "
							print str(planet[2])[1:-1]
				else:
					if len(bodies[j]) == 4:
						if landcheck(bodies[i], bodies[j]):
							lc = 1
							print
							print "The ship has landed on the planet, which is now at "
							print str(planet[2])[1:-1]
				
	root.mainloop()

main()
