function Bullet(id, x, y, rot) {
    //---------------------------
    // Initialization
    //---------------------------
    this.id = id;
    this.speed = 16;
    this.bullet = new jaws.Sprite({'image':'images/bluebullet.png', x:x, y:y,'anchor':'center'});
    this.bullet.angle = rot;
    this.draw = function() {
        //-------------------------------------
        // Draw my sprite and calculate my position. 
        // This is called every game loop. 
        // XXX Im not sure why I have to draw twice
        //-------------------------------------
        this.bullet.draw();
        var a = [0.0, 0.0]
        var r = (this.bullet.angle + 90) * (Math.PI/180);

        a[0] += Math.cos(r) * this.speed;
        a[1] += Math.sin(r) * this.speed;
        this.bullet.x -= a[0];
        this.bullet.y -= a[1];
        this.bullet.draw();
    }
}

