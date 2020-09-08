""" This file is to contain all the scripts to import over """
import datetime
import os
import requests
import time
from io import BytesIO
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage

tz = datetime.timezone(datetime.timedelta(hours=8)) # can add name="SGT" to change %Z from UTC+0800 to SGT


def db_setup(projectid):
	""" Setup firebase connection
		
		Returns:
		user --> user object, access userid by: user["idToken"]
		database --> Firebase data object to get/set from
	"""
	
	# Can remove apikey when not needed
	apikey = os.environ.get("API_KEY")
	private = os.environ.get("PRIVATE_KEY")
	
	# Use a service account
	cred = credentials.Certificate(private)
	firebase_admin.initialize_app(cred, {'storageBucket': 'plant-e-fc09e.appspot.com'})

	return storage.bucket(), firestore.client()


def get_plant(db):
	""" gets plant address from database

		Returns:
		addr_list --> [(ip_addr, user_id), (ip_addr, user_id), ...]
	"""
	all_esp = db.collection('esp32').stream()
	addr_list = []
	for esp in all_esp:
		esp_dict = esp.to_dict()
		ip_address = esp_dict.get("ip_addr")
		user_id = esp_dict.get("user_id")
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
		if result.status_code == 200:
			# Save image
			image = Image.open(result.raw)
			break
		elif i == 4:
			# TODO logging
			image = Image.new("RGB", (n, m))

	image_path = datetime.datetime.now(tz).strftime("%y%m%d_%H%M%S_%f") + ".png"
	image.save(image_path)

	return image_path


def store(db, storage, image_path, user_id):
	""" Sends image to the database """
	
	date = datetime.datetime.strptime(image_path[:-4], "%y%m%d_%H%M%S_%f").strftime("%Y-%m-%d")

	blob = storage.blob("images/" + image_path)
	blob.upload_from_filename(image_path)
	img_url = blob.public_url

	# storage.child("images/" + image_path).put(image_path)
	# img_url = storage.child("images/" + image_path).get_url()

	journal_day = {'title': None, 'datetime': None, 'image_url': img_url, 'text': None}

	# Save img_url to firestore
	db.collection("journals").document(user_id).collection('date').document(date).set(journal_day)
