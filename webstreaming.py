# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
from pyimagesearch.motion_detection import SingleMotionDetector
#from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from flask_socketio import SocketIO, emit 
import sqlite3
from tensorflow.keras.models import load_model
import threading
import argparse
import datetime
#import imutils
import time
import numpy as np
import cv2
import itertools
# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
#model = load_model('cnn_model_keras_sid.h5')
model = load_model('cnn_model_keras2.h5')
x, y, w, h = 300, 100, 300, 350
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)
socketio = SocketIO(app) 

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
#vs = VideoStream(src=0).start()
vs = cv2.VideoCapture(0)
time.sleep(2.0)
t = threading.Thread()
item=""
@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html",item="item")

@app.route("/stopit")
def stopit():
	global vs, t
	vs.release();
	t.join()   
	return render_template("index.html",item="item")

@app.route("/item")
def item():
	return ''


    
@app.route("/startit")
def startit():
	global vs, t
	t = threading.Thread(target=detect_motion, args=(args["frame_count"],))
	t.daemon = True
	t.start() 
	vs = cv2.VideoCapture(0);
	return render_template("index.html",item="video_feed")

def keras_process_image(img):
	crop_img = img[y:y+h, x:x+w].astype('float32')/255.0
	img=cv2.resize(crop_img, dsize = (64,64))
	img = img.astype('float32')
	#cv2.imshow("Cropped",img)
	return img

def keras_predict(model, image):
	processed = keras_process_image(image)
	pred_probab = model.predict(np.array([processed]))[0]
	#pred_class = list(pred_probab).index(max(pred_probab))
	pred_class = np.argmax(pred_probab)
	max_probab = np.max(pred_probab)
	return max_probab,pred_class

def get_pred_text_from_db(pred_class):
	conn = sqlite3.connect("gesture_db.db")
	cmd = "SELECT g_name FROM gesture WHERE g_id="+str(pred_class)
	cursor = conn.execute(cmd)
	for row in cursor:
		return row[0]
    
def get_pred_text_from_list(pred_class) :
    #class_list=['A','B','C','D','E','F','G','H','I','J','Welcome!','NA']
    class_list=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Awesome!','Thank you!','SPACE','DEL','NOTHING']
    return class_list[pred_class]
                
def say_text(text):
	if not is_voice_on:
		return
	while engine._inLoop:
		pass
	engine.say(text)
	engine.runAndWait()

def get_pred_from_contour(img):
	pred_probab, pred_class = keras_predict(model, img)
	text = None
	if pred_probab*100 > 70:
		text = get_pred_text_from_list(pred_class)
	return text

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock, socketio

	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0
	word = ""
	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		if vs.read()[0]==False:
			vs = cv2.VideoCapture(0)
			vs.set(cv2.CAP_PROP_FPS, 30)
		frame = vs.read()[1]
		pred_text= ' '
		old_text = pred_text
		if frame.any() != None:
			frame = cv2.flip(frame, 1)
			pred_text=get_pred_from_contour(frame)
            
			blackboard = np.zeros((480, 640, 3), dtype=np.uint8)
			cv2.putText(blackboard, " ", (180, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (255, 0,0))
			if pred_text != None and pred_text != 'NOTHING':
				if old_text != pred_text and pred_text != 'Awesome!':
					word = word + pred_text   
					old_text = pred_text                    
				elif pred_text == 'Awesome!':
					word = ''.join(ch for ch, _ in itertools.groupby(word))
					cv2.putText(blackboard, word, (30, 240), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255))
					socketio.emit('message', word) 
					word=""
				cv2.putText(blackboard, "Predicted text- " + str(pred_text), (30, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 0))
			#cv2.putText(blackboard, word, (30, 240), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255))
			cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 1)
			res = np.hstack((frame, blackboard))
			with lock:
				outputFrame = res.copy()
             
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())

	# start a thread that will perform motion detection
	#t = threading.Thread(target=detect_motion, args=(
	#	args["frame_count"],))
	#t.daemon = True
	#t.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

# release the video stream pointer
cv2.destroyAllWindows()
vs.release()