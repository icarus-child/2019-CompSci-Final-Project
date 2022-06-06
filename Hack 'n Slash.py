import pygame, sys, random, math, ctypes, time
from pygame.locals import *
from SpriteAnimater import SpriteStripAnim as Sprite
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Comp-Sci Final Project *without* multiple scripts #
# Ethan Meier                                       #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# - might want to eventually make classes for the characters and maps

#ISSUES:
#   world 2 key (key 1) does not render if other key is picked up first

def ratio(n, ratio):
    return n*ratio

# Set up pygame.
pygame.init()
mainClock = pygame.time.Clock()
maxFPS = 120
frames = maxFPS / 12

# Set up the window.
original_WINDOWWIDTH = 750		
original_WINDOWHEIGHT = 600
WINDOWWIDTH = 750		
WINDOWHEIGHT = 600
universalScale = 1
universalScale_x = 1

windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 16)		
pygame.display.set_caption("Hack 'n Slash")
fullscreen = False

endGame = False

# Set up the colors.		
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create map variables
global currentMap
currentMap = 0

halfMapX = (WINDOWWIDTH/2)
halfMapY = (WINDOWHEIGHT/2)

# Create player variables
player = pygame.Rect(halfMapX - 128/2, halfMapY - 128/2, 128, 128)
playerImage = pygame.image.load('test_player.png').convert_alpha()	
playerStretchedImage = pygame.transform.scale(playerImage, (50, 32))
playerHitbox = pygame.Rect(halfMapX - 32, halfMapY - 80, 30, 10)

    # Create player animation specific variables
playerAnimation = True
dodgeAnimation = 0
playerAnim = [
    #0,1,2
    Sprite('player/player_animations/player_Idle_R.png', (0,0,64,64), 8, 1, True, frames*2),
    Sprite('player/player_animations/player_Run_R.png', (0,0,64,64), 8, 1, True, frames),
    Sprite('player/player_animations/player_Attack_R.png', (0,0,64,64), 6, 1, True, frames),
    #3,4,5
    Sprite('player/player_animations/player_Idle_L.png', (0,0,64,64), 8, 1, True, frames*2),
    Sprite('player/player_animations/player_Run_L.png', (0,0,64,64), 8, 1, True, frames),
    Sprite('player/player_animations/player_Attack_L.png', (0,0,64,64), 6, 1, True, frames),
    #6,7
    Sprite('player/player_animations/player_Attack_Up.png', (0,0,64,64), 4, 1, True, frames),
    Sprite('player/player_animations/player_Attack_Down.png', (0,0,64,64), 3, 1, True, frames)
    ]
activePlayerAnimation = playerAnim[3]
attackFrames = 0
    # Create player movement variables
moveLeft = False		
moveRight = False		
moveUp = False		
moveDown = False
dodge = False
playerAttack = False
playerMovespeed = 6
dodgeMaxDistance = 100
playerAttackRange = 50
playerHitboxMovementOffset = 4
movementReset = True
dodgeCooldown = 100
canMove = True
addedPlayerMovement = False
    # Create player combat variables
playerDamage = 5
playerHealth = 100
attackDirection = 'right'
attackTimer = 0
attacked = False

# Create camera variables
cameraOffsetX = 0
cameraMapOffsetX = 0
cameraMouseOffsetX = 0
cameraOffsetY = 0
cameraMapOffsetY = 0
cameraMouseOffsetY = 0
cameraPlayerHitboxMovementOffsetX = 0
cameraPlayerHitboxMovementOffsetY = 0
cameraPlayerCoordinates = 0

mouseCameraSensitivity = 5

# Misc. gameplay variables
(cameraEnemyHitboxCoordinatesX, cameraEnemyHitboxCoordinatesY) = (0,0)
characters = []
objects = []
boundaries = []
loaders = []
keys = []
endGame = []

lastminuterenders = []

artifactOneCollected = False
artifactTwoCollected = False
artifactThreeCollected = False
    #rendering above or below player
renderAbove_top = []
renderBelow_top = []
renderAbove_mid = []
renderBelow_mid = []
renderAbove_bot = []
renderBelow_bot = []
arrayOfArrays = [characters, objects, boundaries, loaders, keys, endGame, lastminuterenders, renderAbove_top, renderBelow_top,
                 renderAbove_mid, renderBelow_mid, renderAbove_bot,
                 renderBelow_bot]
timer = 0

# Test Enemy Class
class Enemy:
    'Base enemy class'

    # Object variables
    enemy = pygame.Rect(50, 50, 50, 32)
    hitbox = pygame.Rect(50, 50, 34, 22)
    hitboxOffsetX = 0
    hitboxOffsetY = 0
    image = playerStretchedImage
    hitCooldown = 0

    # Generic gameplay variables
    health = 20

    # Tags
    damagable = 0x0000000
    destroyed = False

    def __init__(self, inputHitboxOffsetX, inputHitboxOffsetY, inputImage):
        print ('Initiated Enemy Class.\n',
               'Doc:', self.__doc__)
        characters.append(self)
        self.hitboxOffsetX = inputHitboxOffsetX
        self.hitboxOffsetY = inputHitboxOffsetY
        self.image = inputImage

    def hit(self, damage):
        self.health -= damage
        self.hitCooldown = 80

    def perFrameCall(self):
        if self.hitCooldown > 0:
            self.hitCooldown -= 1 
    
    def destroy(self):
        self.destroyed = True
        print(self, 'destroyed')
        for i in arrayOfArrays:
            if contains(i, self):
                i.remove(self)
        self = None
        del self

    def __del__(self):
        print(self, 'deleted')        

# Map object class
class Object:
    'Class for objects contained within maps'

    being = pygame.Rect(50, 50, 50, 32)
    hitbox = pygame.Rect(50, 50, 34, 22)
    hitboxOffsetX = 0
    hitboxOffsetY = 0
    image = playerStretchedImage
    level = 0
    
    def __init__(self, image, x_size, scale, x, y, hitbox_X, hitbox_Y, hitbox_x_size, hitbox_y_size, hitboxVisible, layer, number):
        self.being = pygame.Rect(x, y, int(ratio(x_size, scale)), x_size)
        self.image = pygame.image.load(image).convert_alpha()
        self.scaledImage = pygame.transform.scale(self.image, (int(ratio(x_size, scale)), x_size))
        self.hitbox = pygame.Rect(hitbox_X, hitbox_Y, hitbox_x_size, hitbox_y_size)
        self.hitboxOffsetX = hitbox_X
        self.hitboxOffsetY = hitbox_Y
        self.number = number
        self.hitboxVisible = hitboxVisible
        self.level = layer

    def draw(self):
        if self.hitboxVisible:
            pygame.draw.rect(windowSurface, (255, 0, 0), (self.hitbox.x, self.hitbox.y, self.hitbox.width, self.hitbox.height))

class Boundary:
    'Class for boundaries contained within maps'

    existance = pygame.Rect(50, 50, 50, 32)
    hitbox = pygame.Rect(50, 50, 34, 22)
    hitboxOffsetX = 0
    hitboxOffsetY = 0
    
    def __init__(self, x, y, width, height, hitboxVisible, number):
        self.existance = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.number = number
        self.hitboxVisible = hitboxVisible

    def draw(self):
        if self.hitboxVisible:
            pygame.draw.rect(windowSurface, (255, 0, 0), (self.hitbox.x, self.hitbox.y, self.hitbox.width, self.hitbox.height))

class Loader:
    'Class for loading into new worlds'

    hitboxOffsetX = 0
    hitboxOffsetY = 0
    
    def __init__(self, world, x, y, width, height, hitboxVisible, number):
        self.existance = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.number = number
        self.hitboxVisible = hitboxVisible
        self.world = world

    def loadWorld(self):
        loadWorld(self.world)

    def draw(self):
        if self.hitboxVisible:
            pygame.draw.rect(windowSurface, (0, 0, 255), (self.hitbox.x, self.hitbox.y, self.hitbox.width, self.hitbox.height))        

class Key:
    'Class for unlocking new levels'
    
    x = False
    existance = pygame.Rect(50, 50, 50, 32)
    hitbox = pygame.Rect(50, 50, 34, 22)
    hitboxOffsetX = 0
    hitboxOffsetY = 0
    image = playerStretchedImage
    destroyed = False

    def __init__(self, image, x, y, w, w2, scale, world, hitboxVisible):
        self.existance = pygame.Rect(x, y, int(ratio(w, scale)), w)
        self.image = pygame.image.load(image).convert_alpha()
        self.scaledImage = pygame.transform.scale(self.image, (int(ratio(w2, scale)), w2))
        self.hitbox = pygame.Rect(x, y, int(ratio(w, scale)), w)
        self.image = self.scaledImage
        self.world = world
        self.hitboxVisible = hitboxVisible

    def draw(self):
        if self.hitboxVisible:
            pygame.draw.rect(windowSurface, (0, 0, 255), (self.hitbox.x, self.hitbox.y, self.hitbox.width, self.hitbox.height))        

        
    def unlock(self):
        global artifactOneCollected
        global artifactTwoCollected
        global artifactThreeCollected

        if self.world == 2:
            artifactOneCollected = True
        elif self.world == 3:
            artifactTwoCollected = True
        elif self.world == 4:
            artifactThreeCollected = True
        else:
            print("ERROR: There shouldn't be a key in this level")
        self.destroy()

    def destroy(self):
        global arrayOfArrays
        self.destroyed = True
        #print(self, 'destroyed')
        if contains(keys, self):
            keys.remove(self)
        if contains(currentMap.keys, self):
            currentMap.keys.remove(self)
        self = None
        del self

class endGameTrigger:
    'When activated, ends the game'

    existance = pygame.Rect(50, 50, 50, 32)
    hitbox = pygame.Rect(50, 50, 34, 22)
    hitboxOffsetX = 0
    hitboxOffsetY = 0
    
    def __init__(self, x, y, width, height, hitboxVisible, number):
        self.existance = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.number = number
        self.hitboxVisible = hitboxVisible

    def endgame(self):
        theEndOfTimes()

    def draw(self):
        if self.hitboxVisible:
            pygame.draw.rect(windowSurface, (0, 255, 0), (self.hitbox.x, self.hitbox.y, self.hitbox.width, self.hitbox.height))
        

# Map class
class Map:
    'Generic Map Class'

    number = 0

    def __init__(self, world, image, x, scale, x_pos, y_pos, spawnX, spawnY):
        print ('Initiated Map Class.\n',
                'Doc:', self.__doc__, '\n',
                'World:', world)

        self.world = world
        self.mapObject = pygame.Rect(x_pos, y_pos, x, scale)
        self.mapImage = pygame.image.load(image).convert_alpha()
        self.scaledMap = pygame.transform.scale(self.mapImage, (int(ratio(x, scale)), x))
        self.width = x
        self.height = int(ratio(x, scale))
        self.scale = scale
        self.spawnX = spawnX
        self.spawnY = spawnY

        self.objects = []
        self.boundaries = []
        self.loaders = []
        self.characters = []
        self.keys = []
        self.endGame = []

    def setupBorders(self, boundariesVisible):
        self.addBoundary(-700, -30, self.width+400, 20, boundariesVisible)
        self.addBoundary(-700, self.height-410, self.width+400, 20, boundariesVisible)
        self.addBoundary(-20, -500, 20, self.height-400, boundariesVisible)
        self.addBoundary(self.width+380, -500, 20, self.height-400, boundariesVisible)
    
    def addObject(self, object_name, image, x_size, scale, x, y, hitbox_X, hitbox_Y, hitbox_x_size, hitbox_y_size, hitboxVisible = False, layer = 'mid'):
        self.number += 1
        self.object = Object(image, x_size, scale, x, y, hitbox_X, hitbox_Y, hitbox_x_size, hitbox_y_size, hitboxVisible, layer, self.number)  
        self.objects.append(self.object)

    def addBoundary(self, x, y, width, height, hitboxVisible = False):
        self.number += 1
        self.boundary = Boundary(x, y, width, height, hitboxVisible, self.number)  
        self.boundaries.append(self.boundary)

    def addEndGame(self, x, y, width, height, hitboxVisible = False):
        self.number += 1
        self.endGameTrigger = endGameTrigger(x, y, width, height, hitboxVisible, self.number)  
        self.endGame.append(self.endGameTrigger)

    def addLoader(self, world, x, y, width, height, hitboxVisible = False):
        self.number += 1
        self.loader = Loader(world, x, y, width, height, hitboxVisible, self.number)  
        self.loaders.append(self.loader)

    def addKey(self, image, x, y, width, width2, scale, hitboxVisible):
        self.key = Key(image, x, y, width, width2, scale, self.world, hitboxVisible)  
        self.keys.append(self.key)
    
# Function to force a variable between two variables
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

# Function for checking player hitbox collision (no moving through walls)
# - Eliminate diagnal advantage
def playerMove(dx, dy):
    global cameraMapOffsetX
    global cameraMapOffsetY
    global cameraPlayerHitboxMovementOffsetX
    global cameraPlayerHitboxMovementOffsetY
    global addedPlayerMovement
    global objects
    global characters
    diagnalSpeed = 0
    up = False
    right = False
    down = False
    left = False
    canMoveUp = True
    canMoveRight = True
    canMoveDown = True
    canMoveLeft = True
    
    if dx < 0: # Moving right
        right = True
        left = False
        cameraPlayerHitboxMovementOffsetX = playerHitboxMovementOffset
    if dx > 0: #Moving left
        left = True
        right = False
        cameraPlayerHitboxMovementOffsetX = -playerHitboxMovementOffset
    if dy < 0: #Moving down
        down = True
        up = False
        cameraPlayerHitboxMovementOffsetY = playerHitboxMovementOffset
    if dy > 0: #Moving up
        up = True
        down = False
        cameraPlayerHitboxMovementOffsetY = -playerHitboxMovementOffset
    if dx == 0:
        right = False
        left = False
        cameraPlayerHitboxMovementOffsetX = 0
    if dy == 0:
        up = False
        down = False
        cameraPlayerHitboxMovementOffsetY = 0

    hitboxArray = []
    
    for i in characters:
        hitboxArray.append(i)
    for i in objects:
        hitboxArray.append(i)
    for i in boundaries:
        hitboxArray.append(i)

    for i in hitboxArray:
        if playerHitbox.colliderect(i.hitbox):
            if up:
                canMoveUp = False
            if right:
                canMoveRight = False
            if down:
                canMoveDown = False
            if left:
                canMoveLeft = False
##        if up and right and canMoveUp and canMoveRight:
##            cameraMapOffsetY += dy*diagnalSpeed
##            cameraMapOffsetX += dx*diagnalSpeed
##        elif down and right and canMoveDown and canMoveRight:
##            cameraMapOffsetY += dy*diagnalSpeed
##            cameraMapOffsetX += dx*diagnalSpeed
##        elif up and left and canMoveUp and canMoveLeft:
##            cameraMapOffsetY += dy*diagnalSpeed
##            cameraMapOffsetX += dx*diagnalSpeed
##        elif down and left and canMoveDown and canMoveLeft:
##            cameraMapOffsetY += dy*diagnalSpeed
##            cameraMapOffsetX += dx*diagnalSpeed

    if up and canMoveUp:
        cameraMapOffsetY += dy/1.5
    elif down and canMoveDown:
        cameraMapOffsetY += dy/1.5
    elif right and canMoveRight:
        cameraMapOffsetX += dx/1.5
    elif left and canMoveLeft:
        cameraMapOffsetX += dx/1.5

def contains(array, item):
    value = False
    for i in array[:]:
        if i == item:
            value = True
    return value    

currentAnimation = 'right'

global attackAnimationTimer
attackAnimationTimer = 0
def animationHandler():
    global attackDirection
    global currentAnimation
    global activePlayerAnimation
    global playerAttack
    global attackAnimationTimer
    global attackFrames
    attackAnimationTimer += 1
    if playerAnimation:
        if playerAttack and attackDirection == 'up':
            activePlayerAnimation = playerAnim[6].next()
            attackFrames = 4
        elif playerAttack and attackDirection == 'right':
            activePlayerAnimation = playerAnim[2].next()
            attackFrames = 6
        elif playerAttack and attackDirection == 'down':
            activePlayerAnimation = playerAnim[7].next()
            attackFrames = 3
        elif playerAttack and attackDirection == 'left':
            activePlayerAnimation = playerAnim[5].next()
            attackFrames = 6
        elif moveRight:
            activePlayerAnimation = playerAnim[1].next()
            currentAnimation = 'right'
            attackFrames = 0
            attackAnimationTimer = 0
        elif moveLeft:
            activePlayerAnimation = playerAnim[4].next()
            currentAnimation = 'left'
            attackFrames = 0
            attackAnimationTimer = 0
        elif moveDown:
            if currentAnimation == 'right':
                activePlayerAnimation = playerAnim[1].next()
            elif currentAnimation == 'left':
                activePlayerAnimation = playerAnim[4].next()
            attackFrames = 0
            attackAnimationTimer = 0
        elif moveUp:
            if currentAnimation == 'right':
                activePlayerAnimation = playerAnim[1].next()
            elif currentAnimation == 'left':
                activePlayerAnimation = playerAnim[4].next()
            attackFrames = 0
            attackAnimationTimer = 0
        else:
            # Idle animation
            if currentAnimation == 'right':
                activePlayerAnimation = playerAnim[0].next()
            elif currentAnimation == 'left':
                activePlayerAnimation = playerAnim[3].next()
            attackFrames = 0
            attackAnimationTimer = 0
            
        if attackAnimationTimer >= 120/12*attackFrames:
            playerAttack = False
            attackAnimationTimer = 0
    
def theEndOfTimes():
    print('The End.')
    time.sleep(2)
    pygame.quit()
    sys.exit()

def loadWorld(world):
    global currentMap
    global cameraMapOffsetX
    global cameraMapOffsetY
    global objects
    global boundaries
    global loaders
    global keys
    global endGame
    global artifactOneCollected
    global artifactTwoCollected
    global artifactThreeCollected
    global endGame
    #if currentMap != 0:
    
    if world == 1:
        print('###Loading world 1')
        Overworld = None
        Overworld = Map(1, 'Maps/Overworld/Overworld_Base.png', 1000, 1.4, 0, 0, -435, -300)

        Overworld.objects = []
        Overworld.loaders = []
        Overworld.boundaries = []
        Overworld.keys = []

        Overworld.addObject('Tree1', 'Maps/Overworld/Overworld_Tree1.png', 1000, 1.4, -700, -500, 235, 650, 52, 15, False)
        Overworld.addObject('Tree2', 'Maps/Overworld/Overworld_Tree2.png', 1000, 1.4, -700, -500, 640, 335, 52, 15, False)
        Overworld.addObject('Tree3', 'Maps/Overworld/Overworld_Tree3.png', 1000, 1.4, -700, -500, 1135, 450, 52, 15, False)

        Overworld.addObject('Bush1', 'Maps/Overworld/Bushes/Overworld_Bush1.png', 1000, 1.4, -700, -500, 195, 690, 52, 15, False, 'top')
        Overworld.addObject('Bush2', 'Maps/Overworld/Bushes/Overworld_Bush2.png', 1000, 1.4, -700, -500, 495, 530, 52, 15)
        Overworld.addObject('Bush3', 'Maps/Overworld/Bushes/Overworld_Bush3.png', 1000, 1.4, -700, -500, 168, 260, 52, 15)
        Overworld.addObject('Bush4', 'Maps/Overworld/Bushes/Overworld_Bush4.png', 1000, 1.4, -700, -500, 475, 310, 52, 15)
        Overworld.addObject('Bush5', 'Maps/Overworld/Bushes/Overworld_Bush5.png', 1000, 1.4, -700, -500, 950, 450, 52, 15)
        Overworld.addObject('Bush6', 'Maps/Overworld/Bushes/Overworld_Bush6.png', 1000, 1.4, -700, -500, 1280, 560, 52, 15)
        Overworld.addObject('Bush7', 'Maps/Overworld/Bushes/Overworld_Bush7.png', 1000, 1.4, -700, -500, 1180, 785, 52, 15)

        Overworld.addObject('Hedge', 'Maps/Overworld/Overworld_Hedge.png', 1000, 1.4, -700, -500, 0, 998, 1400, 15, False)

        Overworld.setupBorders(False)

        Overworld.addLoader(2, 190, -10, 100, 20, False)
        Overworld.addLoader(3, 1040, 110, 80, 20, False)
        Overworld.addLoader(4, 550, 970, 200, 20, False)
        Overworld.addLoader(5, -10, 335, 20, 60, False)

        currentMap = Overworld

        cameraMapOffsetX = Overworld.spawnX#Overworld.spawnX
        cameraMapOffsetY = Overworld.spawnY#Overworld.spawnY
        
    elif world == 2:
        print('###Loading world 2')
        Temple = None
        Temple = Map(2, 'Maps/Temple/Base.png', 1000, 1.4, 0, 0, 200, -600)
        
        Temple.objects = []
        Temple.loaders = []
        Temple.boundaries = []
        Temple.keys = []

        Temple.setupBorders(False)

        Temple.addLoader(1, 50, 980, 100, 20, False)

        if not artifactOneCollected:
            Temple.addKey('Maps/Temple/Level 2 Key.png', 400, 80, 50, 50, 1, False)
            print(' Artifact not collected')
        else:
            print(' Artifact collected')
            
        currentMap = Temple

        cameraMapOffsetX = Temple.spawnX
        cameraMapOffsetY = Temple.spawnY
    elif world == 3:
        print('###Loading world 3')

        Mine = None
        Mine = Map(3, 'Maps/Mine/Base.png', 1000, 1.4, 0, 0, 180, -420)

        Mine.objects = []
        Mine.loaders = []
        Mine.boundaries = []
        Mine.keys = []

        Mine.setupBorders(False)

        Mine.addBoundary(-608, 645, 1200, 20, False)
        Mine.addBoundary(-800, 825, 1800, 20, False)
        Mine.addBoundary(1288, -200, 20, 1000, False)
        Mine.addBoundary(1162, 400, 20, 170, False)
        Mine.addBoundary(-608, 454, 1200, 20, False)
        Mine.addBoundary(400, 158, 20, 200, False)
        Mine.addBoundary(218, 340, 200, 20, False)
        Mine.addBoundary(268, 340, 800, 20, False)
        Mine.addBoundary(218, 240, 200, 20, False)
        Mine.addBoundary(268, 240, 800, 20, False)
        Mine.addBoundary(488, 200, 20, 100, False)
        Mine.addBoundary(658, 200, 20, 100, False)
        Mine.addBoundary(0, 20, 600, 20, False)
        Mine.addBoundary(300, -150, 20, 280, False)
        Mine.addBoundary(850, -150, 20, 280, False)

        Mine.addLoader(1, 100, 550, 20, 200, False)

        if not artifactTwoCollected:
            Mine.addKey('Maps/Mine/Level 3 Key.png', 550, 80, 50, 50, 1, False)
            print(' Artifact not collected')
        else:
            print(' Artifact collected')

        currentMap = Mine

        cameraMapOffsetX = Mine.spawnX
        cameraMapOffsetY = Mine.spawnY
        
    elif world == 4:
        print('###Loading world 4')
        
        Mountain = None
        Mountain = Map(4, 'Maps/Mountain/Base.png', 1000, 1.4, 0, 0, -350, 250)
        
        Mountain.objects = []
        Mountain.loaders = []
        Mountain.boundaries = []
        Mountain.keys = []

        Mountain.setupBorders(False)

        Mountain.addLoader(1, 580, 0, 125, 20, False)
        
        Mountain.addBoundary(200, -75, 5, 150, False)
        Mountain.addBoundary(190, 125, 20, 5, False)
        Mountain.addBoundary(220, 125, 5, 20, False)
        Mountain.addBoundary(210, 150, 20, 5, False)
        Mountain.addBoundary(250, 150, 5, 20, False)
        Mountain.addBoundary(250, 175, 20, 5, False)
        Mountain.addBoundary(280, 175, 5, 20, False)
        Mountain.addBoundary(280, 200, 20, 5, False)
        Mountain.addBoundary(320, 200, 5, 20, False)
        Mountain.addBoundary(320, 225, 70, 5, False)
        Mountain.addBoundary(420, 225, 5, 20, False)
        Mountain.addBoundary(420, 250, 25, 5, False)
        Mountain.addBoundary(480, 250, 5, 20, False)
        Mountain.addBoundary(480, 275, 50, 5, False)
        Mountain.addBoundary(475, 290, 200, 5, False)
        Mountain.addBoundary(750, 275, 50, 5, False)
        Mountain.addBoundary(800, 260, 50, 5, False)
        Mountain.addBoundary(850, 245, 50, 5, False)
        Mountain.addBoundary(900, 230, 50, 5, False)
        Mountain.addBoundary(950, 220, 50, 5, False)
        Mountain.addBoundary(980, 210, 100, 5, False)
        Mountain.addBoundary(1100, 200, 50, 5, False)
        Mountain.addBoundary(1160, 185, 5, 10, False)
        Mountain.addBoundary(1150, 185, 50, 5, False)
        Mountain.addBoundary(1200, 175, 50, 5, False)
        Mountain.addBoundary(1250, -75, 5, 170, False)

        if not artifactThreeCollected:
            Mountain.addKey('Maps/Mountain/Level 4 Key_var1.png', 250, 20, 50, 50, 1, False)
            print(' Artifact not collected')
        else:
            print(' Artifact collected')
        
        currentMap = Mountain

        cameraMapOffsetX = Mountain.spawnX
        cameraMapOffsetY = Mountain.spawnY
    elif world == 5:
        print('###Loading world 5')

        Gate = None
        if artifactOneCollected and not artifactTwoCollected and not artifactThreeCollected:
            Gate = Map(5, 'Maps/Gate/Base -  1.png', 1000, 1.4, 0, 0, -980, -250)
        elif artifactTwoCollected and not artifactOneCollected and not artifactThreeCollected:
            Gate = Map(5, 'Maps/Gate/Base -  2.png', 1000, 1.4, 0, 0, -980, -250)
        elif artifactThreeCollected and not artifactOneCollected and not artifactTwoCollected:
            Gate = Map(5, 'Maps/Gate/Base -  3.png', 1000, 1.4, 0, 0, -980, -250)
        elif artifactOneCollected and artifactTwoCollected and not artifactThreeCollected:
            Gate = Map(5, 'Maps/Gate/Base -  1 2.png', 1000, 1.4, 0, 0, -980, -250)
        elif artifactOneCollected and artifactThreeCollected and not artifactTwoCollected:
            Gate = Map(5, 'Maps/Gate/Base -  1 3.png', 1000, 1.4, 0, 0, -980, -250)
        elif artifactTwoCollected and artifactThreeCollected and not artifactOneCollected:
            Gate = Map(5, 'Maps/Gate/Base -  2 3.png', 1000, 1.4, 0, 0, -980, -250)
        elif artifactOneCollected and artifactTwoCollected and artifactThreeCollected:
            Gate = Map(5, 'Maps/Gate/Base -  1 2 3.png', 1000, 1.4, 0, 0, -980, -250)
        else:
            Gate = Map(5, 'Maps/Gate/Base - 0.png', 1000, 1.4, 0, 0, -980, -250)

        Gate.objects = []
        Gate.loaders = []
        Gate.boundaries = []
        Gate.keys = []

        Gate.setupBorders(False)

        Gate.addLoader(1, 1380, 480, 20, 120, False)

        if artifactOneCollected and artifactTwoCollected and artifactThreeCollected:
            Gate.addLoader(6, 450, 480, 20, 120, False)
        
        Gate.addBoundary(-600, 640, 1500, 20, False)
        Gate.addBoundary(448, 480, 20, 120, False)
        Gate.addBoundary(-600, 520, 1500, 20, False)
        
        currentMap = Gate

        cameraMapOffsetX = -980
        cameraMapOffsetY = -250
                
    elif world == 6:
        print('###Loading world 6')

        Volcano = None
        Volcano = Map(6, 'Maps/Volcano/Base.png', 1000, 1.4, 0, 0, -320, -300)
        
        Volcano.objects = []
        Volcano.loaders = []
        Volcano.boundaries = []
        Volcano.keys = []
        Volcano.endGame = []

        Volcano.setupBorders(False)

        Volcano.addBoundary(700, 520, 400, 20, False)
        Volcano.addBoundary(1280, 320, 20, 460, False)
        
        Volcano.addBoundary(-90, 520, 400, 20, False)
        Volcano.addBoundary(100, 320, 20, 460, False)

        Volcano.addEndGame(300, 520, 400, 20, False)

        Volcano.addObject('Gate', 'Maps/Volcano/Gate.png', 1000, 1.4, -700, -500, 540, 836, 300, 30, False)

        currentMap = Volcano

        cameraMapOffsetX = Volcano.spawnX
        cameraMapOffsetY = Volcano.spawnY

    objects = []
    for i in currentMap.objects:
        objects.append(i)

    boundaries = []
    for i in currentMap.boundaries:
        boundaries.append(i)

    loaders = []
    for i in currentMap.loaders:
        loaders.append(i)

    characters = []
    for i in currentMap.characters:
        characters.append(i)

    keys = []
    for i in currentMap.keys:
        keys.append(i)

    endGame = []
    for i in currentMap.endGame:
        endGame.append(i)

loadWorld(1)

# Start Game Loop

while True:

    lastminuterenders = []
    keys = currentMap.keys
    addedPlayerMovement = False
    
    # Get the current mouse position
    mouseX, mouseY = pygame.mouse.get_pos()

    # Draw the white background
    windowSurface.fill((0, 10, 5))

    for i in characters[:]:
        if hasattr(i, 'perFrameCall'):
            i.perFrameCall()

    for i in objects[:]:
        if hasattr(i, 'perFrameCall'):
            i.perFrameCall()
    
    for event in pygame.event.get():
        # Check for the QUIT event.	
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:		
            # Change the keyboard variables.		
            if event.key == K_LEFT or event.key == K_a:		
                moveRight = False		
                moveLeft = True		
            if event.key == K_RIGHT or event.key == K_d:		
                moveLeft = False		
                moveRight = True		
            if event.key == K_UP or event.key == K_w:		
                moveDown = False		
                moveUp = True		
            if event.key == K_DOWN or event.key == K_s:		
                moveUp = False		
                moveDown = True		
        if event.type == KEYUP:
            # Exit program if 'escape' is pressed
            if event.key == K_ESCAPE:		
                    pygame.quit()		
                    sys.exit()
            if event.key == K_LEFT or event.key == K_a:		
                moveLeft = False		
            if event.key == K_RIGHT or event.key == K_d:		
                moveRight = False		
            if event.key == K_UP or event.key == K_w:		
                moveUp = False		
            if event.key == K_DOWN or event.key == K_s:		
                moveDown = False
            # Intiate 'Dodge' sequence
            if event.key == K_SPACE:		
                #dodge = True
                None
##            if event.key == K_f:
##                if not fullscreen:
##                    pygame.display.quit()
##                    pygame.display.init()
##                    ctypes.windll.user32.SetProcessDPIAware()
##                    true_res = (ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1))
##                    windowSurface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
##                    (WINDOWWIDTH, WINDOWHEIGHT) = true_res
##                    player.left = WINDOWWIDTH/2 - 128/2
##                    player.top = WINDOWHEIGHT/2 - 128/2
##                    fullscreen = True
##                else:
##                    pygame.display.quit()
##                    pygame.display.init()
##                    windowSurface = pygame.display.set_mode((original_WINDOWWIDTH, original_WINDOWHEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)		
##                    WINDOWWIDTH = original_WINDOWWIDTH
##                    WINDOWHEIGHT = original_WINDOWHEIGHT
##                    player.left = WINDOWWIDTH/2 - 128/2
##                    player.top = WINDOWHEIGHT/2 - 128/2
##                    fullscreen = False
        if event.type == MOUSEBUTTONUP:
            if (event.button == 3):
                #dodge = True
                None
            if (event.button == 1):
                playerAttack = True
        # Resize window
##        if event.type == VIDEORESIZE:
##            windowSurface = pygame.display.set_mode(event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
##            WINDOWWIDTH = event.dict['w']
##            WINDOWHEIGHT = event.dict['h']
##            universalScale_x = int(WINDOWWIDTH/original_WINDOWWIDTH)
                                   
    universalScale = (universalScale_x, int(ratio(universalScale_x, original_WINDOWWIDTH/original_WINDOWHEIGHT)))
    
    # Player Movement
    if canMove:
        diagnalSpeed = 0.000001
        if moveDown:
            playerMove(0, -playerMovespeed)
            movementReset = False
        if moveUp:		
            playerMove(0, playerMovespeed)
            movementReset = False
        if moveLeft:		
            playerMove(playerMovespeed, 0)
            movementReset = False
        if moveRight:		
            playerMove(-playerMovespeed, 0)
            movementReset = False
        if moveUp and moveRight:
            playerMove(-playerMovespeed*diagnalSpeed, playerMovespeed*diagnalSpeed)
        if moveDown and moveRight:
            playerMove(-playerMovespeed*diagnalSpeed, -playerMovespeed*diagnalSpeed)
        if moveDown and moveLeft:
            playerMove(playerMovespeed*diagnalSpeed, -playerMovespeed*diagnalSpeed)
        if moveUp and moveLeft:
            playerMove(playerMovespeed*diagnalSpeed, playerMovespeed*diagnalSpeed)
        if not moveDown and  not moveUp and not moveLeft and not moveRight:
            if not movementReset:
                playerMove(0, 0)
                movementReset = True
        if dodge:
            # Wait for first part of dodge animation to end
            dodgeAnimation += 1
            
            if dodgeAnimation > 0:
                # Get the current mouse position,
                # Calculate the distance from the player's center to the mouse
                x1 = (player.x + 25) + cameraMouseOffsetX
                y1 = (player.y + 16) + cameraMouseOffsetY
                x2 = mouseX
                y2 = mouseY

                # - Fix divide by zero problem. No, it's not fixed yet.
                try:
                    playerMouseDistance = math.sqrt(((x2 - x1)**2) + ((y2 - y1)**2))
                except ZeroDivisionError:
                    x2 += 1
                    y2 += 1
                    playerMouseDistance = 1
                
                # Clamp the distance at [insert max distance
                # - Make dodge more smooth
                dodgeDistance = clamp(playerMouseDistance, 0.1, dodgeMaxDistance)

                dodgeX = ((dodgeDistance/playerMouseDistance) * (x2 - x1))
                dodgeY = ((dodgeDistance/playerMouseDistance) * (y2 - y1))

                cameraMapOffsetX -= dodgeX
                cameraMapOffsetY -= dodgeY
                
                dodge = False
                dodgeAnimation = 0

    # Combat Handler
    # Player Combat
    if playerAttack:
        # Tell whether the mouse is above, below, to the left
        # or to the right of the player, favouring left and right if needed.
        # Depending on where the mouse is, spawn a 'sword' hitbox
        # - Give the hitbox space on either side of the player too.
        (playerX, playerY) = cameraPlayerCoordinates
        playerX = playerX + (player.height)/2
        playerY = playerY + (player.height)/2

        # Get a value for the rotational value of the
        # mouse relative to the player
        delta_x = mouseX - playerX
        delta_y = mouseY - playerY
        radians = math.atan2(delta_y, delta_x)
        degrees = radians * 180/math.pi
        if attacked == False:
            if degrees > -135 and degrees < -35: # Mouse is above player
                sword = pygame.Rect(playerHitbox.x - 15, playerHitbox.y - 60, 60, 80)
                pygame.draw.rect(windowSurface, (0, 0, 255), (playerHitbox.x - 15, playerHitbox.y - 60, 60, 80))
                attackDirection = 'up'
                attacked = True
                attackTimer = attackFrames*(120/12)-3
            elif degrees > -35 and degrees < 35: # Mouse is right of player
                sword = pygame.Rect(playerHitbox.x + 0, playerHitbox.y - 5, 60, 20)
                pygame.draw.rect(windowSurface, (0, 0, 255), (playerHitbox.x + 0, playerHitbox.y - 5, 80, 20))
                attackDirection = 'right'
                attacked = True
                attackTimer = attackFrames*(120/12)-3
            elif degrees > 35 and degrees < 135: # Mouse is below player
                sword = pygame.Rect(playerHitbox.x - 15, playerHitbox.y - 0, 60, 40)
                pygame.draw.rect(windowSurface, (0, 0, 255), (playerHitbox.x - 15, playerHitbox.y - 0, 60, 40))
                attackDirection = 'down'
                attacked = True
                attackTimer = attackFrames*(120/12)-3
            else: # Mouse is left of player
                sword = pygame.Rect(playerHitbox.x - 30, playerHitbox.y - 5, 60, 20)
                pygame.draw.rect(windowSurface, (0, 0, 255), (playerHitbox.x - 50, playerHitbox.y - 5, 80, 20))
                attackDirection = 'left'
                attacked = True
                attackTimer = attackFrames*(120/12)-3
            # Check if the sword hit anything
            for character in characters[:]:
                if sword.colliderect(character.hitbox) and hasattr(character, 'health') and character.hitCooldown == 0:
                    print('hit')
                    character.hit(playerDamage)
                    print(character.health)
            canMove = False
        else:
            attackTimer -= 1
            if attackTimer <= 0:
                attacked = False
                canMove = True
        
        sword = 0x000000
    
    # Animation Handler
    # Player Animations
    # - Only make left and right movement/idle animations and use the last
    # - used [left or right animation] (discern with same system used to determine left
    # - right idle) when moving up or down
    animationHandler()
            
    # - Figure out how to pass a string to a 'get' function and return the variable equvulent. 

    # Map Handler
    safeToHit = True
    for i in loaders[:]:
        if i.hitbox.colliderect(playerHitbox):
            i.loadWorld()
            safeToHit = False

    if safeToHit:
        for i in keys[:]:
            if i.hitbox.colliderect(playerHitbox):
                i.unlock()
                print('unlocked', i.world, 'key')

    for i in endGame[:]:
        if i.hitbox.colliderect(playerHitbox):
            i.endgame()

    # Destroy dead characters
    for character in characters[:]:
        if character.health <= 0 and character.destroyed == False:
            character.destroy()
    
    # Camera
        # Map a line from the center of the screen to the mouse and take the 1/5 point
    cameraMouseOffsetX = ((WINDOWWIDTH/2 - mouseX)/mouseCameraSensitivity)
    cameraMouseOffsetY = ((WINDOWHEIGHT/2 - mouseY)/mouseCameraSensitivity)
        # Transfer these calculations into more readable variables
    cameraMapCoordinates = (currentMap.mapObject.x + cameraOffsetX + cameraMouseOffsetX + cameraMapOffsetX, currentMap.mapObject.y + cameraOffsetY + cameraMouseOffsetY + cameraMapOffsetY)
    cameraPlayerCoordinates = (player.x + cameraOffsetX + cameraMouseOffsetX, player.y + cameraOffsetY + cameraMouseOffsetY)
    cameraPlayerHitboxCoordinates = (((player.x + 46) + cameraMouseOffsetX) + cameraPlayerHitboxMovementOffsetX, ((player.y + 85) + cameraMouseOffsetY) + cameraPlayerHitboxMovementOffsetY)
    for i in characters[:]:
        setattr(i, 'cameraCoordinates', (((i.enemy.x + i.enemy.width/2) + cameraMapOffsetX + cameraMouseOffsetX), ((i.enemy.y + i.enemy.height/2) + cameraMapOffsetY + cameraMouseOffsetY)))
        setattr(i, 'cameraHitboxCoordinates', (((i.enemy.x + i.enemy.width/2) + cameraMapOffsetX + cameraMouseOffsetX) + i.hitboxOffsetX, ((i.enemy.y + i.enemy.height/2) + cameraMapOffsetY + cameraMouseOffsetY) + i.hitboxOffsetY))
    for i in objects[:]:
        setattr(i, 'cameraCoordinates', (((i.being.x + i.being.width/2) + cameraMapOffsetX + cameraMouseOffsetX), ((i.being.y + i.being.height/2) + cameraMapOffsetY + cameraMouseOffsetY)))
        setattr(i, 'cameraHitboxCoordinates', (((i.being.x + i.being.width/2) + cameraMapOffsetX + cameraMouseOffsetX) + i.hitboxOffsetX, ((i.being.y + i.being.height/2) + cameraMapOffsetY + cameraMouseOffsetY) + i.hitboxOffsetY))
    for i in boundaries[:]:
        setattr(i, 'cameraCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX), ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY)))
        setattr(i, 'cameraHitboxCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX) + i.hitboxOffsetX, ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY) + i.hitboxOffsetY))
    for i in loaders[:]:
        setattr(i, 'cameraCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX), ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY)))
        setattr(i, 'cameraHitboxCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX) + i.hitboxOffsetX, ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY) + i.hitboxOffsetY))
    for i in keys[:]:
        setattr(i, 'cameraCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX), ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY)))
        setattr(i, 'cameraHitboxCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX) + i.hitboxOffsetX, ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY) + i.hitboxOffsetY))
    for i in endGame[:]:
        setattr(i, 'cameraCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX), ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY)))
        setattr(i, 'cameraHitboxCoordinates', (((i.existance.x + i.existance.width/2) + cameraMapOffsetX + cameraMouseOffsetX) + i.hitboxOffsetX, ((i.existance.y + i.existance.height/2) + cameraMapOffsetY + cameraMouseOffsetY) + i.hitboxOffsetY))
    #cameraEnemyCoordinates = (((Enemy.enemy.x + 25) + cameraMapOffsetX + cameraMouseOffsetX), ((Enemy.enemy.y + 16) + cameraMapOffsetY + cameraMouseOffsetY))
    #cameraEnemyHitboxCoordinates = (((Enemy.enemy.x + 25) + cameraMapOffsetX + cameraMouseOffsetX) + 16, ((Enemy.enemy.y + 16) + cameraMapOffsetY + cameraMouseOffsetY) + 8)
    
    # Recalculated location of hitbox coordinates
    (playerHitbox.left, playerHitbox.top) = cameraPlayerHitboxCoordinates
    for i in characters[:]:
        (i.hitbox.left, i.hitbox.top) = i.cameraHitboxCoordinates
    for i in objects[:]:
        (i.hitbox.left, i.hitbox.top) = i.cameraHitboxCoordinates
    for i in boundaries[:]:
        (i.hitbox.left, i.hitbox.top) = i.cameraHitboxCoordinates
    for i in loaders[:]:
        (i.hitbox.left, i.hitbox.top) = i.cameraHitboxCoordinates
    for i in keys[:]:
        (i.hitbox.left, i.hitbox.top) = i.cameraHitboxCoordinates
    for i in endGame[:]:
        (i.hitbox.left, i.hitbox.top) = i.cameraHitboxCoordinates
    
    timer += 1
    while (timer >= 100):
        timer = 0
    
    # Used for player hitbox visualization
    (cameraPlayerHitboxCoordinatesX, cameraPlayerHitboxCoordinatesY) = cameraPlayerHitboxCoordinates

    # Prepare to blit non-player characters and objects
    bot = []
    mid = []
    top = []
    renderBelow_bot = []
    renderBelow_mid = []
    renderBelow_top = []
    renderAbove_bot = []
    renderAbove_mid = []
    renderAbove_top = []
    
    for i in characters[:]:
        if hasattr(i,'level'):
            if i.level == 'bot':
                bot.append(i)
            elif i.level == 'mid':
                mid.append(i)
            elif i.level == 'top':
                top.append(i)
            else:
                print(i.level)
        else:
            mid.append(i)

    for i in objects[:]:
        if hasattr(i,'level'):
            if i.level == 'bot':
                bot.append(i)
            elif i.level == 'mid':
                mid.append(i)
            elif i.level == 'top':
                top.append(i)
            else:
                print(i.level)
        else:
            mid.append(i)

    for i in keys[:]:
        if hasattr(i,'level'):
            if i.level == 'bot':
                bot.append(i)
            elif i.level == 'mid':
                mid.append(i)
            elif i.level == 'top':
                top.append(i)
            else:
                print(i.level)
        else:
            mid.append(i)

    for i in bot:
        if i.hitbox.bottom - (playerHitboxMovementOffset + 5)> playerHitbox.top:
            if not contains(renderAbove_bot, i):
                renderAbove_bot.append(i)
            if contains(renderBelow_bot, i):
                renderBelow_bot.remove(i)
        else:
            if not contains(renderBelow_bot, i):
                renderBelow_bot.append(i)
            if contains(renderAbove_bot, i):
                renderAbove_bot.remove(i)

    for i in mid:
        if i.hitbox.bottom - (playerHitboxMovementOffset + 5)> playerHitbox.top:
            if not contains(renderAbove_mid, i):
                renderAbove_mid.append(i)
            if contains(renderBelow_mid, i):
                renderBelow_mid.remove(i)
        else:
            if not contains(renderBelow_mid, i):
                renderBelow_mid.append(i)
            if contains(renderAbove_mid, i):
                renderAbove_mid.remove(i)
                
    for i in top:
        if i.hitbox.bottom - (playerHitboxMovementOffset + 5)> playerHitbox.top:
            if not contains(renderAbove_top, i):
                renderAbove_top.append(i)
            if contains(renderBelow_top, i):
                renderBelow_top.remove(i)
        else:
            if not contains(renderBelow_top, i):
                renderBelow_top.append(i)
            if contains(renderAbove_top, i):
                renderAbove_top.remove(i)

    scaledPlayerAnimation = pygame.transform.scale2x(activePlayerAnimation)
    # Draw objects onto window
    windowSurface.blit(currentMap.scaledMap, cameraMapCoordinates)
    for i in renderBelow_bot[:]:
        if hasattr(i, 'scaledImage'):
            windowSurface.blit(i.scaledImage, i.cameraCoordinates)
        else:
            windowSurface.blit(i.image, i.cameraCoordinates)
            
    for i in renderBelow_mid[:]:
        if hasattr(i, 'scaledImage'):
            windowSurface.blit(i.scaledImage, i.cameraCoordinates)
        else:
            windowSurface.blit(i.image, i.cameraCoordinates)

    for i in renderBelow_top[:]:
        if hasattr(i, 'scaledImage'):
            windowSurface.blit(i.scaledImage, i.cameraCoordinates)
        else:
            windowSurface.blit(i.image, i.cameraCoordinates)
            
    windowSurface.blit(scaledPlayerAnimation, cameraPlayerCoordinates)
    for i in renderAbove_bot[:]:
        if hasattr(i, 'scaledImage'):
            windowSurface.blit(i.scaledImage, i.cameraCoordinates)
        else:
            windowSurface.blit(i.image, i.cameraCoordinates)

    for i in renderAbove_mid[:]:
        if hasattr(i, 'scaledImage'):
            windowSurface.blit(i.scaledImage, i.cameraCoordinates)
        else:
            windowSurface.blit(i.image, i.cameraCoordinates)

    for i in renderAbove_top[:]:
        if hasattr(i, 'scaledImage'):
            windowSurface.blit(i.scaledImage, i.cameraCoordinates)
        else:
            windowSurface.blit(i.image, i.cameraCoordinates)

    #pygame.draw.rect(windowSurface, (255, 0, 0), ((player.x + 60) + cameraMouseOffsetX, (player.y + 60) + cameraMouseOffsetY, 2, 2))
    #pygame.draw.rect(windowSurface, (255, 255, 0), (Enemy.hitbox.left, Enemy.hitbox.top, 34, 22))
    for i in objects[:]:
        if hasattr(i, 'draw'):
            i.draw()

    for i in boundaries[:]:
        if hasattr(i, 'draw'):
            i.draw()

    for i in loaders[:]:
        if hasattr(i, 'draw'):
            i.draw()

    for i in keys[:]:
        if hasattr(i, 'draw'):
            i.draw()

    for i in endGame[:]:
        if hasattr(i, 'draw'):
            i.draw()

    for i in lastminuterenders:
         pygame.draw.rect(windowSurface, (0, 255, 0), i)
    
    # Draw the window onto the screen.
    pygame.display.update()
    mainClock.tick(maxFPS)
