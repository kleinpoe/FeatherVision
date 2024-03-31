class Box
{
    constructor(top,left,bottom,right)
    {
        this.Top = top;
        this.Left = left;
        this.Bottom = bottom;
        this.Right = right;
    }

    toString() {return `<Box: Top:${this.Top}, Top:${this.Left}, Top:${this.Bottom}, Top:${this.Right}>`;}
}

class Detection
{
    constructor(box, score,label)
    {
        this.Box = box;
        this.Score = score;
        this.Label = label;
    }

    toString() {return `<Detection: Label:${this.Label} Score:${this.Score} Box:${this.Box}>`;}
}

class VideoOverlay{
    constructor() 
    {
        this.stream  = document.getElementById("stream");
        this.canvas = document.getElementById("canvas");
        this.context = this.canvas.getContext('2d');
        this.thickness = 1;
        this.offset = Math.floor(this.thickness/2);
    }

    render(renderGrid, renderDetections, detections)
    {
        this.prepareRender()

        if(renderGrid)
        { this.renderGrid() }
        if(renderDetections)
        {
            detections.forEach( x => this.renderDetection(x) );
        }
    }

	prepareRender()
	{
		let width = this.stream.clientWidth;
        let height = this.stream.clientHeight;
        this.canvas.width = width;
        this.canvas.height = height;
        
		this.context.clearRect(0,0,width,height);
	}

    renderGrid()
    {
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

	renderDetection(detection)
    {
		this.context.strokeStyle  = 'green';
		this.context.fillStyle = 'green';
		let width = this.stream.clientWidth;
        let height = this.stream.clientHeight;

		let boxx = detection.Box.Left*width;
		let boxy = detection.Box.Top*height;
		let boxw = (detection.Box.Right-detection.Box.Left)*width;
		let boxh = (detection.Box.Bottom-detection.Box.Top)*height;

        this.context.strokeRect(boxx, boxy, boxw, boxh);
		this.context.font = "40px Verdana";
		this.context.fillText(detection.Label + " " + (detection.Score * 100).toFixed(0) + "%", boxx, boxy + boxh);
	}

}