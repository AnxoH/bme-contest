import yfinance as yf
import pandas as pd
import os

print("Starting central data download for Spanish Market (15 Years)...")

ibex35 = [
    "ANA.MC", "ANE.MC", "ACS.MC", "AENA.MC", "AMS.MC", "MTS.MC", "SAB.MC", "SAN.MC",
    "BKT.MC", "BBVA.MC", "CABK.MC", "CLNX.MC", "ENG.MC", "ELE.MC", "FER.MC", "FDR.MC",
    "GRF.MC", "IAG.MC", "IBE.MC", "ITX.MC", "LOG.MC", "MAP.MC", "MEL.MC", "MRL.MC",
    "NTGY.MC", "RED.MC", "REP.MC", "ROVI.MC", "SCYR.MC", "SLR.MC", "TEF.MC", "UNI.MC",
    "VIS.MC", "COL.MC", "PUIG.MC"
]

midcaps = [
    "ALM.MC", "CAF.MC", "CASH.MC", "CIE.MC", "DOM.MC", "ENC.MC", "FAE.MC", "GSJ.MC",
    "PHM.MC", "TLGO.MC", "TRE.MC", "TUB.MC", "VID.MC"
]

tickers = ibex35 + midcaps
# Extended Macro Universe
macro_tickers = {
    "^IBEX": "IBEX", 
    "^STOXX50E": "EUROSTOXX", 
    "^GSPC": "SP500",
    "EURBRL=X": "EURBRL",
    "EURMXN=X": "EURMXN",
    "EURUSD=X": "EURUSD",    # New: Dollar exposure
    "BZ=F": "BRENT_OIL",     # New: Brent Crude Oil
    "^TNX": "US10Y",         # US 10 Year Bond
    "ES10YT=RR": "ES10Y"     # Spanish 10 Year Bond Yield (Reuters code for YF)
}

os.makedirs("../data/raw", exist_ok=True)

# Skip stocks if they exist to save time for this test
if not os.path.exists("../data/raw/stocks_close_15y.csv"):
    print("Downloading 15 years of stock data...")
    df_stocks = yf.download(tickers, period="15y", group_by="ticker", auto_adjust=False)
    components = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    for comp in components:
        df_comp = df_stocks.xs(comp, level=1, axis=1)
        df_comp.to_csv(f"../data/raw/stocks_{comp.lower().replace(' ', '')}_15y.csv")

print("Downloading 15 years of macro data...")
df_macro = yf.download(list(macro_tickers.keys()), period="15y", auto_adjust=False)
macro_prices = df_macro['Close'].copy()
macro_prices = macro_prices.rename(columns=macro_tickers)
macro_prices.to_csv("../data/raw/macro_close_15y.csv")

print("All data successfully downloaded and saved to data/raw/ directory.")
