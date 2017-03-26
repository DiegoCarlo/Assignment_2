from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL.Image import *
from math import *
from random import randint
from random import random

### window dimension ###
windowX = 600
windowY = 400

### mouse ###
mouseX = 0
mouseY = 0
mousePrevStateRight = 1 # button pressed or not
mousePrevStateLeft = 1
mouseTracking = False# ready or not to register movements

### view parameters ###
maxViewDistance = 50
minViewDistance = 2.5


### all object ###
listSpaceObjects = None

quadric = None

camera = None

showOrbit = False


### The numerical values shown here have been taken from wikipedia ###
### These are the distances of the main objects from their center of revolution  (x * 10^9 meters) ###
revolutionRadius = [0.00, 57.90, 108.20, 149.60, 0.384, 227.90, 778.30, 1427.00, 2871.00, 4497.10]
### The diameters of the main objects (x * 10^6 meters) ###
diameters = [1391.400, 4.878, 12.102, 12.756, 3.476, 6.786, 142.984, 120.536, 51.118, 49.528]
### The durations of the revolution of the main objects (x day) ###
revolutions = [0, 87.969, 224.700, 365.256, 27.321, 686.96, 4333.286, 10756.199, 30707.043, 60223.352]
### The durations of the bodies of rotation on its own axis (x hours) ###
rotations = [654.6, 1403.667, 5816.083, 23.934, 653.930, 24.555, 9.897, 10.755, 17.192, 16.11] 

inclination = [0, 0.01, 177.36, 23.43, 1.54, 25.19, 3.13, 26.73, 97.77, 28.32]
#rotations = [26.5, 58.65, -243.01, 0.997, 27.32, 1.026, 0.41, 0.426, -0.746, 0.8]

### star, planet, satellite, environment ###
allClasses = ["star", "planet", "planet", "planet", "satellite", "planet", "planet", "planet", "planet", "planet"]

allTexture = ["00_Sole.jpg", "01_Mercurio.jpg", "02_Venere.jpg", "03_Terra.jpg", \
"03_01_Luna_2.jpg", "04_Marte.jpg", "05_Giove.jpg", "06_Saturno.jpg", "07_Urano.jpg", "08_Nettuno.jpg"]

textureSaturnRing = None

class Camera(object):

	def __init__(self):
		global maxViewDistance

		self.z = maxViewDistance * 0.75 # moving forwards -z moving backwards + z

		self.xOrbit = 0
		self.yOrbit = 5

		self.xOrbitTemp = 0
		self.yOrbitTemp = 0

		self.update()

	def zoom(self, z):
		global maxViewDistance, minViewDistance

		temp = self.z + z
		if temp > minViewDistance and temp < maxViewDistance:
			self.z = temp

	''' x,y are mouse coordinates, not scene axis '''
	def update(self):

		gluLookAt(0, 0, self.z, \
			0, 0, 0, \
			0, 1, 0)

		glRotate(self.xOrbit + self.xOrbitTemp, 0, 1, 0)

		angleX = radians((self.xOrbit + self.xOrbitTemp))
		xComp = cos(angleX)
		zComp = sin(angleX)
		glRotate(self.yOrbit + self.yOrbitTemp, xComp, 0, zComp)

	def incrementOrientation(self):
		self.xOrbit += self.xOrbitTemp
		self.yOrbit += self.yOrbitTemp
		self.xOrbitTemp = 0
		self.yOrbitTemp = 0

	def tempIncrementOrientation(self, x, y):
		self.xOrbitTemp = x
		self.yOrbitTemp = y

class Rotation(object):
	def __init__(self, angPosition, angVelocity):
		self.angPosition = angPosition
		self.angVelocity = angVelocity

	def update(self):
		self.angPosition += self.angVelocity
		if self.angPosition >= 360:
			self.angPosition -= 360

class Revolution(Rotation):
	def __init__(self, axisDistance, axis, angPosition, angVelocity, visible, idRootRevolution = None):
		super(Revolution, self).__init__(angPosition, angVelocity)
		self.axisDistance = axisDistance
		self.axis = axis
		self.visible = visible
		if idRootRevolution != None:
			self.idRootRevolution = idRootRevolution
		else:
			self.idRootRevolution = None

	def update(self):
		super(Revolution, self).update()

class SpaceObject(object):

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

	def update(self):
		self.rotation.update()
		self.revolution.update()

def initTexture(pathImage):
	global quadric
	image = open(pathImage)

	ix = image.size[0]
	iy = image.size[1]

	image_bytes = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
	texture = glGenTextures(1)

	glBindTexture(GL_TEXTURE_2D, texture)

	gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image_bytes)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_LINEAR )
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
	gluQuadricTexture(quadric, 1)

	return texture

def createSpaceObject():
	global listSpaceObjects, maxViewDistance

	coeffDiam = 0.45
	coeffDist = 10
	gapDist = 0
	coeffRevo = 0.35
	coeffRot = 0.5
	coeffRevoSatellites = 10
	subdivision = 60

	listSpaceObjects = []
	### create all planet and moon ###
	for i in range(0, len(diameters)):

		rot = 360/rotations[i]
		rotation = Rotation(0, rot * coeffRot)

		dist = 0
		if revolutionRadius[i] != 0:
			dist = (log(revolutionRadius[i], 10) * coeffDist) - gapDist
			#print log(revolutionRadius[i], 10)

		if i == 4:
			dist = 1

		revo = 0
		if revolutions[i] != 0:
			revo = 1/log(revolutions[i], 10) * coeffRevo

		if allClasses[i] == "satellite":
			revo = revo * coeffRevoSatellites

		revolution = Revolution(dist, [0,1,0],randint(0,360),revo, True)
		radius = log(diameters[i]/2, 10) * coeffDiam
		#print revo
		listSpaceObjects.append(SpaceObject(allClasses[i],[0,0,inclination[i]], radius, rotation, \
			revolution, allTexture[i], subdivision))

	### set mun as satellite ###
	listSpaceObjects[4].revolution.idRootRevolution = 3


	createAsteroids(coeffDist, coeffDiam, gapDist, coeffRevo, 8)

	rotation = Rotation(0, -0.02)
	revolution = Revolution(0,[0,1,0],0,0, False)
	listSpaceObjects.append(SpaceObject("environment",[0,0,45], maxViewDistance, rotation, \
		revolution, "The_Milky_Way.jpg", subdivision))	

def createAsteroids(coeffDist, coeffDiam, gapDist, coeffRevo, subdivision):
	for i in range(0, 300):

		rotation = Rotation(0, 0)
		rand = random()
		minDistance = revolutionRadius[5] + 50
		maxDistance = revolutionRadius[6] - 250
		gapDistance = maxDistance - minDistance
		dist = rand * gapDistance + minDistance
		dist = (log(dist, 10) * coeffDist) - gapDist
		minRevolution = revolutions[5]
		maxRevolution = revolutions[6]
		gapRevolution = maxRevolution - minRevolution
		revo = rand * gapRevolution + minRevolution
		revolution = Revolution(dist, [0,1,0],randint(0,360), 1/log(revo, 10) * coeffRevo, False)
		listSpaceObjects.append(SpaceObject("asteroid",[0,0,0], randint(10,40)*coeffDiam*0.0025, rotation, \
		revolution, "04.5_Asteroid_2.jpg", subdivision)) 

def initScene():
	global quadric, listSpaceObjects, camera, textureSaturnRing

	createSpaceObject()

	glEnable(GL_DEPTH_TEST)

	glEnable(GL_COLOR_MATERIAL)
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	#glEnable(GL_NORMALIZE)

	#Parameters for correct shading
	glShadeModel(GL_SMOOTH)
	glDepthFunc(GL_LEQUAL)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
	glCullFace(GL_BACK)
	glEnable(GL_CULL_FACE)
	glClearColor(0.0, 0.0, 0.0, 0.0)

	quadric = gluNewQuadric()

	for i in listSpaceObjects:
		i.texture = initTexture(i.pathImage)

	textureSaturnRing = initTexture("06_01_Anelli.jpg") #06_01_Anelli.jpg")

	camera = Camera()

def revolutionRoot(revolution):
	global showOrbit
	if revolution.idRootRevolution >= 0 and revolution.idRootRevolution < len(listSpaceObjects):
		revolutionRoot(listSpaceObjects[revolution.idRootRevolution].revolution)
	
	axis = revolution.axis

	if showOrbit == True and revolution.visible == True:
		glPushMatrix()
		glRotate(revolution.angPosition, axis[0], axis[1], axis[2])
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

	glRotate(revolution.angPosition, axis[0], axis[1], axis[2])
	glTranslate(revolution.axisDistance, 0, 0)
	glRotate(-revolution.angPosition, axis[0], axis[1], axis[2])

def drawSpaceObject(item):
	global quadric, textureSaturnRing

	item.update() ## todo, questa va messa in un thread a parte

	glPushMatrix()

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
		glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [.9, .9, .9, .0]) #with this, the sun EMITS light
		glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 70)
	
	revolutionRoot(item.revolution)

	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, item.texture)
	glRotatef(-90, 1, .0, .0)
	glRotatef(item.orientation[2], 0, 1, 0)

	glRotatef(item.rotation.angPosition, .0, .0, 1)
	
	if item.classes == "environment":
		gluQuadricOrientation(quadric, GLU_INSIDE)
		gluSphere(quadric, item.radius, item.subdivision, item.subdivision)
		gluQuadricOrientation(quadric, GLU_OUTSIDE)
	else:
		gluSphere(quadric, item.radius, item.subdivision, item.subdivision)

	glPopMatrix()
	glDisable(GL_TEXTURE_2D)


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

def keyPressed(key, x, y):
	if key == chr(27):
		sys.exit()

def mousePressed(button, state, x, y):
	global mousePrevStateRight, mousePrevStateLeft, mouseTracking, mouseX, mouseY, camera, showOrbit
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
			if showOrbit == True:
				showOrbit = False
			else:
				showOrbit = True
	mousePrevStateLeft = state

def mouseMotion(x,y):
	global mouseX, mouseY, camera, mouseTracking
	if mouseTracking == True:
		coeff = 0.1
		xGap = (x - mouseX) * coeff
		yGap = (y - mouseY) * coeff
		camera.tempIncrementOrientation(xGap, yGap)

def main():
	global windowX, windowY

	glutInit()
	glutInitWindowSize(windowX, windowY)
	glutInitWindowPosition(100,100)
	glutCreateWindow("Assignment_2_Solar_System.py")
	glutReshapeFunc(resizeScene)
	glutFullScreen()
	initScene()

	glutDisplayFunc(drawScene)
	glutIdleFunc(drawScene)

	glutKeyboardFunc(keyPressed)

	glutMouseFunc(mousePressed)
	glutMotionFunc(mouseMotion)

	glutMainLoop()

if __name__ == "__main__":
	print "Hit ESC key to quit."
	main()