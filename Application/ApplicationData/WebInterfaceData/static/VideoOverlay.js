class VideoOverlay{
    constructor() {
        this.stream  = document.getElementById("stream");
        this.canvas = document.getElementById("canvas");
        this.context = this.canvas.getContext('2d');
        this.thickness = 1;
        this.offset = Math.floor(this.thickness/2);
    }

    renderGrid(){
        let width = this.stream.clientWidth;
        let height = this.stream.clientHeight;
        let w = width / 3;
        let h = height / 3;
		this.context.fillStyle = 'red';

        this.context.fillRect(w - this.offset, 0, this.thickness, height);
        this.context.fillRect(w * 2 - this.offset, 0, this.thickness, height);
        this.context.fillRect(0, h - this.offset, width, this.thickness);
        this.context.fillRect(0, h * 2 - this.offset, width, this.thickness);
    }

	prepareRender()
	{
		let width = this.stream.clientWidth;
        let height = this.stream.clientHeight;
        this.canvas.width = width;
        this.canvas.height = height;
        
		this.context.clearRect(0,0,width,height);
	}

	renderDetection(top, left, bottom, right, label, score){
		
		this.context.strokeStyle  = 'green';
		this.context.fillStyle = 'green';
		let width = this.stream.clientWidth;
        let height = this.stream.clientHeight;

		let boxx = left*width;
		let boxy = top*height;
		let boxw = (right-left)*width;
		let boxh = (bottom-top)*height;
		//console.log("[DEBUG] rendering box " + boxx + " " + boxy + " " + boxw + " " + boxh);

		//this.context.clearRect(0,0,width,height);
        this.context.strokeRect(boxx, boxy, boxw, boxh);
		this.context.font = "40px Verdana";
		this.context.fillText(label + " " + (score * 100).toFixed(0) + "%", boxx, boxy + boxh);
	}

}