import string
import webbrowser
import requests
import spotipy
import time
import yaml
from ebaysdk.finding import Connection as Finding
from ebaysdk.trading import Connection
from serial import Serial

class CD_to_Spotify_and_EBay:
    def __init__(self, filepath):
        # Get EBay and PayPal User Authentication Information
        with open(filepath) as file:
            information = yaml.load(file, Loader=yaml.FullLoader)
            self.ser = Serial(information['otherInfo']['com_port'])
            self.country = information['otherInfo']['country']
            self.location = information['otherInfo']['location']
            self.site = information['otherInfo']['site']
            self.conditionID = information['otherInfo']['conditionID']
            self.PayPalEmailAddress = information['otherInfo']['PayPalEmailAddress']
            self.description = information['otherInfo']['description']
            self.currency = information['otherInfo']['currency']
            self.price_multiplier = information['api.ebay.com']['pricemultiplier']
            self.appid = information['api.ebay.com']['appid']
            self.user_id = information['spotifyInfo']['user_id']
            self.client_id = information['spotifyInfo']['client_id']
            self.client_secret = information['spotifyInfo']['client_secret']
            self.playlist_uri = information['spotifyInfo']['playlist_uri']

        # Create variables for request session and list of CD prices,
        # set Spotify API scopes, and Spotify redirect URI
        allPrices = []
        scope = 'playlist-modify-private'
        redirect_uri = 'http://localhost:8888/callback'
        # Authenticate User on Spotify
        self.accessToken = spotipy.util.prompt_for_user_token(
            username=self.user_id,
            scope=scope,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=redirect_uri
        )
        self.package = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.accessToken,
        }


    # Returns CD titles for searching on Spotify
    # and listing on eBay
    def format_titles(self, title):
        removables = [
            'vinyl', 'lp', 'remastered', 'cd', 'dvd',
            'mono', 'stereo', '(ost)', 'digipak',
            'music', 'sdtk', 'original', 'soundtrack'
        ]
        # Remove unnecessary characters from
        # Spotify search and eBay Listing title
        title = title.replace("&", "and")
        for i in ['(used)', '(new)', 'Anderson', 'Merchandisers']:
            title = title.replace(i, '')
        ebayTitle = title
        title = title.lower().replace("/", " ")
        title = title.translate(
            str.maketrans('', '', string.punctuation)
        )
        title = title.replace("  ", " ")
        title = ''.join(
            [i for i in title if not i.isdigit()]
        )
        for i in removables:
            title = title.replace(i, '')

        # URL encode Spotify title
        title = title.replace(" ", "%20")
        spotifyTitle = title
        return ebayTitle.strip(), spotifyTitle.strip()


    def get_CD_title_from_UPC(self, upc):
        # Set time of start for adding CD to playlist
        s = requests.session()
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
                self.format_titles(i['title'])[0]
                for i in upcLookupResults['items'][0]['offers']
            ]
            titleList = list(set(titleList))
            titleList.sort(key=len)
            titleList.reverse()

            # Get only the first three titles
            if len(titleList) >= 3:
                titleList = titleList[0:3]

            # Print possible CD titles for user
            for index, i in enumerate(titleList):
                print(index + 1, ":", i)

            # Ask user which CD title is best
            if len(titleList) > 0:
                print()
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


    def search_spotify_by_CD_title(self, title):
        s = requests.session()
        # Get correct formatting for Spotify search
        global spotifyTitle
        spotifyTitle = self.format_titles(title)[1]

        # URL for Spotify Search
        spotifySearchUrl = (
                "https://api.spotify.com/v1/search?q=" +
                spotifyTitle +
                "&type=track"
        )

        # Search Spotify for CD
        spotifySearchResults = s.get(
            spotifySearchUrl,
            headers=self.package
        ).json()
        return spotifySearchResults


    def add_CD_to_playlist(self, spotifySearchResults):
        s = requests.session()
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
                headers = self.package
            ).json()['items']

            trackslist = ",".join([i['uri'] for i in tracks])

            # Add all tracks to user-specified playlist URI
            if addTrackBool == "" or addTrackBool == "y":
                addTracks = s.post(
                    playlistBaseUrl +
                    self.playlist_uri +
                    "/tracks?uris=" +
                    trackslist,
                    headers=self.package
                )
                print('Successfully added to Spotify Playlist')
                return spotifyImage

            # Ask to open Spotify search in browser if
            # user does not want to add track due to
            # incorrect search result
            else:
                print('Ok. Going to next CD.')
                look = input("Look on Spotify to add manually? (Enter or n): ")
                if look == 'y' or look == "":
                    webbrowser.get().open(baseopen)
                print()
                return -1


        # Ask to open Spotify Search in browser if
        # no Spotify Search results returned
        else:
            print('No tracks found. Going to next CD.')
            look = input("Look on Spotify to add manually? (Enter or n): ")
            if look == 'y' or look == "":
                webbrowser.get().open(baseopen)
            print()
            return -1


    # Calculates the price to list the CD on item for on eBay
    def calculate_listing_price(self, upc):
        # Find eBay Search Results for UPC
        priceData = []
        api = Finding(
            siteid = 'EBAY-US',
            appid = self.appid,
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
                    productPrice += 2.89  # Standard cost of USPS Media Mail

                priceData.append(productPrice)

        # Get Average Listing Price of Item and multiply by user-specified multiplier
        salePrice = ((
                sum(priceData) /
                len(priceData)) *
                self.price_multiplier
        )
        salePrice = round(salePrice, 2)
        self.allPrices.append(salePrice)
        return salePrice


    def post_on_ebay(self, title, spotifyImage):
        # Configure EBay Trading Api
        global ebayTitle
        ebayTitle = self.format_titles(title)[0]

        # Get eBay listing price
        price = self.calculate_listing_price(upc)

        # Proceed to add the CD to Spotify
        # if eBay pricing data was found
        if price == -1:
            print('No Pricing Data Found. Going to next CD.\n')
            return -1

        api = Connection(
            config_file="information.yml",
            domain="api.ebay.com",
            debug=False
        )
        request = {
            "Item": {
                "Title": ebayTitle,
                "Country": self.country,
                "Location": self.location,
                "Site": self.site,
                "ConditionID": self.conditionID,
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": self.PayPalEmailAddress,
                "PrimaryCategory": {"CategoryID": "176984"},
                "Description": self.description,
                "StartPrice": self.price,
                "ListingDuration": "GTC",
                "Currency": self.currency,
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


    def run(self):
        while True:
            # Reset CD information after each batch of CDs
            global upc
            upc = ''
            temp = ''
            allPrices = []
            barcodes = []

            # Loop to retrieve all CD Barcodes
            print("Please Scan CD Barcodes (scan the last CD twice to begin transfer to Spotify and listing on eBay)")
            while True:
                upc = self.ser.read(12).decode("utf-8")
                if temp == upc:
                    break
                temp = upc
                barcodes.append(upc)
                print('Barcode Scanned Successfully')
            print()

            # Use retrieved barcodes to add CD tracks to Spotify
            # and list the CD on eBay
            for upc in barcodes:
                title = self.get_CD_title_from_UPC(upc)
                if title != -1:
                    spotifySearchResults = self.search_spotify_by_CD_title(title)
                    spotifyImage = self.add_CD_to_playlist(spotifySearchResults)
                    if spotifyImage != -1:
                        self.post_on_ebay(title, spotifyImage)

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

if __name__ == "__main__":
    cd = CD_to_Spotify_and_EBay('information.yml')
    cd.run()
