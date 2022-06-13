import configparser
import json
import logging
import pickle
from logging.handlers import RotatingFileHandler

# loading configuration file
config = configparser.ConfigParser()
config.read("C:/Users/psbha/OneDrive - University of Kentucky/TradingBot/configu.ini")

# logger settings
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("python_client.log", maxBytes=5 * 1024 * 1024, backupCount=3)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
logger.addHandler(handler)


class Market:

    def __init__(self, session, account, base_url):
        self.session = session
        self.account = account
        self.base_url = base_url

    def quotes(self):
        """
        Calls quotes API to provide quote details for equities, options, and mutual funds

        :param self: Passes authenticated session in parameter
        """
        # symbols = input("\nPlease enter Stock Symbol: ")
        symbols = "TSLA"
        # URL for the API endpoint
        url = self.base_url + "/v1/market/quote/" + symbols + ".json"

        # Make API call for GET request
        response = self.session.get(url)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:

            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))

            # Handle and parse response
            print("")
            data = response.json()
            if data is not None and "QuoteResponse" in data and "QuoteData" in data["QuoteResponse"]:
                for quote in data["QuoteResponse"]["QuoteData"]:
                    if quote is not None and "dateTime" in quote:
                        print("Date Time: " + quote["dateTime"])
                    if quote is not None and "Product" in quote and "symbol" in quote["Product"]:
                        print("Symbol: " + quote["Product"]["symbol"])
                    if quote is not None and "Product" in quote and "securityType" in quote["Product"]:
                        print("Security Type: " + quote["Product"]["securityType"])
                    if quote is not None and "All" in quote and "lastTrade" in quote["All"]:
                        print("Last Price: " + str(quote["All"]["lastTrade"]))
                    if quote is not None and "All" in quote and "changeClose" in quote["All"] \
                            and "changeClosePercentage" in quote["All"]:
                        print("Today's Change: " + str('{:,.3f}'.format(quote["All"]["changeClose"])) + " (" +
                              str(quote["All"]["changeClosePercentage"]) + "%)")
                    if quote is not None and "All" in quote and "open" in quote["All"]:
                        print("Open: " + str('{:,.2f}'.format(quote["All"]["open"])))
                    if quote is not None and "All" in quote and "previousClose" in quote["All"]:
                        print("Previous Close: " + str('{:,.2f}'.format(quote["All"]["previousClose"])))
                    if quote is not None and "All" in quote and "bid" in quote["All"] and "bidSize" in quote["All"]:
                        print("Bid (Size): " + str('{:,.2f}'.format(quote["All"]["bid"])) + "x" + str(
                            quote["All"]["bidSize"]))
                    if quote is not None and "All" in quote and "ask" in quote["All"] and "askSize" in quote["All"]:
                        print("Ask (Size): " + str('{:,.2f}'.format(quote["All"]["ask"])) + "x" + str(
                            quote["All"]["askSize"]))
                    if quote is not None and "All" in quote and "low" in quote["All"] and "high" in quote["All"]:
                        print("Day's Range: " + str(quote["All"]["low"]) + "-" + str(quote["All"]["high"]))
                    if quote is not None and "All" in quote and "totalVolume" in quote["All"]:
                        print("Volume: " + str('{:,}'.format(quote["All"]["totalVolume"])))
            else:
                # Handle errors
                if data is not None and 'QuoteResponse' in data and 'Messages' in data["QuoteResponse"] \
                        and 'Message' in data["QuoteResponse"]["Messages"] \
                        and data["QuoteResponse"]["Messages"]["Message"] is not None:
                    for error_message in data["QuoteResponse"]["Messages"]["Message"]:
                        print("Error: " + error_message["description"])
                else:
                    print("Error: Quote API service error")
        else:
            logger.debug("Response Body: %s", response)
            print("Error: Quote API service error")

    def preview_order(self, req, clientId, limitprice, orderaction):

        """
        Call preview order API based on selecting from different given options
        :param self: Pass in authenticated session and information on selected account
        """

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/orders/preview.json"

        # Add parameters and header information
        headers = {"Content-Type": "application/xml", "consumerKey": config["DEFAULT"]["CONSUMER_KEY"]}
        # Make API call for POST request
        response = self.session.post(url, header_auth=True, headers=headers, data=req)
        logger.debug("Request Header: %s", response.request.headers)
        logger.debug("Request payload: %s", req)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            print("\nPreview Order:")

            if data is not None and "PreviewOrderResponse" in data and "PreviewIds" in data["PreviewOrderResponse"]:
                for previewids in data["PreviewOrderResponse"]["PreviewIds"]:
                    print(previewids["previewId"])
                    self.place_order(clientId, previewids["previewId"], limitprice, orderaction)
            else:
                # Handle errors
                data = response.json()
                if 'Error' in data and 'message' in data["Error"] and data["Error"]["message"] is not None:
                    print("Error: " + data["Error"]["message"])
                else:
                    print("Error: Preview Order API service error")

            if data is not None and "PreviewOrderResponse" in data and "Order" in data["PreviewOrderResponse"]:
                for orders in data["PreviewOrderResponse"]["Order"]:

                    if orders is not None and "Instrument" in orders:
                        for instrument in orders["Instrument"]:
                            if instrument is not None and "orderAction" in instrument:
                                print("Action: " + instrument["orderAction"])
                            if instrument is not None and "quantity" in instrument:
                                print("Quantity: " + str(instrument["quantity"]))
                            if instrument is not None and "Product" in instrument \
                                    and "symbol" in instrument["Product"]:
                                print("Symbol: " + instrument["Product"]["symbol"])
                            if instrument is not None and "symbolDescription" in instrument:
                                print("Description: " + str(instrument["symbolDescription"]))

                if orders is not None and "priceType" in orders and "limitPrice" in orders:
                    print("Price Type: " + orders["priceType"])
                    if orders["priceType"] == "MARKET":
                        print("Price: MKT")
                    else:
                        print("Price: " + str(orders["limitPrice"]))
                if orders is not None and "orderTerm" in orders:
                    print("Duration: " + orders["orderTerm"])
                if orders is not None and "estimatedCommission" in orders:
                    print("Estimated Commission: " + str(orders["estimatedCommission"]))
                if orders is not None and "estimatedTotalAmount" in orders:
                    print("Estimated Total Cost: " + str(orders["estimatedTotalAmount"]))
            else:
                # Handle errors
                data = response.json()
                if 'Error' in data and 'message' in data["Error"] and data["Error"]["message"] is not None:
                    print("Error: " + data["Error"]["message"])
                else:
                    print("Error: Preview Order API service error")
        else:
            # Handle errors
            data = response.json()
            if 'Error' in data and 'message' in data["Error"] and data["Error"]["message"] is not None:
                print("Error: " + data["Error"]["message"])
            else:
                print("Error: Preview Order API service error")

    def place_order(self, clientId, previewIds, limitprice, orderaction):

        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/orders/place.json"

        # Add parameters and header information
        headers = {"Content-Type": "application/xml", "consumerKey": config["DEFAULT"]["CONSUMER_KEY"]}

        # Add payload for POST Request
        payload = """<PlaceOrderRequest>
                       <orderType>EQ</orderType>
                       <clientOrderId>{0}</clientOrderId>
                       <Order>
                           <allOrNone>false</allOrNone>
                           <priceType>LIMIT</priceType>
                           <orderTerm>GOOD_FOR_DAY</orderTerm>
                           <marketSession>REGULAR</marketSession>
                           <stopPrice></stopPrice>
                           <limitPrice>{1}</limitPrice>
                           <Instrument>
                               <Product>
                                   <securityType>EQ</securityType>
                                   <symbol></symbol>
                               </Product>
                               <orderAction>{3}</orderAction>
                               <quantityType>QUANTITY</quantityType>
                               <quantity>1</quantity>
                           </Instrument>
                       </Order>
                       <PreviewIds>
                        <previewId>{2}</previewId>
                       </PreviewIds>
                   </PlaceOrderRequest>"""
        payload = payload.format(clientId, limitprice, previewIds, orderaction)
        response = self.session.post(url, header_auth=True, headers=headers, data=payload)
        logger.debug("Request Header: %s", response.request.headers)
        logger.debug("Request payload: %s", payload)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
        else:
            # Handle errors
            data = response.json()
            if 'Error' in data and 'message' in data["Error"] and data["Error"]["message"] is not None:
                print("Error: " + data["Error"]["message"])
            else:
                print("Error: Place Order API service error")






