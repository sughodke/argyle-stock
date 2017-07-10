import datetime
import logging

import intrinio

import gdax
import pandas as pd

intrinio.client.username = "5aa358835739a7a4cf76b63193451dd3"
intrinio.client.password = "f4e816313de6afff9f9a0ddb923b8827"


def retrieve_stock_data(symbol, d1 = datetime.datetime(2003, 1, 1), d2 = datetime.datetime(2008, 1, 1)):
    """
    DEPRECATED

    Choose a time period reasonably calm (not too long ago so that we get
    high-tech firms, and before the 2008 crash)
    """
    import urllib2
    try:
        from matplotlib.finance import quotes_historical_yahoo
    except ImportError:
        from matplotlib.finance import quotes_historical_yahoo_ohlc as quotes_historical_yahoo

    try:
        return quotes_historical_yahoo(symbol, d1, d2, asobject=True)
    except urllib2.HTTPError as e:
        logging.info(
            '{} was not able to be retrieved.  Err: {}'.format(symbol, e)
        )
        return None


def correct_size(q):
    try:
        return q.shape == (1258,)
    except Exception as e:
        logging.info(
            '{} did not have enough data.  Err: {}'.format(q, e)
        )
        return False


def load_quotes(symbols):
    return filter(correct_size, map(retrieve_stock_data, symbols))


def load_data(startdate, enddate, ticker):
    """
    :return: numpy.recarray with fields: date, open, high, low, close, volume, adj_close
    """

    return intrinio.prices(ticker, start_date=startdate, end_date=enddate)


def load_crypto_data(startdate, enddate, identifier, granularity=str(60*60*24)):
    """
    Get historical stock market prices or indices.

    Returns:
        Dataset as a Pandas DataFrame
    """

    quotes = gdax.PublicClient().get_product_historic_rates(identifier, start=startdate, end=enddate,
                                                            granularity=granularity)
    df = pd.DataFrame(quotes, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    df.index = pd.to_datetime(df.time, unit='s')
    df.drop('time', axis=1, inplace=True)

    df['adj_close'] = df['close']
    # df['adj_open'] = df['open']
    return df
