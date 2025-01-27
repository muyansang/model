import a2 as nf

class company():
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start = start_date
        self.end = end_date
        try:
            self.sentiment = nf.get_data(ticker, start_date, end_date)
        except ValueError:
            self.sentiment = 0
        print (self.sentiment)


    def get_ticker(self):
        return self.ticker
    
    def get_start_date(self):
        return self.start
    
    def get_end_date(self):
        return self.end
    
    def get_score(self):
        return self.sentiment
    
