import asyncio
import pickle
from market.market import Market
from util.generator import randANStr

askList = []
with open("askList.pickle", "wb") as openAskList:
    pickle.dump(askList, openAskList)


class Algorithm:

    def __init__(self, session, account, base_url):
        self.session = session
        self.account = account
        self.base_url = base_url

    def start_script(self):

        loop = asyncio.get_event_loop()

        def calc_tma():
            with open("askList.pickle", "rb") as readAskList:
                cAskList = pickle.load(readAskList)

            mk = Market(self.session, self.account, self.base_url)
            ask = mk.quotes()

            cAskList.append(ask)
            with open("askList.pickle", "wb") as openCAskList:
                pickle.dump(cAskList, openCAskList)

            print(f"Ask Price: \n {ask}")

            loop.call_later(300, calc_tma)

        def createBO():
            with open("askList.pickle", "rb") as readAskList:
                bAskList = pickle.load(readAskList)

            total, count = 0, 0

            for ask in bAskList:
                total += ask
                count += 1

            mAFunc = lambda a, b: a / b
            tma = mAFunc(total, count)

            print(f"Today's Moving Average: {tma}")

            market = Market(self.session, self.base_url, self.account)
            ask = market.quotes()
            if ask < tma:
                def buy():
                    clientorderId = randANStr(20)

                    # Add payload for POST Request
                    payload = """<PreviewOrderRequest>
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
                                                                                  <orderAction>{2}</orderAction>
                                                                                  <quantityType>QUANTITY</quantityType>
                                                                                  <quantity>1</quantity>
                                                                              </Instrument>
                                                                          </Order>
                                                                      </PreviewOrderRequest>"""
                    orderaction = "BUY"
                    payload = payload.format(clientorderId, ask, orderaction)
                    market.preview_order(payload, clientorderId, ask, orderaction)

                loop.call_soon(buy)
                loop.call_later(300, createBO)

        def renew_token():
            url = self.base_url + "/oauth/renew_access_token"

            response = self.session.get(url, header_auth=True)
            print(response)
            loop.call_later(7100, renew_token)

        loop.call_soon(calc_tma)
        # loop.call_later(7200, createBO)
        # loop.call_later(7100, renew_token)
        loop.run_forever()





