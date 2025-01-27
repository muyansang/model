# Libraries for web scraping, parsing, and data manipulation
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
from datetime import timedelta, datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# 1. Retrieve S&P 500 company tickers from Wikipedia
def get_tickers():
    """
    Retrieve the list of S&P 500 tickers from Wikipedia.

    Returns:
        list: A list of stock ticker symbols.
    """
    wikipedia_url = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    stocks = wikipedia_url[0]
    tickers = stocks['Symbol'].tolist()
    return tickers

# 2. Fetch news data for a specific ticker
def fetch_news_table(ticker):
    """
    Fetch news data for a given ticker from the Finviz website.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        tuple: A tuple containing the ticker and the news table (BeautifulSoup object).
    """
    finviz_url = 'https://finviz.com/quote.ashx?t='
    url = finviz_url + ticker.replace(".", "-")

    for _ in range(3):  # Retry up to 3 times if there's an error
        try:
            req = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
            response = urlopen(req)
            html = BeautifulSoup(response, 'html.parser')
            news_table = html.find(id='news-table')
            return ticker, news_table
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            time.sleep(2)
            continue

    print(f"Failed to fetch data for {ticker} after 3 attempts.")
    return ticker, None

# 3. Parse news data
def parse_news_table(news_tables):
    """
    Parse the news table to extract ticker, date, time, and headline.

    Args:
        news_tables (dict): A dictionary containing tickers as keys and news tables as values.

    Returns:
        list: A list of parsed news data, each element containing [ticker, date, time, headline].
    """
    parsed_news = []
    for ticker, news_table in news_tables.items():
        if news_table is None:
            continue
        for x in news_table.findAll('tr'):
            try:
                if len(x.findAll('a')) == 0:
                    continue
                text = x.a.get_text()
                date_scrape = x.td.text.split()
                if len(date_scrape) == 1:
                    time = date_scrape[0]
                else:
                    date = date_scrape[0]
                    time = date_scrape[1]
                parsed_news.append([ticker, date, time, text])
            except Exception as e:
                print(f"Error parsing news for {ticker}: {e}")
    return parsed_news

# 4. Perform sentiment analysis
def sentiment_analysis(parsed_news):
    """
    Analyze the sentiment of the parsed news data using VADER.

    Args:
        parsed_news (list): Parsed news data.

    Returns:
        DataFrame: A DataFrame with sentiment scores for each headline.
    """
    vader = SentimentIntensityAnalyzer()
    columns = ['ticker', 'date', 'time', 'headline']
    parsed_and_scored_news = pd.DataFrame(parsed_news, columns=columns)

    # Get sentiment scores for each headline
    scores = parsed_and_scored_news['headline'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)

    # Merge the sentiment scores with the parsed news
    parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')
    parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news['date'], errors='coerce')

    return parsed_and_scored_news

# 5. Filter and calculate sentiment for a specific ticker and time period
def get_data(ticker, start_date, end_date):
    """
    Retrieve the average compound sentiment score for a specific ticker within a date range.

    Args:
        ticker (str): The stock ticker (e.g., "AAPL").
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

    Returns:
        float: The average compound sentiment score for the given ticker and date range.
    """
    # Parse the input dates
    print(f"getting data for {ticker}")
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if start_date > end_date:
        raise ValueError("Start date must be earlier than or equal to the end date.")

    # Check if ticker exists in S&P 500 list
    tickers = get_tickers()
    if ticker not in tickers:
        raise ValueError(f"Ticker '{ticker}' not found in the S&P 500 company list.")

    # Fetch news data for the ticker
    news_tables = {ticker: fetch_news_table(ticker)[1]}  # Fetch only for the given ticker
    parsed_news = parse_news_table(news_tables)

    # Perform sentiment analysis
    sentiment_data = sentiment_analysis(parsed_news)

    # 移除 NaT 值
    sentiment_data = sentiment_data.dropna(subset=['date'])

    # Filter sentiment data for the specified date range
    ticker_data = sentiment_data[
        (sentiment_data['ticker'] == ticker) &
        (sentiment_data['date'] >= pd.Timestamp(start_date)) &
        (sentiment_data['date'] <= pd.Timestamp(end_date))
    ]

    if ticker_data.empty:
        raise ValueError(f"No sentiment data available for '{ticker}' between {start_date} and {end_date}.")

    # Calculate the average compound sentiment score
    avg_compound_score = ticker_data['compound'].mean()

    return avg_compound_score
