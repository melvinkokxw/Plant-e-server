""" This file is to contain all the scripts to import over """
import datetime
import os
import pyrebase
import requests
import time
from io import BytesIO
from PIL import Image

tz = datetime.timezone(datetime.timedelta(hours=8)) # can add name="SGT" to change %Z from UTC+0800 to SGT

def db_setup(projectid):
	""" Setup firebase connection
		
		Returns:
		user --> user object, access userid by: user["idToken"]
		database --> Firebase data object to get/set from
	"""
	dburl = "https://" + projectid + ".firebaseio.com"
	authdomain = projectid + ".firebaseio.com"
	apikey = os.environ.get("API_KEY")
	
	config = {
		"apiKey": apikey,
		"authDomain": authdomain,
		"databaseURL": dburl,
		"storageBucket": "plant-e.appspot.com",  # TODO
		"serviceAccount": "path/to/serviceAccountCredentials.json"  # TODO
	}
	# Create a firebase object by specifying the URL of the database and its secret token.
	# The firebase object has functions put and get, that allows user to put data onto
	# the database and also retrieve data from the database.

	firebase = pyrebase.initialize_app(config)
	# auth = firebase.auth()
	# admin = auth.sign_in_with_email_and_password(email, password)

	return firebase.storage(), firebase.database()


def get_plant(db):
	""" gets plant address from database

		Variables:
		device_id_dict --> {device_id: {"ip_addr": 202.166.133.236, "user_id": 23, "plot_id": 1}, device_id: {...}, ...}
		
		Returns:
		addr_list --> [(ip_addr, user_id), (ip_addr, user_id), ...]
	"""
	device_id_dict = db.child("esp32").get().val()
	addr_list = []

	for values in device_id_dict.values():
		ip_address = values.get("ip_addr")
		user_id = values.get("user_id")
		addr = (ip_address, user_id)
		addr_list.append(addr)

	return addr_list

def get_image(addr):
	""" Sends a request over to esp32 
		
		Parameters:
		addr --> ip address of the esp32 
		
		Returns:
		image_path --> path of the image returned from the esp32 (1608_180214_234473.png)
																 <day><month>_<hour><min><sec>_<microseconds>
	"""
	for i in range(5):
		result = requests.get(addr, stream=True)
		if result.status_code != 200 and i == 5:
			# TODO logging
			image = Image.new("RGB", (n, m))
			break
		else:
			image = Image.open(BytesIO(result.content))
			break

	image_path = datetime.datetime.now(tz).strftime("%y%d%m_%H%M%S_%f") + ".png"
	image.save(image_path)

	return image_path


def store(db, storage, image_path, user_id):
	""" Sends image to the database """
	
	daymonthyear = datetime.datetime.strptime(image_path[:-4], "%y%d%m_%H%M%S_%f").strftime("%d%m%y")

	storage.child("images/" + image_path).put(image_path)
	img_url = storage.child("images/" + image_path).get_url()
	db.child("journals").child(user_id).child(daymonthyear).child("image_url").set(img_url)
