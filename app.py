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
cap = None

def generate_mjpeg():
    while True:
        ret, frame = cap.read()

        # Encode the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Yield the frame in the response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/mjpeg')
def mjpeg_feed():
    if cap is None:
        return Response(open('static/nocameraselected.jpg', 'rb').read(), mimetype='image/jpeg')
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

def get_jpg_frame():
    ret, frame = cap.read()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

@app.route('/jpg')
def jpg_frame():
    if cap is None:
        return Response(open('static/nocameraselected.jpg', 'rb').read(), mimetype='image/jpeg')
    return Response(get_jpg_frame(), mimetype='image/jpeg')

def get_available_cameras() :
    devices = FilterGraph().get_input_devices()

    available_cameras = {}

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name

    return available_cameras

@app.route('/', methods=['GET', 'POST'])
def camera_page():
    if request.method == 'POST':
        global cap
        cap.release()
        camera = int(request.form['selected_camera'])
        resX = request.form['resX']
        resY = request.form['resY']
        
        change_camera(camera, resX, resY)
   
        #save camera to config file
        with open('config.json', 'r') as f:
            config = json.load(f)
        config['camera'] = camera
        config['resX'] = int(resX)
        config['resY'] = int(resY)
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        return redirect("/")
        
    if request.method == 'GET':
        cameras = get_available_cameras()
        #load camera from config file
        with open('config.json', 'r') as f:
            config = json.load(f)
        selected_camera = config['camera']
        resX = config['resX']
        resY = config['resY']
        
        return render_template('camera.html', cameras=cameras, selected_camera=selected_camera, resX=resX, resY=resY)
    
def change_camera(camera, resX, resY):
    global cap
    if cap is not None:
        cap.release()
    
    cameras = get_available_cameras()
    if camera not in cameras:
        print('Camera does not exist!')
        return
    
    cap = cv2.VideoCapture(camera)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(resX))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(resY))
    

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
             
    change_camera(config['camera'], config['resX'], config['resY'])
    
    app.run(debug=False, port=args.port)
