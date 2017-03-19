from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL.Image import *
from math import *
from random import randint
from random import random

windowX = 1200
windowY = 800
maxViewDistance = 50

minViewDistance = 0.5

distanzaTranslate = 0
tempRot = 0

mouseX = 0
mouseY = 0

mousePrevState = 1

mouseTracking = False

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

allClasses = ["star", "planet", "planet", "planet", "satellite", "planet", "planet", "planet", "planet", "planet"]

allTexture = ["00_Sole.jpg", "01_Mercurio.jpg", "02_Venere.jpg", "03_Terra.jpg", \
"03_01_Luna_2.jpg", "04_Marte.jpg", "05_Giove.jpg", "06_Saturno.jpg", "07_Urano.jpg", "08_Nettuno.jpg"]

celestialObjects = []

quadric = 0


class Rotation(object):
	def __init__(self, angPosition, angVelocity):
		self.angPosition = angPosition
		self.angVelocity = angVelocity
		self.name = "Rotation"

	def updatePosition(self):
		self.angPosition += self.angVelocity
		if self.angPosition >= 360:
			self.angPosition -= 360

		#print "update " + self.name

class Revolution(Rotation):
	def __init__(self, axisDistance, axis, angPosition, angVelocity, revolution = None):
		super(Revolution, self).__init__(angPosition, angVelocity)
		self.axisDistance = axisDistance
		self.axis = axis
		self.name = "Revolution"

		if revolution == None: # if it is empty, the Jedi is the first of the five initial
			self.revolution = None # set a random palanet
		else:
			self.revolution = revolution # set the mother planet

class Camera(object):

    def __init__(self):
    	global maxViewDistance
        self.x = 0
        self.y = 0
        self.z = maxViewDistance*.75 # moving forwars -Z moving backward +Z

        self.xLook = 0
        self.yLook = 0
        self.zLook = 0

        self.xRot = 0
        self.yRot = 1
        self.zRot = 0

        self.orbitX = 0
        self.orbitY = 0
        self.tempOrbitX = 0
        self.tempOrbitY = 0

        self.update()

    def incrementPosition(self, x, y, z):
    	global maxViewDistance, minViewDistance
        self.x = self.x + x
        self.y = self.y + y
        if self.z + z < maxViewDistance:
        	if self.z + z > minViewDistance:
        		self.z = self.z + z
        #print "%(x)s %(y)s %(z)s" % {"x":self.x, "y":self.y, "z":self.z}

    def setPosition(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def update(self):
        
        #glRotatef(self.orbitX + self.tempOrbitX, 0, 1, 0)
        #glRotatef(self.orbitY + self.tempOrbitY, 1, 0, 0)
        
        gluLookAt(self.x, self.y, self.z, \
            self.xLook, self.yLook, self.zLook,\
            self.xRot, self.yRot, self.zRot)

        ipsillon = self.orbitY + self.tempOrbitY
        segno = 1
        if ipsillon < -90:
        	segno = -1
        if ipsillon > +90:
        	segno = -1

        #print segno
        glRotate(self.orbitX + self.tempOrbitX, 0, 1, 0)
        angleX = radians((self.orbitX + self.tempOrbitX))
        
        xComp = cos(angleX)
        zComp = sin(angleX)

        #print (self.orbitY + self.tempOrbitY*segno)
        glRotate(self.orbitY + self.tempOrbitY, xComp, 0, zComp)

        #glPushMatrix()
        
        #glPopMatrix()
        #print self.orbitY

    def incrementOrientation(self):
        self.orbitX += self.tempOrbitX
        self.orbitY += self.tempOrbitY
        self.tempOrbitX = 0
        self.tempOrbitY = 0

    def tempIncrementOrientation(self, x, y):
        self.tempOrbitX = x
        self.tempOrbitY = y

""" CelestialObject contiene tutto il necessario per rappresentare l'oggetto,
	texture, posizione, rotazione, velocita ecc.. """
class celestialObject(object):

	def __init__ (self, name, classes, orientation, radius, rotation, revolution, orbit, pathImage):

		self.name = name
		self.classes = classes
		self.orientation = orientation
		self.radius = radius
		self.rotation =  rotation
		self.revolution = revolution
		self.orbit = orbit
		self.pathImage = pathImage
		self.texture = pathImage

	def update(self):
		self.rotation.updatePosition()
		self.revolution.updatePosition()

def creaCorpiCelesti2():
	global celestialObjects, maxViewDistance

	coeffDiam = 0.3
	coeffDist = 7
	gapDist = 0
	coeffRevo = .35
	coeffRot = 0.5
	coeffRevoSatellites = 10

	celestialObjects = []
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

		revolution = Revolution(dist, [0,1,0],randint(0,360),revo)
		radius = log(diameters[i]/2, 10) * coeffDiam
		#print revo
		celestialObjects.append(celestialObject(allTexture[i], allClasses[i], [0, 0, inclination[i]], radius, rotation, revolution, False, allTexture[i]))

	celestialObjects[4].revolution.revolution = celestialObjects[3].revolution

	createAsteroids(coeffDist, gapDist, coeffRevo)
	#celestial	

	rotation = Rotation(0, -(360/rotations[0])*coeffRevo*0.1)
	revolution = Revolution(0, [0,0,0],0,0)
	celestialObjects.append(celestialObject("sky", "environment",  [0, 0, 45],\
		maxViewDistance, rotation, revolution, False, "The_Milky_Way.jpg"))

def createAsteroids(coeffDist,gapDist, coeffRevo):
	for i in range(0, 50):

		rotation = Rotation(0, 0)
		rand = random()
		minDistance = revolutionRadius[5]
		maxDistance = revolutionRadius[6]
		gapDistance = maxDistance - minDistance
		dist = rand * gapDistance + minDistance
		dist = (log(dist, 10) * coeffDist) - gapDist
		minRevolution = revolutions[5]
		maxRevolution = revolutions[6]
		gapRevolution = maxRevolution - minRevolution
		revo = rand * gapRevolution + minRevolution
		revolution = Revolution(dist, [0,1,0],randint(0,360), 1/log(revo, 10) * coeffRevo)
		celestialObjects.append(celestialObject("Asteroid","asteroid", [0,0,0], randint(10,40)*0.001, rotation, revolution, False, "04.5_Asteroid_2.jpg")) 

def creaCorpiCelesti(FromThe):
    global celestialObjects, maxViewDistance

    timeCoeff = 1

    #for i range(0, len(planet)):

	    #rotation = Rotation(i[0], i[1])
	    #revolution = Revolution(i[2], [i[3],i[4],i[5]],i[6],i[7]*timeCoeff)
	    #celestialObjects = [celestialObject(i[8], i[9], rotation, revolution, i[10])]

    ### sun ###
    #planet = [angleRot, angleVel, distanceSun, rivAxis, angleRiv, angleRivVel, name, radius, image]
    rotation = Rotation(0, 0.5)
    revolution = Revolution(0, [0,0,0],0,0*timeCoeff)
    celestialObjects = [celestialObject("Sole", 2.0, rotation, revolution, "00_Sole.jpg")]

    ### mercury ###
    rotation = Rotation(0, 1)
    revolution = Revolution(4, [0,1,0],0,0.41*timeCoeff)
    celestialObjects.append(celestialObject("Mercurio", .5, rotation, revolution, "01_Mercurio.jpg"))

    ### venus ###
    rotation = Rotation(0, 1)
    revolution = Revolution(6, [0,1,0],0,0.31*timeCoeff)
    celestialObjects.append(celestialObject("Venere", .5, rotation, revolution, "02_Venere.jpg"))

    ### earth ###
    rotation = Rotation(0, 1.2)
    revolution = Revolution(8, [0,1,0],0,0.21*timeCoeff)
    celestialObjects.append(celestialObject("Terra", .5, rotation, revolution, "03_Terra.jpg"))

    ### earth ###
    rotation = Rotation(0, 1*timeCoeff)
    revolution = Revolution(1, [0,1,0],0, 1*timeCoeff, revolution)
    celestialObjects.append(celestialObject("Luna", .2, rotation, revolution, "03_01_Luna_2.jpg"))

    ### mars ###
    rotation = Rotation(0, 1)
    revolution = Revolution(10, [0,1,0],0,0.11*timeCoeff)
    celestialObjects.append(celestialObject("Marte", .5, rotation, revolution, "04_Marte.jpg"))

    ### mars ###
    rotation = Rotation(0, 1)
    revolution = Revolution(12, [0,1,0],0,0.11*timeCoeff)
    celestialObjects.append(celestialObject("Giove", .5, rotation, revolution, "05_Giove.jpg"))

    ### mars ###
    rotation = Rotation(0, 1)
    revolution = Revolution(14, [0,1,0],0,0.11*timeCoeff)
    celestialObjects.append(celestialObject("Saturno", .5, rotation, revolution, "06_Saturno.jpg"))

    ### mars ###
    rotation = Rotation(0, 1)
    revolution = Revolution(16, [0,1,0],0,0.11*timeCoeff)
    celestialObjects.append(celestialObject("Urano", .5, rotation, revolution, "07_Urano.jpg"))

    ### mars ###
    rotation = Rotation(0, 1)
    revolution = Revolution(18, [0,1,0],0,0.11*timeCoeff)
    celestialObjects.append(celestialObject("Nettuno", .5, rotation, revolution, "08_Nettuno.jpg"))

    ### mars ###
    rotation = Rotation(0, 0.01)
    revolution = Revolution(0, [0,0,0],0,0*timeCoeff)
    celestialObjects.append(celestialObject("sky", maxViewDistance, rotation, revolution, "skyMap.jpg"))

def initData():
    global quadric, camera, celestialObjects, windowX, windowY
    camera = Camera()
    
    #gluPerspective(60.0, float(windowX)/float(windowY), 0, 60.0)
    #creaCorpiCelesti()
    creaCorpiCelesti2()
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)

    #glEnable(GL_LIGHTING)          # Enable lighting
    #glEnable(GL_LIGHT0)            # Enable light #0
    #glEnable(GL_LIGHT1)            # Enable light #1
    #glEnable(GL_LIGHT2)  
    quadric = gluNewQuadric()

    for celOb in celestialObjects:
    	celOb.texture = initTexture2(celOb.pathImage)

def initTexture(pathImage):
	
	### load image from hd ###
	image = open(pathImage)
	imageX = image.size[0]
	imageY = image.size[1]
	image = image.tobytes("raw", "RGBX", 0, -1)


	glEnable(GL_TEXTURE_2D)
	texture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, texture)
	glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
	glTexImage2D(GL_TEXTURE_2D, 0, 3, imageX, imageY, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
	
	gluQuadricTexture(quadric, 1)
	
	glDisable(GL_TEXTURE_2D)

	return texture

def initTexture2(pathImage):
    image = open(pathImage)

    ix = image.size[0]
    iy = image.size[1]
    
    image_bytes  = image.convert("RGBA").tobytes( "raw", "RGBA", 0, -1)
    texture = glGenTextures(1)

    glBindTexture( GL_TEXTURE_2D, texture )
   
    gluBuild2DMipmaps ( GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image_bytes )
    gluQuadricTexture(quadric, 1)
    return texture

def drawScene():
	global celestialObjects
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	camera.update()

	for celOb in celestialObjects:
		drawObject(celOb)

	glutSwapBuffers()

def drawObject(item):
	global quadric

	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, item.texture)
	glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
	glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
	glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_LINEAR )
	glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )

		
	#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)       #set the texture's stretching properties
	#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) #GL_LINEAR
	#glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

	item.update()
	#glLoadIdentity()
	
	if item.orbit:
		addOrbit(item.revolution)

	glPushMatrix()

	recursiveRevolution(item.revolution)
	
	glRotatef(-90, 1, 0.0, 0.0)
	#glRotatef(-90, 1, 0.0, 0.0)
	glRotatef(item.orientation[2], 0, 1, 0)

	glRotatef(item.rotation.angPosition,0.0,0.0,1.0)            # Rotate The Cube On It's Z Axis

	gluSphere(quadric, item.radius, 40, 40)

	glPopMatrix()
	glDisable(GL_TEXTURE_2D)

	#define PI_GRECO 3.14159f

def addOrbit(revolution):
	glPushMatrix()
	
	axis = revolution.axis
	glRotate(revolution.angPosition, axis[0], axis[1], axis[2])
	glRotatef(90, 1, 0, 0)
	glRotatef(-180, 0, 0, 1)
	fRadius = revolution.axisDistance #* 2 + (-item.radius)
	#print fRadius
	fCenterX = 0.0 
	fCenterY = 0.0 

	glBegin(GL_LINE_STRIP)
	i = 0
	while(i<3.14*1.5):

		fX = fCenterX + (fRadius* (sin(i)))
		fY = fCenterY + (fRadius* (cos(i)))

		glVertex3f(fX, fY, 0);
		i +=0.01
	glEnd();

	glPopMatrix()

def recursiveRevolution(revolution):
	axis = revolution.axis

	if revolution.revolution != None:
		recursiveRevolution(revolution.revolution)

	glRotate(revolution.angPosition, axis[0], axis[1], axis[2])
	glTranslate(revolution.axisDistance, 0, 0)
	glRotate(-revolution.angPosition, axis[0], axis[1], axis[2])

def keyPressed(key,x,y):
    if key == chr(27):
        sys.exit()

def mousePressed(button, state, x, y):
    global mousePrevState, mouseTracking, mouseX, mouseY, camera
    if button == 3:
        camera.incrementPosition(0,0,-0.5)
        #print camera.z
    elif button == 4:
        camera.incrementPosition(0,0,0.5)
        #print camera.z

    if button == 2:
                
        if state == 0:
            if mousePrevState == 1:
                    #print "pressed"
                    mouseX = x
                    mouseY = y
                    mouseTracking = True
            #print "movim"

        if state == 1:
            if mousePrevState == 0:
                #print "released"
                mouseTracking = False
                camera.incrementOrientation()
    
    mousePrevState = state

        #camera.incrementPosition() 

def mouseMotion(x, y):
    global mouseX, mouseY, mouseTracking, camera
    if mouseTracking == True:
        coeff = 0.1
        
        X = (x - mouseX)*coeff
       
        Y = (y - mouseY)*coeff
        
        camera.tempIncrementOrientation(X, Y)

def resizeScene(windowX, windowY):
	global maxViewDistance
	if windowY == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
		windowY = 1

	glViewport(0, 0, windowX, windowY)        # Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60.0, float(windowX)/float(windowY), 0.1, maxViewDistance*2)
	glMatrixMode(GL_MODELVIEW)

def main():
	global windowX, windowY
	glutInit() # necessaria per inizializzare

	glutInitWindowSize(windowX, windowY) # imposta le dimensioni della finestra
	glutInitWindowPosition(100, 100) # coordinate di posizione della finestra
	glutCreateWindow("Solar System.py") # creazione e titolo della finestra

	glutKeyboardFunc(keyPressed) # permette di chiamare la funzione keyPressed quando un tasto viene premuto

	glutDisplayFunc(drawScene)

	# Uncomment this line to get full screen.
	# glutFullScreen()
	glutIdleFunc(drawScene)

	# Register the function called when our window is resized.
	glutReshapeFunc(resizeScene)

	# Register the function called when the keyboard is pressed.  
	glutKeyboardFunc(keyPressed)

	#
	glutMouseFunc(mousePressed)
	glutMotionFunc(mouseMotion)
	initData() # inizializzo i dati

	glutMainLoop()

if __name__ == "__main__":
	print "Hit ESC key to quit."
	main()