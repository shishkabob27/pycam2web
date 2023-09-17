import json
from flask import Flask, redirect, request, Response, render_template
import cv2
from pygrabber.dshow_graph import FilterGraph
import argparse

parser = argparse.ArgumentParser(description='Webcam streamer')
parser.add_argument('--port', type=int, default=7000, help='Port to run the server on')

args = parser.parse_args()

app = Flask(__name__)

# Initialize the webcam
cap = cv2.VideoCapture(0)

def generate_mjpeg():
    while True:
        ret, frame = cap.read()

        # Encode the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Yield the frame in the response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/')
@app.route('/mjpeg')
def mjpeg_feed():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_jpg_frame():
    ret, frame = cap.read()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

@app.route('/jpg')
def jpg_frame():
    return Response(get_jpg_frame(), mimetype='image/jpeg')

def get_available_cameras() :
    devices = FilterGraph().get_input_devices()

    available_cameras = {}

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name

    return available_cameras

@app.route('/camera', methods=['GET', 'POST'])
def change_camera():
    if request.method == 'POST':
        global cap
        cap.release()
        camera = int(request.form['selected_camera'])
        resX = request.form['resX']
        resY = request.form['resY']
        cap = cv2.VideoCapture(camera)
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(resX))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(resY))
   
        #save camera to config file
        with open('config.json', 'r') as f:
            config = json.load(f)
        config['camera'] = camera
        config['resX'] = int(resX)
        config['resY'] = int(resY)
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        return redirect("/mjpeg")
        
    if request.method == 'GET':
        cameras = get_available_cameras()
        #load camera from config file
        with open('config.json', 'r') as f:
            config = json.load(f)
        selected_camera = config['camera']
        resX = config['resX']
        resY = config['resY']
        
        return render_template('changecamera.html', cameras=cameras, selected_camera=selected_camera, resX=resX, resY=resY)

if __name__ == '__main__':
    #Create config file if not exists
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {
            'camera': 0,
            'resX': 1920,
            'resY': 1080
            }
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
             
    cap = cv2.VideoCapture(int(config['camera']))
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(config['resX']))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(config['resY']))
    
    app.run(debug=True, port=args.port)
