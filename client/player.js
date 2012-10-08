function Player(id, x, y, rot) {
    //----------------------------
    // Initialization
    //----------------------------
    this.id = id;

    this.top = new jaws.Sprite({'image':"images/tanktop.png", x:x, y:y,'anchor_x':0.5, 'anchor_y':0.75});
    this.bottom = new jaws.Sprite({'image':"images/tankbot.png", x:x, y:y,'anchor':"center"});

    this.velocity = [0, 0];
    this.history = [];

    this.loading = false;

    this.draw = function() {
        //-------------------------------------
        // Draw my sprites. This is called every game loop
        //-------------------------------------
        this.bottom.draw();
        this.top.draw();
    }

    this.fire = function() {
        //----------------------------------
        // Fire a bullet
        //----------------------------------
        if (!this.loading) {
            this.loading = true;
            console.log(this); 
            setTimeout(function() { this.loading = false; }.bind(this), 1000)
        }
    }

    this.move = function(d) {
        //-----------------------------------
        // Move the tank forward or backwards
        // d - direction (w, s)
        //-----------------------------------
        var a = [0,0];

        var r = (this.bottom.angle + 90) * (Math.PI/180);

        a[0] += Math.cos(r)*.9
        a[1] += Math.sin(r)*.9

        var ff = .5

        this.velocity[0] *= ff;
        this.velocity[1] *= ff;

        this.velocity[0] += a[0]; 
        this.velocity[1] += a[1];

        if (d == 'w') {
            // Forward
            this.bottom.x -= this.velocity[0];
            this.bottom.y -= this.velocity[1];
            
            this.top.x -= this.velocity[0];
            this.top.y -= this.velocity[1];
        } else {
            // Backwards (s)
            this.bottom.x += this.velocity[0];
            this.bottom.y += this.velocity[1];

            this.top.x += this.velocity[0];
            this.top.y += this.velocity[1];
        }
    }

    this.rotate = function(d) {
        //----------------------------------
        // Rotate the tank base
        // d - direction (a, d)
        //----------------------------------
        if (d == 'a') {
            // Left
            this.bottom.angle -= 1;
        } else {
            // Right (d)
            this.bottom.angle += 1;
        }
    }

    this.rotateTurret = function(d) {
        //----------------------------------
        // Rotate the tank turret
        // d - direction (left, right)
        //----------------------------------
        if (d == 'left') {
            // Left
            this.top.angle -= 1;
        } else {
            // Right (right)
            this.top.angle += 1;
        }
    }

    this.logState = function(cts) {
        //----------------------------------------
        // Log your current state in your history
        // cts - current time stamp
        // ---------------------------------------
        this.history.push([cts, this.top.toJSON(), this.bottom.toJSON()]);  
    }

    this.correctPosition = function(y) {
        //-----------------------------------
        // Correct my position from a server update. 
        // This can be used by you or other players.
        // y - a json object representing you
        //-----------------------------------
        this.bottom.x = y.x;
        this.bottom.y = y.y;
        this.bottom.angle = y.rot;

        this.top.x = y.tx;
        this.top.y = y.ty;
        this.top.angle = y.trot;
    }

}
