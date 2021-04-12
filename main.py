import string
import webbrowser
import requests
import spotipy
import time
import yaml
from ebaysdk.finding import Connection as Finding
from ebaysdk.trading import Connection
from serial import Serial


allPrices = []
scope = 'playlist-modify-private'
# Get User Authentication Information
with open('information.yml') as file:
    information = yaml.load(file, Loader=yaml.FullLoader)
    ser = Serial(information['otherInfo']['com_port'])
    country = information['otherInfo']['country']
    location = information['otherInfo']['location']
    site = information['otherInfo']['site']
    conditionID = information['otherInfo']['conditionID']
    PayPalEmailAddress = information['otherInfo']['PayPalEmailAddress']
    description = information['otherInfo']['description']
    currency = information['otherInfo']['currency']
    price_multiplier = information['api.ebay.com']['pricemultiplier']
    appid = information['api.ebay.com']['appid']
    user_id = information['spotifyInfo']['user_id']
    client_id = information['spotifyInfo']['client_id']
    client_secret = information['spotifyInfo']['client_secret']
    playlist_uri = information['spotifyInfo']['playlist_uri']
    redirect_uri = 'http://localhost:8888/callback'

accessToken = spotipy.util.prompt_for_user_token(
    username=user_id,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri
)

package = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + accessToken,
}


def calculateSalesPrice(upc):
    priceData = []
    # Find eBay Search Results for UPC
    api = Finding(
        siteid='EBAY-US',
        appid=appid,
        config_file=None,
        domain="svcs.ebay.com",
        debug=False
    )
    priceRequest = api.execute(
        'findItemsAdvanced',
        {'keywords': upc}
    ).dict()
    results_count = int(
        priceRequest['searchResult']['_count']
    )
    if results_count != 0:
        priceInfo = priceRequest['searchResult']['item']
    else:
        return -1

    for i in range(0, results_count):
        if priceInfo[i]['listingInfo']['listingType'] == 'FixedPrice':
            productPrice = float(
                priceInfo[i]['sellingStatus']['convertedCurrentPrice']['value']
            )
            try:
                productPrice += float(
                    priceInfo[i]['shippingInfo']['shippingServiceCost']['value']
                )
            except:
                productPrice += 2.5

            priceData.append(productPrice)

    # Get Sale Price of Item
    salePrice = (sum(priceData) / len(priceData)) * price_multiplier
    salePrice = round(salePrice, 2)
    allPrices.append(salePrice)
    return salePrice


def postOnEBay(title, spotifyImage, price):
    # Configure Api
    api = Connection(config_file="information.yml", domain="api.ebay.com", debug=False)
    request = {
        "Item": {
            "Title": title,
            "Country": country,
            "Location": location,
            "Site": site,
            "ConditionID": conditionID,
            "PaymentMethods": "PayPal",
            "PayPalEmailAddress": PayPalEmailAddress,
            "PrimaryCategory": {"CategoryID": "176984"},
            "Description": description,
            "StartPrice": price,
            "ListingDuration": "GTC",
            "Currency": currency,
            "ReturnPolicy": {
                "ReturnsAcceptedOption": "ReturnsAccepted",
                "RefundOption": "MoneyBack",
                "ReturnsWithinOption": "Days_30",
                "ShippingCostPaidByOption": "Buyer"
            },
            "ShippingDetails": {
                "ShippingServiceOptions": {
                    "FreeShipping": "True",
                    "ShippingService": "USPSMedia"
                }
            },
            "DispatchTimeMax": "3"
        }
    }
    if spotifyImage != "":
        request['Item']["PictureDetails"] = {"PictureURL": spotifyImage}

    # Continue Program on Failure to Add
    try:
        result = api.execute("AddFixedPriceItem", request)
        print('eBay Listing Added Successfully for $', price, "\n")

    except Exception as e:
        print('Failed To List Because:', e, "\nGoing to Next CD.")

    end_time = time.time()
    print('Time to Post:', round((end_time - start_time), 2), '\n')


def formatTitles(spotifyTitle):
    removables = ['vinyl', 'lp', 'remastered', 'cd', 'dvd',
                  'mono', 'stereo', '(ost)', 'digipak',
                  'music', 'sdtk', 'original', 'soundtrack']

    # Prepare CD Title for Spotify Search
    spotifyTitle = spotifyTitle.replace("&", "and")
    for i in ['(used)', '(new)', 'Anderson', 'Merchandisers']:
        spotifyTitle = spotifyTitle.replace(i, '')
    ebayTitle = spotifyTitle
    spotifyTitle = spotifyTitle.lower().replace("/", " ")
    spotifyTitle = spotifyTitle.translate(str.maketrans('', '', string.punctuation))
    spotifyTitle = spotifyTitle.replace("  ", " ")

    spotifyTitle = ''.join([i for i in spotifyTitle if not i.isdigit()])

    for i in removables:
        spotifyTitle = spotifyTitle.replace(i, '')

    spotifyTitle = spotifyTitle.replace(" ", "%20")
    return ebayTitle.strip(), spotifyTitle.strip()


def addCDToSpotify(resultsReturned, ebayTitle, spotifyTitle, spotifySearch, price):
    s = requests.session()
    baseopen = "https://open.spotify.com/search/" + spotifyTitle
    if resultsReturned != 0:
        # Get Album Info
        playlistBaseUrl = "https://api.spotify.com/v1/playlists/"
        albumData = spotifySearch['tracks']['items'][0]['album']
        spotifyImage = albumData['images'][0]['url']
        albumId = albumData['id']

        addTrackBool = input("Add " + albumData['name'] + ' by ' +
            albumData['artists'][0]['name'] +
            " to Spotify and eBay? (Enter or n): "
        )

        tracks = s.get("https://api.spotify.com/v1/albums/" +
                       albumId + "/tracks",
                       headers=package
        ).json()['items']

        trackslist = ",".join([i['uri'] for i in tracks])

        # Add Tracks to Playlist URI
        if addTrackBool == "" or addTrackBool == "y":
            addTracks = s.post(playlistBaseUrl + playlist_uri +
                        "/tracks?uris=" + trackslist, headers=package
            )

            print('Successfully added to Spotify Playlist')
            postOnEBay(ebayTitle.rstrip('\n'), spotifyImage, price)

        else:
            look = input("Look on Spotify? (Enter or n): ")
            if look == 'y' or look == "":
                webbrowser.get().open(baseopen)

            print()
    else:
        print('No tracks found. Going to next CD.\n')
        look = input("Look on Spotify? (Enter or n): ")

        if look == 'y' or look == "":
            webbrowser.get().open(baseopen)


def spotifyCDSearch(spotifyTitle, upc):
    s = requests.session()

    ebayTitle, spotifyTitle = formatTitles(spotifyTitle)

    # Search Spotify by Altered Title
    spotifySearchUrl = "https://api.spotify.com/v1/search?q=" + spotifyTitle + "&type=track"
    spotifySearch = s.get(spotifySearchUrl, headers=package)

    spotifySearch = spotifySearch.json()
    resultsReturned = spotifySearch['tracks']['total']
    price = calculateSalesPrice(upc)
    if price != -1:
        addCDToSpotify(resultsReturned,
                       ebayTitle,
                       spotifyTitle,
                       spotifySearch,
                       price
        )
    else:
        print('No Pricing Data Found. Going to next CD.\n')


def scanBarupc(upc):
    global start_time
    s = requests.session()
    start_time = time.time()

    # Get UPC information from database
    upcLookupURL = "https://api.upcitemdb.com/prod/trial/lookup?upc=" + upc
    upcLookupResults = s.get(upcLookupURL).json()

    if upcLookupResults['code'] == 'OK':
        titleList = [formatTitles(i['title'])[0]
                     for i in upcLookupResults['items'][0]['offers']]
        titleList = list(set(titleList))
        titleList.sort(key=len)
        titleList.reverse()

        if len(titleList) >= 3:
            titleList = titleList[0:3]

        for index, i in enumerate(titleList):
            print(index + 1, ":", i)

        print()

        if len(titleList) > 0:
            choice = input('Enter the number of the most accurate '
                           'search term (Or Enter for 1): ')
            if choice == "":
                choice = 1
            else:
                choice = int(choice)
            print()
            spotifyCDSearch(titleList[choice - 1], upc)

        else:
            print("Failed to Find Title")

    elif upcLookupResults['code'] != 'EXCEED_LIMIT':
        print('UPC Barcode Limit Reached. Use VPN to get more requests.')

    else:
        print("Failed to Find UPC")


if __name__ == "__main__":
    while True:
        allPrices = []
        barcodes = []
        upc = ''
        temp = ''

        print("Please Scan the Barcodes (Scan the Last One Twice to Stop)")
        while True:
            upc = ser.read(12).decode("utf-8")
            if temp == upc:
                break
            temp = upc
            barcodes.append(upc)
            print('Barcode Scanned Successfully')

        print()

        for upc in barcodes:
            scanBarupc(upc)
        try:
            print("Average CD Sales Price is:",
              round(sum(allPrices) / len(allPrices), 2), '\n'
            )
        except:
            continue
