from math import cos, radians, sin

bulletid = 0

class Bullet(object):

    def __init__(self, world, owner, x, y, rot):
        global bulletid
        bulletid += 1
        self.id = bulletid

        self.world = world
        self.x = x
        self.y = y
        self.rot = rot
        self.owner = owner
        
        self.dead = False
        self.speed = 16
    
        #if the bullet has been broadcasted then we move
        #it over to the bullet_list
        self.broadcasted = False
        
        self.owner.new_bullets.append(self)
        self.world.add(self)

    def update(self):
        """
        Update the bullets location.
        Eventually do collision
        """
        
        if self in self.owner.new_bullets and self.broadcasted:
            self.owner.new_bullets.remove(self)
            self.owner.bullet_list.append(self)

        a = [0.0, 0.0]
        a[0] += cos(radians(self.rot+90)) * self.speed
        a[1] += sin(radians(self.rot+90)) * self.speed

        self.x -= a[0]
        self.y -= a[1]

        if self.x < -10 or self.y < -10 or self.x > 510 or self.y > 510:
            self.remove()

    def remove(self):
            self.owner.bullet_list.remove(self)
            self.world.remove(self)
            del(self)

    def toObj(self):
        
        return {
            "id":self.id,
            "x":self.x,
            "y":self.y,
            "rot":self.rot
        }
