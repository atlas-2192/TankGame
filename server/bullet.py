from math import cos, radians, sin

bulletid = 0

class Bullet(object):

    def __init__(self, x, y, rot, owner):
        global bulletid
        bulletid += 1
        self.id = bulletid
        self.x = x
        self.y = y
        self.rot = rot
        self.owner = owner
        
        self.dead = False
        self.speed = 16

    def update(self):
        """
        Update the bullets location.
        Eventually do collision
        """

        a = [0.0, 0.0]
        a[0] += cos(radians(self.rot+90)) * self.speed
        a[1] += sin(radians(self.rot+90)) * self.speed

        self.x -= a[0]
        self.y -= a[1]

        if self.x < 0 or self.y < 0:
            self.owner.bullet_list.remove(self)
            del(self)

        elif self.x > 500 or self.y > 500:
            self.owner.bullet_list.remove(self)
            del(self)

    def toObj(self):
        
        return {
            "id":self.id,
            "x":self.x,
            "y":self.y,
            "rot":self.rot
        }
