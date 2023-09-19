# pycam2web

This is a simple Flask web application that streams video from your webcam. It allows you to switch between available cameras if you have multiple connected.

## How to Use

### Installation

1. Make sure you have Python installed on your system.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

### Running the Application

Use the following command to start the application:

```bash
python app.py --port 7000
```

By default, the application runs on port 7000. You can specify a different port using the --port argument.

### Accessing the Stream

To view the home page, go to http://localhost:7000.
From the home page, you can switch between available cameras and change the resolution.

To directly access the stream, go to http://localhost:7000/mjpeg.
To access a jpg snapshot, go to http://localhost:7000/jpg.