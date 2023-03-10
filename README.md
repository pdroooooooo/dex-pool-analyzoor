# CEX - DEX Arb Analytics Functions

## Overview

Followin the data analytics tool to explore arbitrage opportunities between a liquid Centrilized Exchange (CEX) and a less-liquid cross-chain Decentralized Exchage (DEX), the functions in this repository allow for API connection to the Exchange servers and, in a well-written infinite loop, serve to build simulations and profitable trades.

Buit for the Ironhack DA FT Jan23 Mx Bootcamp.

### Objective

Provide the necessary tools to analyze for price differencials between a liquid Centrilized Exchange (CEX) and a less-liquid cross-chain Decentralized Exchage (DEX) and to generate connections to their corresponding servers.

#### Data Sources

The source for the functions in this project need come from:

Binance API endpoints: https://binance-docs.github.io/apidocs/spot/en/#filters
Midgard (THORChain) API endpoints: https://midgard.ninerealms.com/v2/doc
The amazing Binance API Python wrapper used: https://python-binance.readthedocs.io/en/latest/account.html?highlight=create_order#id2

#### Results

These functions need to be input into a well-written infinite loop to run continually. Speed matters, so optimization is recommended.

#### Other notes

1. Trello board can be found here: https://trello.com/invite/b/AMd8fMKZ/ATTI8c3cbb08570b5439c5d424d175892b1254E7AE5F/pgboard
2. Inspiration from the bot found here: https://gitlab.com/thorchain/trade-bots/asgard-bot/-/blob/master/bot.py
