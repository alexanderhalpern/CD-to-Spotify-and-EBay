# CDSpotifyConverter

CDs have become quite antiquated in recent years, and you might still have some lying around the house. Instead of just throwing them out, why not transfer the songs on them to your everyday Spotify playlist, so you can hold on to your old songs and memories. You can also make a little money by listing them on eBay. CDSpotifyConverter is a Python utility which interfaces with standard barcode scanners (such as Zebra scanners), allowing users to scan the barcodes of many CDs consecutively and automatically adding the contents of those CDs to a requested Spotify Playlist and posting those CDs on eBay for the average selling price of the CD. 

## Setup Spotify Authorization


Go to [Spotify Dashboard](https://developer.spotify.com/dashboard/applications) to Create a Spotify Application of any name

Go to Settings and set Redirect URI to:
http://localhost:8888/callback

![Spotify Auth](https://media.giphy.com/media/dNW3FEWCy0h8dZHLKW/giphy.gif)

Open information.yaml and input your authorization information (gif above shows where this information is), as well as the URI of the playlist you would like to add the contents of the CD to:
```yaml
# Spotify Authorization Information
spotifyInfo:
    user_id: INSERT_SPOTIFY_USERNAME
    client_id: INSERT_SPOTIFY_CLIENT_ID
    client_secret: INSERT_SPOTIFY_CLIENT_SECRET
    playlist_uri: INSERT_SPOTIFY_PLAYLIST_URI
```
## Setup eBay Authorization
Go to eBay Developer Website and follow Instructions [here](https://developer.ebay.com/DevZone/building-blocks/eBB_Join.pdf) to create a **Production** application.

<img src="https://user-images.githubusercontent.com/67870720/114329569-b0525d00-9b0d-11eb-85d8-3336bdc23588.png" width="400">

Make sure to connect this account to your eBay seller account by retrieving a Production User Token (by clicking on the button in the photo shown above) and signing into the Seller Account.

Insert eBay Application Information (shown above) and price multiplier (percent of average selling price to list item for Example: .85 for 85 percent) into information.yaml:
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
Finally make sure to fill out the rest of the information in the information.yaml (especially the COM (Windows) or serial (OSX or Linux) port of the scanner.

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

Scan a batch of barcodes back to back. Scan the final barcode twice to initiate transfer to Spotify and posting on eBay.

## License
[MIT](https://choosealicense.com/licenses/mit/)
