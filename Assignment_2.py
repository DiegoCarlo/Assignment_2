from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL.Image import *
from math import *
from random import randint
from random import random

### window param ###
windowWidth = 1200
windowHeight = 600
windowX = 300
windowY = 150

### mouse ###
mouseX = 0
mouseY = 0
mousePrevStateRight = 1 # button pressed or not
mousePrevStateMiddle = 1
mousePrevStateLeft = 1
mouseTracking = False# ready or not to register movements

### view parameters ###
maxViewDistance = 150

### all object ###
listSpaceObjects = None

### param of visualization ###
# Parameters for a more apreciable rappresentation
coeffDiam = 0.45 # object diameter
coeffDist = 10 # distance from the sun
gapDist = 0 # 
coeffRevo = 0.40 # coefficient of orbital time
coeffRot = 0.35 # coefficient of rotation time
coeffRevoSatellites = 10 # for moon
subdivision = 60 # "faces of the object"

### asteroids ###
numberOfAsteroid = 200
asteroidMarsGap = 50
asteroidJupiterGap = 250

### permits to draw objects ###
quadric = None

### manage the view ###
camera = None

### simulation variables ###
update = True # do simulation or not
simulationVelocity = 1
maxSimulationVelocity = 50

showOrbit = False

allTexture = ["00_Sole.jpg", "01_Mercurio.jpg", "02_Venere.jpg", "03_Terra.jpg", \
"03_01_Luna_2.jpg", "04_Marte.jpg", "05_Giove.jpg", "06_Saturno.jpg", "07_Urano.jpg", "08_Nettuno.jpg"]

asteroidPath = "04.5_Asteroid_2.jpg"
asteroidTexture = None

textureSaturnRing = None
### The numerical values shown here have been taken from wikipedia ###
### These are the distances of the main objects from their center of revolution  (x * 10^9 meters) ###
revolutionRadius = [0.00, 57.90, 108.20, 149.60, 0.384, 227.90, 778.30, 1427.00, 2871.00, 4497.10]
### The diameters of the main objects (x * 10^6 meters) ###
diameters = [1391.400, 4.878, 12.102, 12.756, 3.476, 6.786, 142.984, 120.536, 51.118, 49.528]
### The durations of the revolution of the main objects (x day) ###
revolutions = [0, 87.969, 224.700, 365.256, 27.321, 686.96, 4333.286, 10756.199, 30707.043, 60223.352]
### The durations of the bodies of rotation on its own axis (x hours) ###
rotations = [654.6, 1403.667, 5816.083, 23.934, 653.930, 24.555, 9.897, 10.755, 17.192, 16.11] 
### Inclination of its axis ###
inclination = [0, 0.01, 177.36, 23.43, 1.54, 25.19, 3.13, 26.73, 97.77, 28.32]
### Inclination to Sun's equator ###
inclinationOrbit = [0, 3.38, 3.86, 7.155, 5.145, 5.65, 6.09, 5.51, 6.48, 6.43]

#rotations = [26.5, 58.65, -243.01, 0.997, 27.32, 1.026, 0.41, 0.426, -0.746, 0.8]

### star, planet, satellite, environment ###
allClasses = ["star", "planet", "planet", "planet", "satellite", "planet", "planet", "planet", "planet", "planet"]


class Camera(object):
	""" This class manage the view.

	Attributes:
		maxDistance: the max distance of the camera from the origin
		minDistance: the minimum distance of the camera from the origin
		
		z: the current distance from the camera from the origin

		xOrbit: the angle of vertical increment
		yOrbit: the angle of horizontal increment

		xOrbitTemp: the vertical angle increment while the mouse drags the view
		yOrbitTemp: the horizontal angle increment while the mouse drags the view
	"""
	def __init__(self):

		self.maxDistance = 60
		self.minDistance = 2.5

		self.z = self.maxDistance * 0.75 # moving forwards -z moving backwards + z

		self.xOrbit = -65 
		self.yOrbit = 0

		self.xOrbitTemp = 0
		self.yOrbitTemp = 0

		self.update()

	def zoom(self, z):
		""" zoom increment the distance from origin """
		temp = self.z + z
		if temp > self.minDistance and temp < self.maxDistance:
			self.z = temp

	def update(self):
		""" aggiorna la posizione della telecamera """
		gluLookAt(0, 0, self.z, \
			0, 0, 0, \
			0, 1, 0)

		glRotate(self.xOrbit + self.xOrbitTemp, 0, 1, 0)

		angleX = radians((self.xOrbit + self.xOrbitTemp))
		xComp = cos(angleX)
		zComp = sin(angleX)

		glRotate(self.yOrbit + self.yOrbitTemp, xComp, 0, zComp)

	def incrementOrientation(self):
		""" the function must be called when the mouse was released """
		self.xOrbit += self.xOrbitTemp
		self.yOrbit += self.yOrbitTemp
		self.xOrbitTemp = 0
		self.yOrbitTemp = 0

	def tempIncrementOrientation(self, x, y):
		""" it must be called when the mouse drag the view """
		self.xOrbitTemp = x
		self.yOrbitTemp = y

class Rotation(object):
	""" this class is responsible for the rotation of an object """
	def __init__(self, angPosition, angVelocity):
		self.angPosition = angPosition
		self.angVelocity = angVelocity

	def update(self, coeff):
		self.angPosition += (self.angVelocity * coeff)
		if self.angPosition >= 360:
			self.angPosition -= 360

class Orbit(Rotation):
	""" This class handles the orbit of the subject with respect to an axis
		Attributes:
			axisDistance: 
			axis: orbit inclination to Sun's equator
			angPosition: the angular position of the object
			angVelocity: the angular velocity
			visible: if True shows an orbital track
			idRootorbit: an index of the listSpaceObjects and which object this orbit uses as center

	"""
	def __init__(self, axisDistance, axis, angPosition, angVelocity, visible, idRootOrbit = None):
		super(Orbit, self).__init__(angPosition, angVelocity)
		self.axisDistance = axisDistance
		self.axis = axis
		self.visible = visible
		if idRootOrbit != None:
			self.idRootOrbit = idRootOrbit
		else:
			self.idRootOrbit = None

	def update(self, coeff):
		super(Orbit, self).update(coeff)

class SpaceObject(object):
	"""	It contains the parameters of a space object

	Attributes:
		classes: star, planet, satellite, environment. To choose materials
		orientation: self axis inclination
		radius: SO radius
		rotation: ...
		revolution: orbit
		pathImage: ...
		subdivision: a higher value increases the number of faces of the sphere
		texture: texture loaded
	"""
	def __init__(self, classes, orientation, radius, 
		rotation, revolution, \
		pathImage, subdivision):

		self.classes = classes
		self.orientation = orientation
		self.radius = radius
		
		self.rotation = rotation
		self.revolution = revolution
		
		self.pathImage = pathImage
		self.texture = None

		self.subdivision = subdivision ### sphere subdivision

	def update(self, coeff):
		self.rotation.update(coeff)
		self.revolution.update(coeff)

def initTexture(pathImage):
	""" load texture for a single object """
	global quadric
	image = open(pathImage)

	ix = image.size[0]
	iy = image.size[1]
	# load image using PIL
	image_bytes = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
	# generate one texture name
	texture = glGenTextures(1)
	# bind a named texture to a texturing targhet
	glBindTexture(GL_TEXTURE_2D, texture)
	# build a two-dimensional mipmap
	gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image_bytes)
	# parameters 
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_LINEAR )
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
	
	# this texture must be generated for quadrics render
	gluQuadricTexture(quadric, 1)

	return texture

def createSpaceObject():
	""" This function instantiates the major planets """
	global listSpaceObjects, maxViewDistance, coeffDiam, coeffDist, gapDist, coeffRevo, coeffRot, coeffRevoSatellites, subdivision

	listSpaceObjects = []
	for i in range(0, len(diameters)):

		# object rotation
		rot = 360/rotations[i]
		rotation = Rotation(0, rot * coeffRot)

		# distance
		dist = 0
		if revolutionRadius[i] != 0:
			dist = (log(revolutionRadius[i], 10) * coeffDist) - gapDist
			#print log(revolutionRadius[i], 10)
		# distance of the moon adjusted for consistency
		if i == 4:
			dist = 1
		# revolution period
		revo = 0
		if revolutions[i] != 0:
			revo = 1/log(revolutions[i], 10) * coeffRevo

		if allClasses[i] == "satellite":
			revo = revo * coeffRevoSatellites

		# object orbit
		revolution = Orbit(dist, inclinationOrbit[i], randint(0,360),revo, True)
		radius = log(diameters[i], 10) * coeffDiam
		
		listSpaceObjects.append(SpaceObject(allClasses[i],[0,0,inclination[i]], radius, rotation, \
			revolution, allTexture[i], subdivision))

	### set mun as satellite of the earth ###
	listSpaceObjects[4].revolution.idRootOrbit = 3

	# create some asteroids
	createAsteroids(coeffDist, coeffDiam, gapDist, coeffRevo, 8)

	# skysphere
	rotation = Rotation(0, -0.02)
	revolution = Orbit(0,0,0,0, False)
	listSpaceObjects.append(SpaceObject("environment",[0,0,45], maxViewDistance, rotation, \
		revolution, "The_Milky_Way.jpg", subdivision))	

def createAsteroids(coeffDist, coeffDiam, gapDist, coeffRevo, subdivision):
	""" this function create small asteroids """
	global numberOfAsteroid, asteroidMarsGap, asteroidJupiterGap
	for i in range(1, numberOfAsteroid):

		rotation = Rotation(0, 0)
		rand = random()
		minDistance = revolutionRadius[5] + asteroidMarsGap
		maxDistance = revolutionRadius[6] - asteroidJupiterGap
		gapDistance = maxDistance - minDistance
		dist = rand * gapDistance + minDistance
		dist = (log(dist, 10) * coeffDist) - gapDist
		minOrbit = revolutions[5]
		maxOrbit = revolutions[6]
		gapOrbit = maxOrbit - minOrbit
		revo = rand * gapOrbit + minOrbit
		revolution = Orbit(dist, randint(0,99)*0.02+5.8,randint(0,360), 1/log(revo, 10) * coeffRevo, False)
		listSpaceObjects.append(SpaceObject("asteroid",[0,0,0], randint(10,40)*coeffDiam*0.0035, rotation, \
		revolution, asteroidTexture, subdivision)) 

def initScene():
	global quadric, listSpaceObjects, camera, textureSaturnRing

	createSpaceObject()

	glEnable(GL_DEPTH_TEST)

	glEnable(GL_COLOR_MATERIAL)
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)

	# Parameters for correct shading
	glShadeModel(GL_SMOOTH)
	glDepthFunc(GL_LEQUAL)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
	glCullFace(GL_BACK)
	glEnable(GL_CULL_FACE)
	glClearColor(0.0, 0.0, 0.0, 0.0)

	quadric = gluNewQuadric()

	asteroidTexture = initTexture(asteroidPath)
	for i in listSpaceObjects:
		if i.classes == "asteroid":
			i.texture = asteroidTexture
		else:
			i.texture = initTexture(i.pathImage)

	textureSaturnRing = initTexture("06_01_Anelli.jpg") #06_01_Anelli.jpg")

	camera = Camera()

def revolutionRoot(revolution):
	global showOrbit
	# if the object is orbiting around a second object which in turn is orbiting about a third object, run the rotation of the second object before and so recursively
	# se l'oggetto orbita attorno ad un corpo che orbita a sua volta eseguo prima la rotazione del corpo e cosi ricorsivamente
	if revolution.idRootOrbit >= 0 and revolution.idRootOrbit < len(listSpaceObjects):
		revolutionRoot(listSpaceObjects[revolution.idRootOrbit].revolution)
	
	axis = revolution.axis
	# he main bodies have their visible primary orbit, below them a track is represented
	# i soggetti principali hanno la loro orbita primaria visibile, di seguito ne viene rappresentata una traccia
	if showOrbit == True and revolution.visible == True:
		glPushMatrix()
		glRotate(revolution.axis,1,0,0)
		glRotate(revolution.angPosition, 0,1,0)
		glRotatef(90, 1, 0, 0)
		glRotatef(135, 0, 0, 1)
		fRadius = revolution.axisDistance #* 2 + (-item.radius)
		#print fRadius
		fCenterX = 0.0 
		fCenterY = 0.0 

		glBegin(GL_LINE_STRIP)
		i = 0
		while(i<3.14*1.25):

			fX = fCenterX + (fRadius* (sin(i)))
			fY = fCenterY + (fRadius* (cos(i)))

			glVertex3f(fX, fY, 0);
			i +=0.01
		glEnd();

		glPopMatrix()

	glRotate(revolution.axis,1,0,0)
	glRotate(revolution.angPosition,0,1,0)
	glTranslate(revolution.axisDistance, 0, 0)
	glRotate(-revolution.angPosition, 0,1,0)

def drawSpaceObject(item):
	global quadric, textureSaturnRing, update
	
	if update == True:
		item.update(simulationVelocity)
	
	glPushMatrix()

	# choice of material
	if item.classes == "planet" or item.classes == "environment" or item.classes == "asteroid":
		glMaterialfv(GL_FRONT, GL_EMISSION, [.0, .0, .0, 1])
		glMaterialfv(GL_FRONT, GL_SHININESS, 50)
		glMaterialfv(GL_FRONT, GL_DIFFUSE, [.5, .5, .5, 1.0])
		glMaterialfv(GL_FRONT, GL_SPECULAR, [.1, .1, .1, 1])

	elif item.classes == "asteroid":
		glMaterialfv(GL_FRONT, GL_EMISSION, [.0, .0, .0, 1])
		glMaterialfv(GL_FRONT, GL_SHININESS, 100)
		glMaterialfv(GL_FRONT, GL_DIFFUSE, [.5, .5, .5, 1.0])
		glMaterialfv(GL_FRONT, GL_SPECULAR, [.1, .1, .1, 1])

	elif item.classes == "star":
		glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [1, 1, 1, .0]) #with this, the sun EMITS light
		glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 70)
	
	### positioning and rotations ###
	revolutionRoot(item.revolution)

	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, item.texture)

	glRotatef(-90, 1, .0, .0)
	glRotatef(item.orientation[2], 0, 1, 0)

	glRotatef(item.rotation.angPosition, .0, .0, 1)
	
	# skySphere
	if item.classes == "environment":
		glDepthMask(GL_FALSE)
		gluQuadricOrientation(quadric, GLU_INSIDE)
		gluSphere(quadric, item.radius, item.subdivision, item.subdivision)
		gluQuadricOrientation(quadric, GLU_OUTSIDE)
		glDepthMask(GL_TRUE)
	else:
		gluSphere(quadric, item.radius, item.subdivision, item.subdivision)

	glPopMatrix()
	glDisable(GL_TEXTURE_2D)


	### special guest: saturn ring ###
	if item.pathImage == "06_Saturno.jpg":
		glPushMatrix()
		glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [.0, .0, .0, 1])
		glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 100)
		glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [.5, .5, .5, 1.0])
		glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [.1, .1, .1, 1])
		
		revolutionRoot(item.revolution)

		glEnable(GL_TEXTURE_2D)
		glDisable(GL_CULL_FACE)
		glBindTexture(GL_TEXTURE_2D, textureSaturnRing)
		glRotatef(-90, 1, .0, .0)
		glRotatef(item.orientation[2], 0, 1, 0)

		glRotatef(item.rotation.angPosition, .0, .0, 1)

		gluDisk(quadric, 1.1, 2, item.subdivision, item.subdivision/2)
		glEnable(GL_CULL_FACE);
		glPopMatrix()
		glDisable(GL_TEXTURE_2D)

def toggleShowOrbit():
	global showOrbit
	if showOrbit == True:
		showOrbit = False
	else:
		showOrbit = True

def drawScene():
	global listSpaceObjects

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	camera.update()
	glLightfv(GL_LIGHT0, GL_POSITION, [.0, .0, .0, 1])

	for i in listSpaceObjects:
		drawSpaceObject(i)
	glutSwapBuffers()

def resizeScene(width, height):
	global maxViewDistance
	if height == 0:
		height = 1

	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60, float(width)/float(height), 0.1, maxViewDistance*2) # todo
	glMatrixMode(GL_MODELVIEW)

### interaction ###
def keyPressed(key, x, y):
	global simulationVelocity, maxSimulationVelocity
	if key == chr(27):
		sys.exit()

	if key == '+' or key == 'l' or key == 'L':
		if simulationVelocity < maxSimulationVelocity:
			simulationVelocity += 1

	if key == '-' or key == 'j' or key == 'J':
		if simulationVelocity > - maxSimulationVelocity:
			simulationVelocity -= 1 

	if key == '0' or key == 'k' or key == 'K':
		simulationVelocity = 1

	if key == '5' or key == 'o' or key == 'O':
		toggleShowOrbit()

	if key == '4' or key == 'a' or key == 'A':
		camera.xOrbit += 1

	if key == '6' or key == 'd' or key == 'D':
		camera.xOrbit -= 1

	if key == '8' or key == 'w' or key == 'W':
		camera.yOrbit += 1

	if key == '2' or key == 's' or key == 'S':
		camera.yOrbit -= 1

	if key == '*' or key == 'x' or key == 'X':
		camera.zoom(+0.5)

	if key == '/' or key == 'z' or key == 'Z':
		camera.zoom(-0.5)

def mousePressed(button, state, x, y):
	global mousePrevStateRight, mousePrevStateMiddle, mousePrevStateLeft, mouseTracking, mouseX, mouseY, camera, showOrbit, update
	
	if button == 3:
		camera.zoom(-0.5) # forwards 
	elif button == 4:
		camera.zoom(0.5) # backwards

	if button == 2: # right mouse button
		if state == 0:	
			if mousePrevStateRight == 1: 
				#print "pressed"
				mouseX = x
				mouseY = y
				mouseTracking = True
				#print mouseTracking

		if state == 1:
			if mousePrevStateRight == 0:
				#print "released"
				mouseTracking = False
				camera.incrementOrientation()

	mousePrevStateRight = state

	if button == 0:
		if state == 0 and mousePrevStateLeft == 1:
			if update == True:
				update = False
			else:
				update = True
	mousePrevStateLeft = state

	if button == 1:
		if state == 0 and mousePrevStateMiddle == 1:
			toggleShowOrbit()
	mousePrevStateMiddle = state

def mouseMotion(x,y):
	global mouseX, mouseY, camera, mouseTracking
	if mouseTracking == True:
		coeff = 0.1
		xGap = (x - mouseX) * coeff
		yGap = (y - mouseY) * coeff
		camera.tempIncrementOrientation(xGap, yGap)

def main():
	global windowWidth, windowHeight, physicsThread

	glutInit()
	glutInitWindowSize(windowWidth, windowHeight)
	glutInitWindowPosition(windowX, windowY)
	glutCreateWindow("Assignment_2_Solar_System.py")
	glutReshapeFunc(resizeScene)
	#glutFullScreen()
	initScene()

	glutDisplayFunc(drawScene)
	glutIdleFunc(drawScene)
	glutKeyboardFunc(keyPressed)

	glutMouseFunc(mousePressed)
	glutMotionFunc(mouseMotion)

	glutMainLoop()

if __name__ == "__main__":
	print '\033[31m' + "Keyboard: (wasd zx lkj o)" + '\033[0m'
	print '\033[32m' + "\nNumeric Keypad(8426 */ +0- 5)" + '\033[0m'
	print '\033[34m' + "\nMouse(left, middle up, middle down, middle, left)" + '\033[0m'
	print "\nHit ESC key to quit."
	main()