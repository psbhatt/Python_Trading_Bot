import webbrowser
import logging
import configparser
from rauth import OAuth1Service
from accounts.accounts import Accounts
from logging.handlers import RotatingFileHandler

# loading configuration file
config = configparser.ConfigParser()
config.read("C:/Users/psbha/OneDrive - University of Kentucky/TradingBot/configu.ini")


def oauth():
    """Allows user authorization for the sample application with OAuth 1"""

    etrade = OAuth1Service(
        name="etrade",
        consumer_key=config["DEF"]["consumer_key"],
        consumer_secret=config["DEF"]["consumer_secret"],
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url="https://api.etrade.com")

    menu_items = {"1": "Sandbox Consumer Key",
                  "2": "Live Consumer Key",
                  "3": "Exit"}
    while True:
        print("")
        options = menu_items.keys()
        for entry in options:
            print(entry + ")\t" + menu_items[entry])
        selection = input("Please select Consumer Key Type: ")
        if selection == "1":
            base_url = config["DEF"]["sandbox_base_url"]
            break
        elif selection == "2":
            base_url = config["DEF"]["prod_base_url"]
            break
        elif selection == "3":
            break
        else:
            print("Unknown Option Selected!")
    print("")

    # Step 1: Get OAuth 1 request token and secret
    request_token, request_token_secret = etrade.get_request_token(
        params={"oauth_callback": "oob", "format": "json"})

    # Step 2: Go through the authentication flow. Login to E*TRADE.
    # After you log in, the page will provide a text code to enter.
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    webbrowser.open(authorize_url)
    text_code = input("Please accept agreement and enter text code from browser: ")

    # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
    session = etrade.get_auth_session(request_token,
                                      request_token_secret,
                                      params={"oauth_verifier": text_code})

    # main_menu(session, base_url)
    accounts = Accounts(session, base_url)
    accounts.account_list()


# def main_menu(session, base_url):
#     """
#     Provides the different options for the sample application: Market Quotes, Account List
#
#     :param session: authenticated session
#     """
#
#     menu_items = {"1": "Market Quotes",
#                   "2": "Account List",
#                   "3": "Exit"}
#
#     while True:
#         print("")
#         options = menu_items.keys()
#         for entry in options:
#             print(entry + ")\t" + menu_items[entry])
#         selection = input("Please select an option: ")
#         if selection == "1":
#             market = Market(session, base_url)
#             market.quotes()
#         elif selection == "2":
#             accounts = Accounts(session, base_url)
#             accounts.account_list()
#         elif selection == "3":
#             break
#         else:
#             print("Unknown Option Selected!")


if __name__ == "__main__":
    oauth()
