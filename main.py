import string
import webbrowser
import requests
import spotipy
import time
import yaml
from ebaysdk.finding import Connection as Finding
from ebaysdk.trading import Connection
from serial import Serial



# Get EBay and PayPal User Authentication Information
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

# Create variables for request session and list of CD prices, 
# set Spotify API scopes, and Spotify redirect URI
s = requests.session()
allPrices = []
scope = 'playlist-modify-private'
redirect_uri = 'http://localhost:8888/callback'

# Authenticate User on Spotify
accessToken = spotipy.util.prompt_for_user_token(
    username = user_id,
    scope = scope,
    client_id = client_id,
    client_secret = client_secret,
    redirect_uri = redirect_uri
)

package = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + accessToken,
}

# Returns CD titles for searching on Spotify
# and listing on eBay
def format_titles(title):
    removables = [
        'vinyl', 'lp', 'remastered', 'cd', 'dvd',
        'mono', 'stereo', '(ost)', 'digipak',
        'music', 'sdtk', 'original', 'soundtrack'
    ]
    # Remove unnecessary characters from
    # Spotify search and eBay Listing title
    spotifyTitle = spotifyTitle.replace("&", "and")
    for i in ['(used)', '(new)', 'Anderson', 'Merchandisers']:
        spotifyTitle = spotifyTitle.replace(i, '')
    ebayTitle = spotifyTitle
    spotifyTitle = spotifyTitle.lower().replace("/", " ")
    spotifyTitle = spotifyTitle.translate(
        str.maketrans('', '', string.punctuation)
    )
    spotifyTitle = spotifyTitle.replace("  ", " ")
    spotifyTitle = ''.join(
        [i for i in spotifyTitle if not i.isdigit()]
    )
    for i in removables:
        spotifyTitle = spotifyTitle.replace(i, '')
    
    # URL encode Spotify title
    spotifyTitle = spotifyTitle.replace(" ", "%20")
    return ebayTitle.strip(), spotifyTitle.strip()

def get_CD_title_from_UPC(upc):
    # Set time of start for adding CD to playlist
    # and listing on eBay
    global start_time
    start_time = time.time()

    # Get UPC information from upcitemdb
    upcLookupURL = "https://api.upcitemdb.com/prod/trial/lookup?upc=" + upc
    upcLookupResults = s.get(upcLookupURL).json()

    if upcLookupResults['code'] == 'OK':
        # Format returned UPC Titles and arrange from
        # greatest length to least
        titleList = [
            format_titles(i['title'])[0]
            for i in upcLookupResults['items'][0]['offers']
        ]
        titleList = list(set(titleList))
        titleList.sort(key = len)
        titleList.reverse()
        
        # Get only the first three titles
        if len(titleList) >= 3:
            titleList = titleList[0:3]
        
        # Print possible CD titles for user
        for index, i in enumerate(titleList):
            print(index + 1, ":", i)
        print()
        
        # Ask user which CD title is best
        if len(titleList) > 0:
            choice = input(
                'Enter the number of the most accurate '
                 'search term (Or Enter for 1): '
            )
            if choice == "":
                choice = 1
            else:
                choice = int(choice)
            print()
            
            # Return CD Title
            return titleList[choice - 1]

        else:
            print("Failed to Find Title of CD")
    
    # Instruct User to use a VPN if they have run 
    # out of UPC database requests
    elif upcLookupResults['code'] != 'EXCEED_LIMIT':
        print('UPC Barcode Limit Reached. Use VPN to get more requests.')
    else:
        print("Failed to Find UPC Information")
        
    return -1

def search_spotify_by_CD_title(title):    
    # Get correct formatting for Spotify search
    spotifyTitle = format_titles(title)[1]

    # URL for Spotify Search
    spotifySearchUrl = (
        "https://api.spotify.com/v1/search?q=" + 
        spotifyTitle + 
        "&type=track"
    )
    
    #Search Spotify for CD
    spotifySearchResults = s.get(
        spotifySearchUrl, 
        headers = package
    ).json()
    return spotifySearchResults

def add_CD_to_playlist(spotifySearchResults):
    # Set request URLs
    baseopen = "https://open.spotify.com/search/" + spotifyTitle
    playlistBaseUrl = "https://api.spotify.com/v1/playlists/"
    albumsBaseUrl = "https://api.spotify.com/v1/albums/"
    
    # Integer of how many results were returned
    # from Spotify search
    resultsReturned = spotifySearchResults['tracks']['total']
    
    if resultsReturned != 0:
        # Organized returned album information
        albumData = spotifySearchResults['tracks']['items'][0]['album']
        spotifyImage = albumData['images'][0]['url']
        albumId = albumData['id']

        addTrackBool = input(
            "Add " + 
            albumData['name'] + 
            ' by ' +
            albumData['artists'][0]['name'] +
            " to Spotify and eBay? (Enter or n): "
        )
        
        # Get all tracks from album
        tracks = s.get(
            albumsBaseUrl +
            albumId + 
            "/tracks",
            headers = package
        ).json()['items']
        
        trackslist = ",".join([i['uri'] for i in tracks])

        # Add all tracks to user-specified playlist URI
        if addTrackBool == "" or addTrackBool == "y":
            addTracks = s.post(
                playlistBaseUrl + 
                playlist_uri +
                "/tracks?uris=" + 
                trackslist, 
                headers = package
            )
            print('Successfully added to Spotify Playlist')
            return spotifyImage
        
        # Ask to open Spotify search in browser if
        # user does not want to add track due to 
        # incorrect search result
        else:
            print('Ok. Going to next CD.\n')
            look = input("Look on Spotify anyway? (Enter or n): ")
            if look == 'y' or look == "":
                webbrowser.get().open(baseopen)
            return -1
            print()
            
    # Ask to open Spotify Search in browser if
    # no Spotify Search results returned
    else:
        print('No tracks found. Going to next CD.\n')
        look = input("Look on Spotify anyway? (Enter or n): ")
        if look == 'y' or look == "":
            webbrowser.get().open(baseopen)
        return -1


# Calculates the price to list the CD on item for on eBay
def calculate_listing_price():
    # Find eBay Search Results for UPC
    priceData = []
    api = Finding(
        siteid = 'EBAY-US',
        appid = appid,
        config_file = None,
        domain = "svcs.ebay.com",
        debug = False
    )
    
    priceRequest = api.execute(
        'findItemsAdvanced',
        {'keywords': upc}
    ).dict()
    
    results_count = int(
        priceRequest['searchResult']['_count']
    )
    
    # Get price info or return -1 if no eBay Search Results found
    if results_count != 0:
        priceInfo = priceRequest['searchResult']['item']
    else:
        return -1
    
    # Create list of base price + shipping price for listings on eBay
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
                productPrice += 2.89 # Standard cost of USPS Media Mail

            priceData.append(productPrice)

    # Get Average Listing Price of Item and multiply by user-specified multiplier
    salePrice = (
        sum(priceData) / 
        len(priceData)) * 
        price_multiplier
    )
    salePrice = round(salePrice, 2)
    allPrices.append(salePrice)
    return salePrice


def post_on_ebay(title, spotifyImage):
    # Configure EBay Trading Api
    ebayTitle = format_titles(title)[0]
    
    # Get eBay listing price 
    price = calculateListingPrice()
    
    # Proceed to add the CD to Spotify
    # if eBay pricing data was found 
    if price == -1:
        print('No Pricing Data Found. Going to next CD.\n')
        return -1
    
    api = Connection(
        config_file = "information.yml", 
        domain = "api.ebay.com", 
        debug = False
    )
    request = {
        "Item": {
            "Title": ebayTitle,
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
    
    # Add image to listing request if image found on Spotify
    if spotifyImage != "":
        request['Item']["PictureDetails"] = {"PictureURL": spotifyImage}

    # Request to add listing to EBay
    try:
        result = api.execute("AddFixedPriceItem", request)
        print('eBay Listing Added Successfully for $', price, "\n")

    except Exception as e:
        print('Failed To List Because:', e, "\nGoing to Next CD.")
    
    # Print total time it took to add songs to Spotify
    # and list CD on eBay
    end_time = time.time()
    print('Time to Post:', round((end_time - start_time), 2), '\n')

if __name__ == "__main__":
    while True:
        # Reset CD information after each batch of CDs
        global upc
        allPrices = []
        barcodes = []
        upc = ''
        temp = ''
        
        # Loop to retrieve all CD Barcodes
        print("Please Scan the Barcodes (scan the last CD twice to begin transfer to Spotify and listing on eBay)")
        while True:
            upc = ser.read(12).decode("utf-8")
            if temp == upc:
                break
            temp = upc
            barcodes.append(upc)
            print('Barcode Scanned Successfully')
        print()
        
        # Use retrieved barcodes to add CD tracks to Spotify
        # and list the CD on eBay
        for upc in barcodes:
            title = get_CD_title_from_UPC(upc)
            if title != -1:
                spotifySearchResults = search_spotify_by_CD_title(title)
            spotifyImage = add_CD_to_playlist(spotifySearchResults)
            if spotifyImage != -1:
                post_on_ebay(title, spotifyImage)

        # Print the average listing price of the CDs
        # if any price information was found
        try:
            print(
              "Average CD Listing Price is:",
              round(sum(allPrices) / len(allPrices), 2), 
              '\n'
            )
        except:
            continue
