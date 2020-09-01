# Plant-e-server
Server side for esp32


## Firestore architecture

- Shallow structure is so that multiple users can have a esp32 vice versa
- Easier to get all the esp32 ip_addr at once too

[Read more over here](https://firebase.google.com/docs/firestore/data-model)

```
database
	|-plot_to_users
		|-relationship_id
			|-user_id 			(fk)
			|-plot_id 			(fk)
	|-esp32
		|-device_id
			|-ip_addr        	        (esp32 public IP Address - eg. 202.166.133.236)
			|-user_id 			(fk)
			|-plot_id 			(fk)
	|-plots
		|-plot_id				(pk)
			|-light                         (to be confirmed)
			|-moisture                      (to be confirmed)
			|-last_watered                  (timestamp)
	|-users
		|-user_id				(pk)
			|-username
			|-password
			|-email
	|-journals
		|-user_id
			|-date                          (this is uncessary nesting - think of how to flattern it)
				|-yyyy-mm-dd
					|-title
					|-datetime
					|-image_url
					|-text
				|-yyyy-mm-dd
					|-title
					|-timestamp
					|-image_url
					|-text
			|-latest_image
				|-image_url
	|-log
		|-date
```
