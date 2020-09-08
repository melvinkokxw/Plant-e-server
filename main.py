""" This file is the main cron script """
from dotenv import load_dotenv
import time
from scripts import *

def main():
    # Load environment variables
    load_dotenv()

    # Connect to firebase
    storage, db = db_setup("plant-e")      # change plant-e to new firebase name

    addr_list = get_plant(db)

    for addr in addr_list:
        image_path = get_image(addr[0])
        store(db, storage, image_path, addr[1])

if __name__ == "__main__":
    main()