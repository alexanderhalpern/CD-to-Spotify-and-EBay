# CD to Spotify and EBay

CDs have become quite antiquated in recent years, and you might still have some lying around the house. Instead of just throwing them out, why not transfer the songs on them to your everyday Spotify playlist so you can hold on to your old songs and memories. You can also make a little money by listing them on eBay. 

CD-to-Spotify-and-EBay is a Python utility which interfaces with standard barcode scanners (such as Zebra scanners); users scan the barcodes of many CDs consecutively and the program automatically adds the contents of those CDs to a requested Spotify Playlist and lists the scanned CDs on eBay for the average listing price of the CD. 

## Spotify Authorization Setup


Go to [Spotify Dashboard](https://developer.spotify.com/dashboard/applications) to Create a Spotify Application of any name.

Go to Settings and set Redirect URI to:
http://localhost:8888/callback

![Spotify Auth](https://media.giphy.com/media/dNW3FEWCy0h8dZHLKW/giphy.gif)

Create a copy of information.yaml found [here](https://github.com/alexanderhalpern/CD-to-Spotify-and-EBay/blob/main/information.yml) (or just edit the file if cloning the repository) and input your Spotify username, your client_id and client_secret from the application you created (gif above shows where this information is), as well as the URI of the playlist you would like to add the contents of the CD to:
```yaml
# Spotify Authorization Information
spotifyInfo:
    user_id: INSERT_SPOTIFY_USERNAME
    client_id: INSERT_SPOTIFY_CLIENT_ID
    client_secret: INSERT_SPOTIFY_CLIENT_SECRET
    playlist_uri: INSERT_SPOTIFY_PLAYLIST_URI
```

## EBay Authorization Setup
With an eBay Developer account create application keys for a **Production Application** [here](https://developer.ebay.com/my/keys).

<img src="https://user-images.githubusercontent.com/67870720/114329569-b0525d00-9b0d-11eb-85d8-3336bdc23588.png" width="400">

Connect your developer account to your eBay seller account by retrieving a Production User Token (by clicking on user tokens on application keys page) and signing into your Seller Account.

Insert the eBay appid, certid, devid, token (from application keys you created) and pricemultiplier (percent of average listing price to list item for Example: .85 for 85 percent) into information.yaml:

```yaml
# EBay Authorization information (See GitHub)
api.ebay.com:
    compatability: 719 #No Need to Change
    appid: INSERT_EBAY_APP_ID
    certid: INSERT_EBAY_CERT_ID
    devid:  INSERT_EBAY_DEV_ID
    token: INSERT_EBAY_TOKEN
    pricemultiplier: INSERT_PRICE_MULTIPLIER
```

## Final Setup
Finally, make sure to fill out the rest of the information in the information.yaml which provides the serial port of the scanner and information for posting the CD on eBay:

```yaml
otherInfo:
    country: INSERT_COUNTRY #Example: US
    location: INSERT_LOCATION #Example: NY
    site: INSERT_SITE #Example: US
    conditionID: INSERT_CONDITION_ID #See eBay docs
    PayPalEmailAddress: INSERT_PAYPAL_EMAIL
    description: INSERT_EBAY_DESCRIPTION
    currency: INSERT_CURRENCY_TYPE
    com_port: INSERT_COM_PORT
```
## Usage
First pip install the package: 
```bash
pip3 install CD_to_Spotify_and_EBay
```
Then use the package in python like this:
```python
from CD_to_Spotify_and_EBay import BarcodeScanner
cd = BarcodeScanner(PATH_TO_INFORMATION.YML)
cd.run()
```
OR

Clone this repository, connect your barcode scanner, cd into the repository, and run:

```bash
sudo pip3 install -r requirements.txt
```

then

```bash
python3 main.py
```

For both, scan a batch of barcodes back to back and scan the final barcode twice to initiate transfer to Spotify and posting on eBay.

## License
[MIT](https://choosealicense.com/licenses/mit/)
