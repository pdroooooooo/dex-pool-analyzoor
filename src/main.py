import os
import pdb
import time
import json
import logging
import requests
import datetime
import sqlalchemy
import pandas as pd
from binance import Client # API wrapper from https://github.com/sammchardy/python-binance
from dotenv import load_dotenv, find_dotenv
from binance.exceptions import BinanceAPIException

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname).4s | %(message)s")

BNB = "BNB.BNB"
RUNE = "BNB.RUNE-B1A"
USDT = "ETH.USDT-0XDAC17F958D2EE523A2206206994597C13D831EC7"
stablecoins = ["USDC", "USDT", "BUSD"]
CACAO = "MAYA.CACAO"

def raise_for_non_bnb(coin): #Remove if not used
    if coin.asset != BNB:
        raise Exception(f"must start with BNB: got {coin}")

# Safe key management
load_dotenv(find_dotenv())
user = os.getenv("MYSQL_USER")
pwd = os.getenv("MYSQL_PWD")
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")    

## DB, Log and Misc:

# Log information to a db
def log(ex, sql = True):
    df = get_info()
    if sql:
        pandas_to_sql(df, 'arb_logs', f'mysql://{user}:{pwd}@localhost/arb_logs')
    else:
        pandas_to_json(df)
    return

def get_info():
    df = pd.DataFrame(columns = ["pool", "balance_asset", "balance_rune", "implied_asset_price", "datetime"])
    url = "https://midgard.ninerealms.com/v2/pools"
    # Request pool info
    response = requests.request("GET", url)
    pools = json.loads(response.text)
    pool_snapshot = []
    for pool in pools:
        asset = pool["asset"].split("-")[0]
        # asset depth
        balance_asset = pool["assetDepth"]
        # rune / cacao depth
        balance_rune = pool["runeDepth"]
        # implied_asset_price = 0
        implied_asset_price = pool["assetPriceUSD"]
        # snapshot datetime
        dt = datetime.datetime.now()
        pool_snapshot = [*pool_snapshot, asset, balance_asset, balance_rune, implied_asset_price, dt]
        df.loc[len(df.index)] = pool_snapshot
        pool_snapshot = []
    return df

# Send from a df to a json file
def pandas_to_json(df):
    # Serializing json
    json_obj = df.to_json(orient='records')
    # Writing to sample.json
    with open("../data/log.json", "w") as outfile:
        outfile.write(json_obj)
    return

# Send from a df to my SQL local server
def pandas_to_sql(df, table_name, conn_string):
    engine = sqlalchemy.create_engine(conn_string)
    df.to_sql(table_name, engine, if_exists='append', index=False)
    return True

# Builds useful tweet
def build_tweet(df, lang):
    if lang == "eng":
        tweet = f""" Liquidity Auction Progress Report! __ days since the start. 
                    __ days remaining. $__ notional USD total pooled like so: __ BTC, __ ETH, __ Stablecoins and __ RUNE. 
                    Our deepest pool yet  is the ____ pool. 
                    Have you earned a share of $CACAO yet? Add liquidity using @THORWalletDEX now!
                    """
    if lang == "sp":
        tweet = f""" ¡Reporte del progreso de la Subasta de Liquidez! Llevamos __ días desde el inicio. 
                    Quedan __ días para la donación de $CACAO. 
                    Se han aportado $__ de dólares nocionales de la siguiente manera: __ BTC, __ ETH, __ en Stablecoins y __ RUNE. 
                    Nuestra pool más líquida al momento es ___. ¡Participa mediante @THORWalletDEX!
                    """
    return tweet

## THORChain operation:

def quote_swap(asset_in, asset_out, amount_in, address_out):
    url = f"https://thornode.ninerealms.com/thorchain/quote/swap?amount={amount_in}&from_asset={asset_in}&to_asset={asset_out}&destination={address_out}"
    response = requests.request("GET", url)
    constants = json.loads(response.text)
    return constants

# Get network constants
def get_constants():
    """ Get constant values from the API """
    url = "https://thornode.ninerealms.com/thorchain/constants"
    response = requests.request("GET", url)
    constants = json.loads(response.text)
    return constants

# Get pool price from THORChain, using an API endpoint
def thorchain_price():
    """
    Calculates an aproximate asset price in USD using a list of USD pools.
    I think realizing this price would require trading both pools.
    """
    if ex == "Thor":
        url = "https://midgard.ninerealms.com/v2/pools"
    elif ex == "Maya":
        url = "https://stagenet.mayanode.mayachain.info/thorchain/pools" # Not implemented yet
        return False

    # Request pool info
    response = requests.request("GET", url)
    pools = json.loads(response.text)

    # Build a list of all the pools, using dictionaries / json format
    pool_info = []
    for pool in pools:
        pool_asset = pool["asset"]
        price = pool["assetPriceUSD"]
        status = pool["status"]
        apr = pool["annualPercentageRate"]
        vol_24hr = pool["volume24h"]
        pool_dict = { "pool_asset": pool_asset, "price": price, "status": status, "apr": apr, "vol_24hr": vol_24hr }
        pool_info.append(pool_dict)
    return thorchain_price

# THORChain Outbound Fees

def calc_outbound_fee(network = "BTC"):
    """ 
        https://dev.thorchain.org/thorchain-dev/concepts/fees#understanding-gas_rate
        https://docs.thorchain.org/how-it-works/fees#outbound-fee
    """
    url = "https://thornode.ninerealms.com/thorchain/inbound_addresses"
    response = requests.request("GET", url)
    chains = json.loads(response.text)

    for chain in chains:
        if chain["chain"] == network:
            return int(chain["outbound_fee"])

## Binance operation:

# Build a Binance client
client = Client(api_key, api_secret)

# Check connection
def check_status():
    try:
        client.get_account_status()
        return True
    except:
        return False

# get account trading fees (specific books might defer)
# https://www.binance.com/en/fee/schedule
def get_account_trading_fees(self):
    info_dict = client.get_account()
    return {"maker": info_dict["makerCommission"]/100, "taker": info_dict["takerCommission"]/100}

# Get price from Binance, using an API wrapper
def binance_price(ticker="BNBBTC"):
    raw = client.get_symbol_ticker(ticker)
    price = raw["price"]
    return price

# Tests
if __name__ == "__main__":
    ex = "Maya"
    sql = False

    calc_outbound_fee("BTC")

    while True:
        time.sleep(1)
        log(ex, sql)
    # 
    # thorchain_price()




    

