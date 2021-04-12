# CDSpotifyConverter

CDSpotifyConverter is a Python Application for scanning CD Barcodes, posting the contents of scanned CDs on Spotify, and listing the CDs on eBay.

## Setup Spotify Authorization


Go to [Spotify Dashboard](https://developer.spotify.com/dashboard/applications) to Create a Spotify Application of any name

Go to Settings and set Redirect URI to:
http://localhost:8888/callback

![Spotify Auth](https://media.giphy.com/media/dNW3FEWCy0h8dZHLKW/giphy.gif)

Open information.yaml and input your authorization information (Video Above shows where it is)
```yaml
# Spotify Authorization Information
spotifyInfo:
    user_id: INSERT_SPOTIFY_USERNAME
    client_id: INSERT_SPOTIFY_CLIENT_ID
    client_secret: INSERT_SPOTIFY_CLIENT_SECRET
    playlist_uri: INSERT_SPOTIFY_PLAYLIST_URI
```
## Setup eBay Authorization
Go to eBay Developer Website and Follow Instructions [Here](https://developer.ebay.com/DevZone/building-blocks/eBB_Join.pdf) to create a **Production** application.

<img src="https://user-images.githubusercontent.com/67870720/114329569-b0525d00-9b0d-11eb-85d8-3336bdc23588.png" width="400">

Make sure to connect this account to your eBay seller account by retrieving a Production User Token (by clicking on the button in the photo shown above) and signing into the Seller Account.

Insert Other Information (shown above) into information.yaml
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
Finally Make Sure to fill out the rest of the information in information.yaml (especially COM (Windows) or serial (OSX or Linux) port of scanner).

```yaml
otherInfo:
    country: INSERT_COUNTRY
    location: INSERT_LOCATION #Example: NY
    site: INSERT_SITE #Example: US
    conditionID: INSERT_CONDITION_ID
    PayPalEmailAddress: INSERT_PAYPAL_EMAIL
    description: INSERT_EBAY_DESCRIPTION
    currency: INSERT_CURRENCY_TYPE
    com_port: INSERT_COM_PORT
```
## Use
Save information.yaml, connect your barcode scanner, then cd into the repository, and run:

```bash
sudo pip3 install -r requirements.txt
```

then

```bash
python3 main.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
