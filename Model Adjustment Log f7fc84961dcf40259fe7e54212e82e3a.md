# Model Adjustment Log

To run the model test, please run `main.py`

- Initial cash: 10000
- Percentages:
    - 50 for Versions 1.0s
    - Depends on (a parameter based on sentiment score) for version 2.0s

```python
Total Tickers Processed: ...
Number of Positive Value Differences: The gain using the strategy
Number of Negative Value Differences: The loss using the strategy
Average Difference in Cash: Avg difference in cash compared to original/prev method
Average Difference in Value: Avg difference in value compared to original/prev method
Average Gain (Positive Differences): Average return
Average Loss (Negative Differences): Average Loss
```

# Adjustment Version 1.0

### **1. Dynamic Parameter Adjustment: `weight_short` and `weight_long`**

- Adjusts the moving average periods dynamically based on a sentiment `score` associated with the company.
- **`weight_short`**: Computes the short-period weight as `15 + (12.5 × score)`.
- **`weight_long`**: Computes the long-period weight as 1**00+(50 × score)**.
    
    100+(50×score)100 + (50 * score)
    

The reason for this strategy is to measure that if a firm has more positive news we can may take a bit more risk on selling and buying because it’s overall positive so we are looking at a long time period. Shorter time frame logic vise versa.

## Method

```python
# ———————————————————— 1. Method Section ——————————————————————
class MovingAverageCrossoverStrategy(bt.Strategy):

    params = (
        ('short', 15),
        ('long', 30),
    )
       
    def __init__(self):
        # Create moving average indicators
        self.short_ma = btind.SimpleMovingAverage(self.data, period=self.params.short)
        self.long_ma = btind.SimpleMovingAverage(self.data, period=self.params.long)
        self.crossover = btind.CrossOver(self.short_ma, self.long_ma) 
        print(f"Short period: {self.params.short}, Long period: {self.params.long}")

    def next(self):
        # Buy In Condition
        if self.crossover > 0 and not self.position:
            self.buy()
        
        # Selling Condition
        elif self.crossover < 0 and self.position:
            self.sell()

# ———————————————————— 2. Param weighter ——————————————————————

def weight_short(score):
    return int(15 + (12.5 * score))

def weight_long(score):
    return int(100 + (50 * score))

# ———————————————————— 3. Section Runner ——————————————————————
a = cp.company("A", "2015-01-01", "2025-01-01")

def run(test, company, cash, percentage):

    assert type(company) == type(a)

    # Fetch data
    data = yf.download(company.get_ticker(),
                       start = company.get_start_date(), 
                       end = company.get_end_date())
    data.columns = [col[0] for col in data.columns]

    # Convert data to Backtrader feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Set up Backtrader
    cerebro = bt.Cerebro()
    score = company.get_score()
    if test:
        cerebro.addstrategy(MovingAverageCrossoverStrategy,
                        long = weight_long(score),
                        short = weight_short(score))
    else:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)

    cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage)
    cerebro.adddata(data_feed)

    # Running & Plotting Backtesting
    cerebro.broker.setcash(cash)
    cerebro.run()
    
    cash = cerebro.broker.get_cash()  
    value = cerebro.broker.get_value()  

    return (cash, value)

# ———————————————————— 4. Client end script ——————————————————————

a = cp.company("GOOGL", "2020-01-01", "2025-01-01")
run(True, a, 10000, 100)
```

## Result

```python
   Ticker      Old Cash     Old Value      New Cash     New Value     Diff Cash   Diff Value Is Diff Value Positive
0     MMM  10593.742473  10593.742473  10761.369956  10761.369956    167.627482   167.627482                   True
1     AOS  11509.554447  11509.554447   9428.904471   9428.904471  -2080.649976 -2080.649976                  False
2     ABT  10481.209990  10481.209990   4790.119404   9811.463781  -5691.090587  -669.746209                  False
3    ABBV   6271.290474  12607.835470  11146.576787  11146.576787   4875.286314 -1461.258683                  False
4     ACN   6236.534246  12297.673093   4608.475253   9581.027537  -1628.058993 -2716.645556                  False
5    ADBE   8806.904560   8806.904560   9448.319518   9448.319518    641.414958   641.414958                   True
6     AMD  12954.479980  12954.479980  12839.311013  12839.311013   -115.168967  -115.168967                  False
7     AES  13006.904263  13006.904263  10443.318227  10443.318227  -2563.586037 -2563.586037                  False
8     AFL  11329.929820  11329.929820  14401.189856  14401.189856   3071.260036  3071.260036                   True
9       A   6177.281110  11960.862028   9583.321755   9583.321755   3406.040645 -2377.540273                  False
10    APD   9069.429903   9069.429903   4662.376887  10011.322965  -4407.053016   941.893062                   True
11   ABNB   8726.101588   8726.101588   4134.327577   8122.377340  -4591.774010  -603.724248                  False
12   AKAM   4454.358312   8679.042675   7595.121552   7595.121552   3140.763239 -1083.921124                  False
13    ALB  12372.028363  12372.028363   6371.074983  12250.835253  -6000.953380  -121.193111                  False
14    ARE   9206.153088   9206.153088   8510.827185   8510.827185   -695.325903  -695.325903                  False
15   ALGN  20351.973288  20351.973288  14291.931464  14291.931464  -6060.041824 -6060.041824                  False
16   ALLE   9034.006105   9034.006105  10357.478336  10357.478336   1323.472231  1323.472231                   True
17    LNT   8950.859952   8950.859952   4151.099095   9140.801837  -4799.760857   189.941885                   True
18    ALL  12164.807854  12164.807854   6886.914485  14538.455582  -5277.893369  2373.647728                   True
19  GOOGL   5536.329294  11147.653611   7216.824344  14779.503204   1680.495050  3631.849593                   True
20   GOOG   5840.366238  11744.128733   7183.086982  14684.725119   1342.720744  2940.596386                   True
21     MO  10154.680626  10154.680626   4831.648336  11434.489497  -5323.032291  1279.808871                   True
22   AMZN   7434.565972  16158.728174   4327.012982   9216.044809  -3107.552990 -6942.683365                  False
23   AMCR  10666.536206  10666.536206   8966.346345   8966.346345  -1700.189861 -1700.189861                  False
24    AEE   9974.915328   9974.915328   4127.477850   9066.571505  -5847.437478  -908.343824                  False
25    AEP   9652.885959   9652.885959   9436.436281   9436.436281   -216.449677  -216.449677                  False
26    AXP   6541.980457  14150.609404   5026.625374  14223.235918  -1515.355084    72.626514                   True
27    AIG  16500.277740  16500.277740  12297.359939  12297.359939  -4202.917801 -4202.917801                  False
28    AMT   8637.288280   8637.288280   8020.453342   8020.453342   -616.834938  -616.834938                  False
29    AWK   8506.292677   8506.292677   8383.942089   8383.942089   -122.350588  -122.350588                  False
30    AMP  17906.833094  17906.833094   5554.883519  12129.002170 -12351.949575 -5777.830924                  False
31    AME  14358.576370  14358.576370   5050.701348  10429.790739  -9307.875022 -3928.785631                  False
32   AMGN  10296.401227  10296.401227  10361.390984  10361.390984     64.989757    64.989757                   True
33    APH  13809.862060  13809.862060   5938.119724  12063.007211  -7871.742337 -1746.854849                  False
34    ADI   8948.145091   8948.145091  11332.065602  11332.065602   2383.920512  2383.920512                   True
35   ANSS   8732.415323   8732.415323   4002.286863   8112.028830  -4730.128460  -620.386493                  False
36    AON  12089.292532  12089.292532   4249.639983   8901.317343  -7839.652549 -3187.975188                  False
37    APA  16992.634461  16992.634461  10018.930375  10018.930375  -6973.704086 -6973.704086                  False
38    APO   7109.727870  17960.951705   6542.755839  15172.058326   -566.972031 -2788.893379                  False
39   AAPL   7837.041864  16035.863978   5113.233781  11861.661127  -2723.808083 -4174.202850                  False
40   AMAT   9484.623318   9484.623318  18000.191171  18000.191171   8515.567853  8515.567853                   True
41   APTV   5927.747689  11994.936326   6583.380954   6583.380954    655.633265 -5411.555372                  False
42   ACGL  13379.338375  13379.338375  15591.367605  15591.367605   2212.029230  2212.029230                   True
43    ADM  12926.187581  12926.187581  13103.744074  13103.744074    177.556493   177.556493                   True
44   ANET   8948.708890  18107.049470   5842.185365  21064.644371  -3106.523525  2957.594901                   True
45    AJG  16850.086864  16850.086864  15790.756628  15790.756628  -1059.330236 -1059.330236                  False
46    AIZ  13811.719367  13811.719367   6928.715833  14974.171272  -6883.003535  1162.451905                   True
47      T  10310.865957  10310.865957   4824.154935  11416.463206  -5486.711022  1105.597250                   True
48    ATO  10201.648018  10201.648018   4338.525482   9671.770388  -5863.122536  -529.877630                  False
49   ADSK   9243.019530   9243.019530   3698.396798   8136.082668  -5544.622733 -1106.936862                  False
```

### Summary Statistics

```python
Total Tickers Processed: 50
Number of Positive Value Differences: 19
Number of Negative Value Differences: 31
Average Difference in Cash: -2264.28
Average Difference in Value: -747.02
Average Gain (Positive Differences): 1853.36
Average Loss (Negative Differences): -2340.80
```

## Analysis

### Performance Analysis of Adjustment Version 1.0

### **Summary of Results**

1. **Total Tickers Processed**: 50
2. **Positive Value Differences**: 19 (38%)
3. **Negative Value Differences**: 31 (62%)
4. **Average Difference in Cash**: **2264.28**
5. **Average Difference in Value**: **747.02**
6. **Average Gain (Positive Value Differences)**: **1853.36**
7. **Average Loss (Negative Value Differences)**: **2340.80**

---

### **Strengths of the Strategy**

1. **Positive Gains**:
    - For the 19 tickers with positive value differences, the average gain is **1853.36**, which indicates the strategy can deliver significant returns when it works well.
    - Some tickers, such as **AMAT** and **GOOGL**, show very high positive value differences (+8515.57 and +3631.85, respectively).
        
        +8515.57+8515.57
        
        +3631.85+3631.85
        
2. **Potential for High Returns**:
    - The strategy is capable of capturing substantial value gains in favorable market conditions, as evidenced by outliers with large positive value differences.

# Adjustment Version 1.1

### **1. Param Weighter Adjustments**

The calculation for determining the short and long moving average periods now includes:

- **Smoothing of Sentiment Score**: The sentiment score is smoothed using the `tanh()` function to normalize it within a range of -1 to 1. This ensures stability and prevents extreme weights.
- **Dynamic Constraints**: Both `weight_short()` and `weight_long()` functions now include:
    - **Base**: Minimum value for the moving average periods (`base`).
    - **Factor**: Determines how much the sentiment score affects the weight (`factor`).
    - **Cap and Floor**: Constrains the moving average periods to a defined range (`cap` and `floor`).

### Impact:

- This ensures that the moving average periods are dynamically adapted to sentiment scores without resulting in unreasonably high or low values, providing better control and more stable strategy behavior.

## Method

```python
# ———————————————————— 1. Method Section ——————————————————————
class MovingAverageCrossoverStrategy(bt.Strategy):

    params = (
        ('short', 15),
        ('long', 30),
    )
       
    def __init__(self):
        # Create moving average indicators
        self.short_ma = btind.SimpleMovingAverage(self.data, period=self.params.short)
        self.long_ma = btind.SimpleMovingAverage(self.data, period=self.params.long)
        self.crossover = btind.CrossOver(self.short_ma, self.long_ma) 
        print(f"Short period: {self.params.short}, Long period: {self.params.long}")

    def next(self):
        # Buy In Condition
        if self.crossover > 0 and not self.position:
            self.buy()
        
        # Selling Condition
        elif self.crossover < 0 and self.position:
            self.sell()

# ———————————————————— 2. Param weighter ——————————————————————

import math

def weight_short(score, base=15, factor=12.5, cap=50, floor=5):
    """
    Calculate the short moving average weight, dynamically adjusted based on sentiment score.
    - score: Sentiment score (-1.0 ~ 1.0)
    - base: Minimum base value
    - factor: Dynamic weight factor
    - cap: Maximum weight limit
    - floor: Minimum weight limit
    """
    adjusted_score = math.tanh(score)  # Smooth the sentiment score (-1.0 ~ 1.0)
    weight = base + (factor * adjusted_score)
    return max(floor, min(int(weight), cap))  # Constrain the value between floor and cap

def weight_long(score, base=100, factor=50, cap=300, floor=50):
    """
    Calculate the long moving average weight, dynamically adjusted based on sentiment score.
    - score: Sentiment score (-1.0 ~ 1.0)
    - base: Minimum base value
    - factor: Dynamic weight factor
    - cap: Maximum weight limit
    - floor: Minimum weight limit
    """
    adjusted_score = math.tanh(score)  # Smooth the sentiment score (-1.0 ~ 1.0)
    weight = base + (factor * adjusted_score)
    return max(floor, min(int(weight), cap))  # Constrain the value between floor and cap

# ———————————————————— 3. Section Runner ——————————————————————
a = cp.company("A", "2015-01-01", "2025-01-01")

def run(test, company, cash, percentage):

    assert type(company) == type(a)

    # Fetch data
    data = yf.download(company.get_ticker(),
                       start = company.get_start_date(), 
                       end = company.get_end_date())
    data.columns = [col[0] for col in data.columns]

    # Convert data to Backtrader feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Set up Backtrader
    cerebro = bt.Cerebro()
    score = company.get_score()
    if test:
        cerebro.addstrategy(MovingAverageCrossoverStrategy,
                        long = weight_long(score),
                        short = weight_short(score))
    else:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)

    cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage)
    cerebro.adddata(data_feed)

    # Running & Plotting Backtesting
    cerebro.broker.setcash(cash)
    cerebro.run()
    
    cash = cerebro.broker.get_cash()  
    value = cerebro.broker.get_value()  

    return (cash, value)

# ———————————————————— 4. Client end script ——————————————————————

a = cp.company("GOOGL", "2020-01-01", "2025-01-01")

run(True, a, 10000, 100)
```

### Result

```python
   Ticker      Old Cash     Old Value      New Cash     New Value     Diff Cash   Diff Value Is Diff Value Positive
0     MMM  10593.741829  10593.741829  10761.371003  10761.371003    167.629174   167.629174                   True
1     AOS  11509.551997  11509.551997   9428.905352   9428.905352  -2080.646645 -2080.646645                  False
2     ABT  10481.214385  10481.214385   4790.118650   9811.462238  -5691.095735  -669.752147                  False
3    ABBV   6271.294239  12607.843040  11405.884719  11405.884719   5134.590480 -1201.958321                  False
4     ACN   6236.535056  12297.674689   4608.475823   9581.028722  -1628.059233 -2716.645967                  False
5    ADBE   8806.904560   8806.904560   9448.319518   9448.319518    641.414958   641.414958                   True
6     AMD  12954.479980  12954.479980  12839.311013  12839.311013   -115.168967  -115.168967                  False
7     AES  13006.900853  13006.900853  10443.315245  10443.315245  -2563.585607 -2563.585607                  False
8     AFL  11329.939130  11329.939130  14401.185250  14401.185250   3071.246120  3071.246120                   True
9       A   6177.281527  11960.862835   9583.320831   9583.320831   3406.039304 -2377.542004                  False
10    APD   9069.428326   9069.428326   4662.379399  10011.328359  -4407.048927   941.900033                   True
11   ABNB   8726.101588   8726.101588   4168.284520   8189.089785  -4557.817068  -537.011803                  False
12   AKAM   4454.358312   8679.042675   7595.121552   7595.121552   3140.763239 -1083.921124                  False
13    ALB  12372.035793  12372.035793   6371.074686  12250.834682  -6000.961106  -121.201111                  False
14    ARE   9206.152400   9206.152400   8510.826109   8510.826109   -695.326291  -695.326291                  False
15   ALGN  20351.973288  20351.973288  14291.931464  14291.931464  -6060.041824 -6060.041824                  False
16   ALLE   9034.009456   9034.009456  10357.477828  10357.477828   1323.468373  1323.468373                   True
17    LNT   8950.858634   8950.858634   4151.098722   9140.800242  -4799.759912   189.941608                   True
18    ALL  12164.807955  12164.807955   6886.914210  14538.455002  -5277.893745  2373.647047                   True
19  GOOGL   5536.329092  11147.653204   7216.824695  14779.503923   1680.495603  3631.850720                   True
20   GOOG   5840.367148  11744.130563   7183.086047  14684.723208   1342.718899  2940.592644                   True
21     MO  10154.673726  10154.673726   4831.648359  11434.490869  -5323.025367  1279.817143                   True
22   AMZN   7434.565972  16158.728174   4327.012982   9216.044809  -3107.552990 -6942.683365                  False
23   AMCR  10666.529308  10666.529308   8966.346623   8966.346623  -1700.182685 -1700.182685                  False
24    AEE   9974.912566   9974.912566   4127.478419   9066.572754  -5847.434148  -908.339812                  False
25    AEP   9652.883440   9652.883440   9436.431033   9436.431033   -216.452406  -216.452406                  False
26    AXP   6541.976657  14150.602086   5026.626487  14223.238212  -1515.350170    72.636126                   True
27    AIG  16500.275441  16500.275441  12297.361741  12297.361741  -4202.913701 -4202.913701                  False
28    AMT   8637.284190   8637.284190   8020.453978   8020.453978   -616.830213  -616.830213                  False
29    AWK   8506.296834   8506.296834   8383.940443   8383.940443   -122.356392  -122.356392                  False
30    AMP  17906.838893  17906.838893   5554.882664  12129.000303 -12351.956229 -5777.838590                  False
31    AME  14358.573758  14358.573758   5050.699590  10429.787107  -9307.874169 -3928.786651                  False
32   AMGN  10296.404740  10296.404740  10361.391952  10361.391952     64.987212    64.987212                   True
33    APH  13809.864540  13809.864540   5938.117577  12063.002851  -7871.746963 -1746.861689                  False
34    ADI   8948.149952   8948.149952  11332.069646  11332.069646   2383.919694  2383.919694                   True
35   ANSS   8732.415323   8732.415323   4002.286863   8112.028830  -4730.128460  -620.386493                  False
36    AON  12089.286832  12089.286832   4249.639619   8901.316582  -7839.647213 -3187.970251                  False
37    APA  16992.642481  16992.642481  10018.928662  10018.928662  -6973.713819 -6973.713819                  False
38    APO   7109.725118  17960.944753   6542.755639  15172.057863   -566.969479 -2788.886890                  False
39   AAPL   7837.040585  16035.861360   5113.234194  11861.662626  -2723.806391 -4174.198734                  False
40   AMAT   9484.625614   9484.625614  18000.191117  18000.191117   8515.565503  8515.565503                   True
41   APTV   5927.747689  11994.936326   6583.380954   6583.380954    655.633265 -5411.555372                  False
42   ACGL  13379.338375  13379.338375  15784.482111  15784.482111   2405.143736  2405.143736                   True
43    ADM  12926.186595  12926.186595  13103.745884  13103.745884    177.559289   177.559289                   True
44   ANET   8948.708890  18107.049470   5842.185365  21064.644371  -3106.523525  2957.594901                   True
45    AJG  16850.083548  16850.083548  15790.755997  15790.755997  -1059.327551 -1059.327551                  False
46    AIZ  13811.721372  13811.721372   6928.716213  14974.172093  -6883.005159  1162.450722                   True
47      T  10310.855624  10310.855624   4824.154273  11416.463167  -5486.701352  1105.607543                   True
48    ATO  10201.648883  10201.648883   4364.967884   9730.717798  -5836.680999  -470.931085                  False
49   ADSK   9243.019530   9243.019530   3698.396798   8136.082668  -5544.622733 -1106.936862                  False
```

### Summary Statistics

```python
Summary Statistics:
Total Tickers Processed: 50
Number of Positive Value Differences: 19
Number of Negative Value Differences: 31
Average Difference in Cash: -2254.02
Average Difference in Value: -735.46
Average Gain (Positive Differences): 1863.53
Average Loss (Negative Differences): -2328.39
```

## Comments

**Comparison Analysis: Current vs. Previous Results**

| Metric | Current Results | Previous Results | Difference |
| --- | --- | --- | --- |
| **Total Tickers Processed** | 50 | 50 | No Change |
| **Positive Value Differences** | 19 | 19 | No Change |
| **Negative Value Differences** | 31 | 31 | No Change |
| **Average Difference in Cash** | -2254.02 | -2264.28 | +10.26 |
| **Average Difference in Value** | -735.46 | -747.02 | +11.56 |
| **Average Gain** | 1863.53 | 1853.36 | +10.17 |
| **Average Loss** | -2328.39 | -2340.80 | +12.41 |

## Adjustment Version 1.2

**Modified Weighting Functions**:

- The `weight_short` and `weight_long` functions now use different base values and scaling factors:
    - **`weight_short`:** Changed from `15 + (12.5 * score)` with caps/floors to a simpler scaling system.
    - **`weight_long`:** Changed from `100 + (50 * score)` (original cap: 300) to `80 + (50 * score)`.

### Method

```python
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import datetime
import yfinance as yf
import pandas as pd
import matplotlib
import company as cp

# ———————————————————— 1. Method Section ——————————————————————
class MovingAverageCrossoverStrategy(bt.Strategy):

    params = (
        ('short', 15),
        ('long', 30),
    )
       
    def __init__(self):
        # Create moving average indicators
        self.short_ma = btind.SimpleMovingAverage(self.data, period=self.params.short)
        self.long_ma = btind.SimpleMovingAverage(self.data, period=self.params.long)
        self.crossover = btind.CrossOver(self.short_ma, self.long_ma) 
        print(f"Short period: {self.params.short}, Long period: {self.params.long}")

    def next(self):
        # Buy In Condition
        if self.crossover > 0 and not self.position:
            self.buy()
        
        # Selling Condition
        elif self.crossover < 0 and self.position:
            self.sell()

# ———————————————————— 2. Param weighter ——————————————————————

def weight_short(score):
    return int(15 + (12.5 * score))

def weight_long(score):
    return int(80 + (50 * score))

# ———————————————————— 3. Section Runner ——————————————————————
a = cp.company("A", "2015-01-01", "2025-01-01")

def run(test, company, cash, percentage):

    assert type(company) == type(a)

    # Fetch data
    data = yf.download(company.get_ticker(),
                       start = company.get_start_date(), 
                       end = company.get_end_date())
    data.columns = [col[0] for col in data.columns]

    # Convert data to Backtrader feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Set up Backtrader
    cerebro = bt.Cerebro()
    score = company.get_score()
    if test:
        cerebro.addstrategy(MovingAverageCrossoverStrategy,
                        long = weight_long(score),
                        short = weight_short(score))
    else:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)

    cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage)
    cerebro.adddata(data_feed)

    # Running & Plotting Backtesting
    cerebro.broker.setcash(cash)
    cerebro.run()
    
    cash = cerebro.broker.get_cash()  
    value = cerebro.broker.get_value()  

    return (cash, value)

# ———————————————————— 4. Client end script ——————————————————————

a = cp.company("GOOGL", "2020-01-01", "2025-01-01")
run(True, a, 10000, 100)
```

### Result

```python
   Ticker      Old Cash     Old Value      New Cash     New Value     Diff Cash   Diff Value Is Diff Value Positive
0     MMM  10593.739792  10593.739792  10933.186752  10933.186752    339.446960   339.446960                   True
1     AOS  11509.557888  11509.557888  11723.711605  11723.711605    214.153718   214.153718                   True
2     ABT  10481.210571  10481.210571   9928.410238   9928.410238   -552.800333  -552.800333                  False
3    ABBV   6271.294859  12607.844287  11669.235772  11669.235772   5397.940912  -938.608515                  False
4     ACN   6236.535610  12297.675783   5705.823365  11789.565355   -530.712246  -508.110427                  False
5    ADBE   8806.904560   8806.904560   9055.187264   9055.187264    248.282705   248.282705                   True
6     AMD  12954.479980  12954.479980  12373.598058  12373.598058   -580.881922  -580.881922                  False
7     AES  13006.905049  13006.905049  11778.641818  11778.641818  -1228.263231 -1228.263231                  False
8     AFL  11329.933309  11329.933309  14466.350994  14466.350994   3136.417685  3136.417685                   True
9       A   6177.281446  11960.862679  13380.711456  13380.711456   7203.430010  1419.848777                   True
10    APD   9069.428538   9069.428538  10266.968729  10266.968729   1197.540191  1197.540191                   True
11   ABNB   8726.101588   8726.101588   4069.492708   7937.085354  -4656.608880  -789.016234                  False
12   AKAM   4454.358312   8679.042675   7876.236780   7876.236780   3421.878467  -802.805896                  False
13    ALB  12372.034961  12372.034961  13015.736057  13015.736057    643.701096   643.701096                   True
14    ARE   9206.151236   9206.151236   7417.679780   7417.679780  -1788.471457 -1788.471457                  False
15   ALGN  20351.973288  20351.973288  14643.813102  14643.813102  -5708.160186 -5708.160186                  False
16   ALLE   9034.006681   9034.006681  11178.854205  11178.854205   2144.847524  2144.847524                   True
17    LNT   8950.859152   8950.859152   3984.035715   8771.011717  -4966.823436  -179.847434                  False
18    ALL  12164.809067  12164.809067   6166.154516  13467.544554  -5998.654550  1302.735487                   True
19  GOOGL   5536.329294  11147.653611   6550.512116  13761.857313   1014.182822  2614.203702                   True
20   GOOG   5840.368261  11744.132802   6899.656512  14466.736654   1059.288251  2722.603852                   True
21     MO  10154.676073  10154.676073   5102.114281  12185.380135  -5052.561792  2030.704061                   True
22   AMZN   7434.565972  16158.728174   4599.346607   9814.348005  -2835.219365 -6344.380169                  False
23   AMCR  10666.534233  10666.534233  10046.383504  10046.383504   -620.150730  -620.150730                  False
24    AEE   9974.914091   9974.914091   3878.181218   8607.745077  -6096.732873 -1367.169013                  False
25    AEP   9652.884744   9652.884744   9094.396358   9094.396358   -558.488385  -558.488385                  False
26    AXP   6541.978064  14150.604227   5630.767910  12759.739785   -911.210153 -1390.864441                  False
27    AIG  16500.266632  16500.266632  11968.459238  11968.459238  -4531.807394 -4531.807394                  False
28    AMT   8637.285296   8637.285296   8159.757249   8159.757249   -477.528047  -477.528047                  False
29    AWK   8506.295773   8506.295773   7936.759883   7936.759883   -569.535890  -569.535890                  False
30    AMP  17906.832609  17906.832609   7202.899252  15727.419012 -10703.933357 -2179.413598                  False
31    AME  14358.576468  14358.576468   6320.459355  12906.922475  -8038.117113 -1451.653993                  False
32   AMGN  10296.404906  10296.404906  11351.362809  11351.362809   1054.957903  1054.957903                   True
33    APH  13809.865076  13809.865076   6454.594475  13292.575378  -7355.270601  -517.289698                  False
34    ADI   8948.148562   8948.148562  10447.032195  10447.032195   1498.883633  1498.883633                   True
35   ANSS   8732.415323   8732.415323   4055.707721   8207.161992  -4676.707602  -525.253331                  False
36    AON  12089.293313  12089.293313  10246.378110  10246.378110  -1842.915203 -1842.915203                  False
37    APA  16992.628991  16992.628991  10377.281771  10377.281771  -6615.347221 -6615.347221                  False
38    APO   7109.722532  17960.938219   6658.794765  15584.719373   -450.927767 -2376.218846                  False
39   AAPL   7837.043032  16035.866366   6240.630602  14529.294707  -1596.412430 -1506.571659                  False
40   AMAT   9484.627859   9484.627859  14593.080825  14593.080825   5108.452966  5108.452966                   True
41   APTV   5927.747689  11994.936326   9235.876086   9235.876086   3308.128397 -2759.060240                  False
42   ACGL  13379.338375  13379.338375  15046.812417  15046.812417   1667.474042  1667.474042                   True
43    ADM  12926.184923  12926.184923  14146.729815  14146.729815   1220.544892  1220.544892                   True
44   ANET   8948.708890  18107.049470   6499.653338  15700.558291  -2449.055551 -2406.491179                  False
45    AJG  16850.088594  16850.088594  14558.252378  14558.252378  -2291.836216 -2291.836216                  False
46    AIZ  13811.727258  13811.727258   6031.669079  13659.010880  -7780.058179  -152.716377                  False
47      T  10310.860104  10310.860104   4797.204452  11341.224176  -5513.655652  1030.364073                   True
48    ATO  10201.645364  10201.645364   4641.666482  10217.458648  -5559.978881    15.813284                   True
49   ADSK   9243.019530   9243.019530   4265.876028   9395.096478  -4977.143503   152.076948                   True
```

### Summary Statistics

```python
Number of Positive Value Differences: 20
Number of Negative Value Differences: 30
Average Difference in Cash: -1552.73
Average Difference in Value: -475.97
Average Gain (Positive Differences): 1488.15
Average Loss (Negative Differences): -1785.39
```

| **Metric** | **Current Results** | **Previous Results** | **Difference (Current - Previous)** |
| --- | --- | --- | --- |
| **Total Tickers Processed** | 50 | 50 | No Change |
| **Positive Value Differences** | 20 | 19 | +1 |
| **Negative Value Differences** | 30 | 31 | -1 |
| **Average Difference in Cash** | -1552.73 | -2254.02 | +701.29 |
| **Average Difference in Value** | -475.97 | -735.46 | +259.49 |
| **Average Gain** | 1488.15 | 1863.53 | -375.38 |
| **Average Loss** | -1785.39 | -2328.39 | +543.00 |

The Model is improving but the overall difference in cash and value is still significantly negative and losing. Therefore this model will be discarded and swap to another model.

## Adjustment Version 2.0

### **Performance Insights**

- **Improvement in Investment percentage weighted by sentiment Score**

### Method

```python
# ———————————————————— 1. Method Section ——————————————————————
class MovingAverageCrossoverStrategy(bt.Strategy):

    params = (
        ('short', 15),
        ('long', 30),
    )
       
    def __init__(self):
        # Create moving average indicators
        self.short_ma = btind.SimpleMovingAverage(self.data, period=self.params.short)
        self.long_ma = btind.SimpleMovingAverage(self.data, period=self.params.long)
        self.crossover = btind.CrossOver(self.short_ma, self.long_ma) 
        print(f"Short period: {self.params.short}, Long period: {self.params.long}")

    def next(self):
        # Buy In Condition
        if self.crossover > 0 and not self.position:
            self.buy()
        
        # Selling Condition
        elif self.crossover < 0 and self.position:
            self.sell()

# ———————————————————— 2. Param weighter ——————————————————————

def weight_short(score):
    return int(30 + (12.5 * score))

def weight_long(score):
    return int(50 + (50 * score))

# ———————————————————— 3. Section Runner ——————————————————————
a = cp.company("A", "2015-01-01", "2025-01-01")

def run(test, company, cash, percentage):

    assert type(company) == type(a)

    # Fetch data
    data = yf.download(company.get_ticker(),
                       start = company.get_start_date(), 
                       end = company.get_end_date())
    data.columns = [col[0] for col in data.columns]

    # Convert data to Backtrader feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Set up Backtrader
    cerebro = bt.Cerebro()
    score = company.get_score()
    if test:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)
        cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage + 100 * (score * 2))
    else:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)
        cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage)

    cerebro.adddata(data_feed)

    # Running & Plotting Backtesting
    cerebro.broker.setcash(cash)
    cerebro.run()
    
    cash = cerebro.broker.get_cash()  
    value = cerebro.broker.get_value()  

    return (cash, value)

# ———————————————————— 4. Client end script ——————————————————————

a = cp.company("GOOGL", "2020-01-01", "2025-01-01")
run(True, a, 10000, 50)
```

### Result

```python
   Ticker      Old Cash     Old Value      New Cash     New Value    Diff Cash   Diff Value  Sentiment Better?
0     MMM  10593.735142  10593.735142  10581.997687  10581.997687   -11.737455   -11.737455   0.155270   False
1     AOS  11509.550457  11509.550457  12041.464078  12041.464078   531.913622   531.913622   0.103033    True
2     ABT  10481.212314  10481.212314  10000.000000  10000.000000  -481.212314  -481.212314   0.251644   False
3    ABBV   6271.289364  12607.833240  10000.000000  10000.000000  3728.710636 -2607.833240   0.325603   False
4     ACN   6236.535312  12297.675194   2234.766553  13862.154906 -4001.768758  1564.479712   0.170985    True
5    ADBE   8806.904560   8806.904560   7567.836448   7567.836448 -1239.068111 -1239.068111   0.196356   False
6     AMD  12954.479980  12954.479980  12954.479980  12954.479980     0.000000     0.000000   0.000000   False
7     AES  13006.901987  13006.901987  10000.000000  10000.000000 -3006.901987 -3006.901987   0.252921   False
8     AFL  11329.935844  11329.935844  12047.026101  12047.026101   717.090257   717.090257   0.188082    True
9       A   6177.285054  11960.869666   2771.316338  12988.126089 -3405.968716  1027.256424   0.148324    True
10    APD   9069.430455   9069.430455   8572.615026   8572.615026  -496.815430  -496.815430   0.116435   False
11   ABNB   8726.101588   8726.101588   7978.916031   7978.916031  -747.185557  -747.185557   0.120565   False
12   AKAM   4454.358312   8679.042675   2327.469324   8034.649427 -2126.888988  -644.393249   0.111874   False
13    ALB  12372.029401  12372.029401  12970.836348  12970.836348   598.806947   598.806947   0.110948    True
14    ARE   9206.155449   9206.155449   8514.371964   8514.371964  -691.783485  -691.783485   0.193326   False
15   ALGN  20351.973288  20351.973288  23391.797158  23391.797158  3039.823870  3039.823870   0.059494    True
16   ALLE   9034.007044   9034.007044   8567.909310   8567.909310  -466.097734  -466.097734   0.108125   False
17    LNT   8950.861872   8950.861872  10000.000000  10000.000000  1049.138128  1049.138128   0.293430    True
18    ALL  12164.805801  12164.805801  13076.932351  13076.932351   912.126550   912.126550   0.118395    True
19  GOOGL   5536.330779  11147.656601   5536.330779  11147.656601     0.000000     0.000000   0.000000   False
20   GOOG   5840.366238  11744.128733   5840.366238  11744.128733     0.000000     0.000000   0.000000   False
21     MO  10154.671165  10154.671165  10101.993606  10101.993606   -52.677559   -52.677559   0.146139   False
22   AMZN   7434.565972  16158.728174   7434.565972  16158.728174     0.000000     0.000000   0.000000   False
23   AMCR  10666.533951  10666.533951  10952.146302  10952.146302   285.612351   285.612351   0.125146    True
24    AEE   9974.913318   9974.913318   9933.419392   9933.419392   -41.493926   -41.493926   0.063298   False
25    AEP   9652.891274   9652.891274   9423.436818   9423.436818  -229.454456  -229.454456   0.121724   False
26    AXP   6541.977309  14150.603495   6541.977309  14150.603495     0.000000     0.000000   0.000000   False
27    AIG  16500.276005  16500.276005  20654.419470  20654.419470  4154.143465  4154.143465   0.123125    True
28    AMT   8637.286248   8637.286248   7690.795422   7690.795422  -946.490826  -946.490826   0.166070   False
29    AWK   8506.295667   8506.295667  10000.000000  10000.000000  1493.704333  1493.704333   0.299916    True
30    AMP  17906.831496  17906.831496  25284.426063  25284.426063  7377.594567  7377.594567   0.168603    True
31    AME  14358.572902  14358.572902  17352.033244  17352.033244  2993.460342  2993.460342   0.139619    True
32   AMGN  10296.398687  10296.398687  10321.338880  10321.338880    24.940193    24.940193   0.031886    True
33    APH  13809.871691  13809.871691  16446.540259  16446.540259  2636.668568  2636.668568   0.154652    True
34    ADI   8948.147815   8948.147815   8593.382249   8593.382249  -354.765566  -354.765566   0.070565   False
35   ANSS   8732.415323   8732.415323   7983.501452   7983.501452  -748.913871  -748.913871   0.129442   False
36    AON  12089.293849  12089.293849  12818.058929  12818.058929   728.765079   728.765079   0.083559    True
37    APA  16992.642748  16992.642748  21214.951219  21214.951219  4222.308471  4222.308471   0.141073    True
38    APO   7109.725011  17960.944482   2651.470578  24498.129877 -4458.254433  6537.185395   0.170979    True
39   AAPL   7837.041365  16035.862957   7837.041365  16035.862957     0.000000     0.000000   0.000000   False
40   AMAT   9484.628323   9484.628323   8606.112260   8606.112260  -878.516063  -878.516063   0.121001   False
41   APTV   5927.747689  11994.936326   2622.077843  12791.687030 -3305.669845   796.750705   0.146385    True
42   ACGL  13379.338375  13379.338375  15718.658572  15718.658572  2339.320197  2339.320197   0.160520    True
43    ADM  12926.185188  12926.185188  13095.595330  13095.595330   169.410142   169.410142   0.014054    True
44   ANET   8948.708890  18107.049470     73.805268  16930.862277 -8874.903622 -1176.187193   0.246633   False
45    AJG  16850.080460  16850.080460  19395.240344  19395.240344  2545.159883  2545.159883   0.070428    True
46    AIZ  13811.719506  13811.719506  17836.583065  17836.583065  4024.863559  4024.863559   0.217548    True
47      T  10310.853605  10310.853605  10280.536182  10280.536182   -30.317422   -30.317422   0.159819   False
48    ATO  10201.650949  10201.650949  10000.000000  10000.000000  -201.650949  -201.650949   0.307759   False
49   ADSK   9243.019530   9243.019530   8472.558585   8472.558585  -770.460945  -770.460945   0.158918   False
```

### Summary Statistics

```python
Number of Positive Value Differences: 23
Number of Negative Value Differences: 27
Average Difference in Cash: 120.09
Average Difference in Value: 678.93
Average Gain (Positive Differences): 2163.94
Average Loss (Negative Differences): -586.07
```

Here is the updated comparison table including the new results for clarity:

| **Metric** | **Current Results** | **Previous Results** | **Difference (Current - Previous)** |
| --- | --- | --- | --- |
| **Total Tickers Processed** | 50 | 50 | No Change |
| **Positive Value Differences** | 23 | 20 | +3 |
| **Negative Value Differences** | 27 | 30 | -3 |
| **Average Difference in Cash** | 120.09 | -1552.73 | +1672.82 |
| **Average Difference in Value** | 678.93 | -475.97 | +1154.90 |
| **Average Gain** | 2163.94 | 1488.15 | +675.79 |
| **Average Loss** | -586.07 | -1785.39 | +1199.32 |

## Adjustment Version 2.1

### Method

```python
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import datetime
import yfinance as yf
import pandas as pd
import matplotlib
import company as cp

# ———————————————————— 1. Method Section ——————————————————————
class MovingAverageCrossoverStrategy(bt.Strategy):

    params = (
        ('short', 15),
        ('long', 30),
    )
       
    def __init__(self):
        # Create moving average indicators
        self.short_ma = btind.SimpleMovingAverage(self.data, period=self.params.short)
        self.long_ma = btind.SimpleMovingAverage(self.data, period=self.params.long)
        self.crossover = btind.CrossOver(self.short_ma, self.long_ma) 
        print(f"Short period: {self.params.short}, Long period: {self.params.long}")

    def next(self):
        # Buy In Condition
        if self.crossover > 0 and not self.position:
            self.buy()
        
        # Selling Condition
        elif self.crossover < 0 and self.position:
            self.sell()

# ———————————————————— 2. Param weighter ——————————————————————

def weight_short(score):
    return int(30 + (12.5 * score))

def weight_long(score):
    return int(50 + (50 * score))

# ———————————————————— 3. Section Runner ——————————————————————
a = cp.company("A", "2015-01-01", "2025-01-01")

def run(test, company, cash, percentage):

    assert type(company) == type(a)

    # Fetch data
    data = yf.download(company.get_ticker(),
                       start = company.get_start_date(), 
                       end = company.get_end_date())
    data.columns = [col[0] for col in data.columns]

    # Convert data to Backtrader feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Set up Backtrader
    cerebro = bt.Cerebro()
    score = company.get_score()
    if test:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)
        cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage + 100 * (score * 1.8))
    else:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)
        cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage)

    cerebro.adddata(data_feed)

    # Running & Plotting Backtesting
    cerebro.broker.setcash(cash)
    cerebro.run()
    
    cash = cerebro.broker.get_cash()  
    value = cerebro.broker.get_value()  

    return (cash, value)

# ———————————————————— 4. Client end script ——————————————————————

a = cp.company("GOOGL", "2020-01-01", "2025-01-01")
run(True, a, 10000, 50)
```

### Result

```python
   Ticker      Old Cash     Old Value      New Cash     New Value    Diff Cash    Diff Value  Sentiment Better?
0     MMM  10593.736929  10593.736929  10594.401340  10594.401340     0.664411      0.664411   0.155270    True
1     AOS  11509.545550  11509.545550  11991.082875  11991.082875   481.537324    481.537324   0.103033    True
2     ABT  10481.213452  10481.213452  10710.242999  10710.242999   229.029548    229.029548   0.251644    True
3    ABBV   6271.293717  12607.841990  10000.000000  10000.000000  3728.706283  -2607.841990   0.325603   False
4     ACN   6236.533546  12297.671712   2688.562561  13707.647131 -3547.970985   1409.975418   0.170985    True
5    ADBE   8806.904560   8806.904560   7698.691285   7698.691285 -1108.213275  -1108.213275   0.196356   False
6     AMD  12954.479980  12954.479980  12954.479980  12954.479980     0.000000      0.000000   0.000000   False
7     AES  13006.906466  13006.906466  14648.142312  14648.142312  1641.235846   1641.235846   0.252921    True
8     AFL  11329.937053  11329.937053  11987.950595  11987.950595   658.013542    658.013542   0.188082    True
9       A   6177.282586  11960.864886   3148.782362  12891.429741 -3028.500223    930.564855   0.148324    True
10    APD   9069.432964   9069.432964   8623.678067   8623.678067  -445.754896   -445.754896   0.116435   False
11   ABNB   8726.101588   8726.101588   8056.373022   8056.373022  -669.728566   -669.728566   0.120565   False
12   AKAM   4454.358312   8679.042675   2528.800826   8099.999543 -1925.557486   -579.043133   0.111874   False
13    ALB  12372.035799  12372.035799  12924.291244  12924.291244   552.255445    552.255445   0.110948    True
14    ARE   9206.153393   9206.153393   8585.832948   8585.832948  -620.320444   -620.320444   0.193326   False
15   ALGN  20351.973288  20351.973288  23078.510344  23078.510344  2726.537056   2726.537056   0.059494    True
16   ALLE   9034.006822   9034.006822   8615.491156   8615.491156  -418.515666   -418.515666   0.108125   False
17    LNT   8950.853932   8950.853932  10000.000000  10000.000000  1049.146068   1049.146068   0.293430    True
18    ALL  12164.808449  12164.808449  12989.572172  12989.572172   824.763723    824.763723   0.118395    True
19  GOOGL   5536.330725  11147.656493   5536.330725  11147.656493     0.000000      0.000000   0.000000   False
20   GOOG   5840.366838  11744.129941   5840.366838  11744.129941     0.000000      0.000000   0.000000   False
21     MO  10154.675918  10154.675918  10111.819125  10111.819125   -42.856793    -42.856793   0.146139   False
22   AMZN   7434.565972  16158.728174   7434.565972  16158.728174     0.000000      0.000000   0.000000   False
23   AMCR  10666.531504  10666.531504  10925.107407  10925.107407   258.575903    258.575903   0.125146    True
24    AEE   9974.922607   9974.922607   9938.200207   9938.200207   -36.722400    -36.722400   0.063298   False
25    AEP   9652.884898   9652.884898   9448.064261   9448.064261  -204.820637   -204.820637   0.121724   False
26    AXP   6541.977303  14150.603483   6541.977303  14150.603483     0.000000      0.000000   0.000000   False
27    AIG  16500.267453  16500.267453  20208.124009  20208.124009  3707.856556   3707.856556   0.123125    True
28    AMT   8637.283221   8637.283221   7785.742635   7785.742635  -851.540586   -851.540586   0.166070   False
29    AWK   8506.300219   8506.300219  10000.000000  10000.000000  1493.699781   1493.699781   0.299916    True
30    AMP  17906.837762  17906.837762  24465.143809  24465.143809  6558.306047   6558.306047   0.168603    True
31    AME  14358.576874  14358.576874  17033.168835  17033.168835  2674.591961   2674.591961   0.139619    True
32   AMGN  10296.403714  10296.403714  10318.982599  10318.982599    22.578885     22.578885   0.031886    True
33    APH  13809.867388  13809.867388  16174.625344  16174.625344  2364.757955   2364.757955   0.154652    True
34    ADI   8948.149080   8948.149080   8629.748843   8629.748843  -318.400237   -318.400237   0.070565   False
35   ANSS   8732.415323   8732.415323   8060.059968   8060.059968  -672.355354   -672.355354   0.129442   False
36    AON  12089.294760  12089.294760  12744.584822  12744.584822   655.290061    655.290061   0.083559    True
37    APA  16992.635577  16992.635577  20794.507209  20794.507209  3801.871632   3801.871632   0.141073    True
38    APO   7109.725684  17960.946182   3185.810173  23817.790126 -3923.915511   5856.843944   0.170979    True
39   AAPL   7837.041655  16035.863550   7837.041655  16035.863550     0.000000      0.000000   0.000000   False
40   AMAT   9484.624437   9484.624437   8705.660156   8705.660156  -778.964280   -778.964280   0.121001   False
41   APTV   5927.747689  11994.936326   2973.445821  12724.595487 -2954.301868    729.659162   0.146385    True
42   ACGL  13379.338375  13379.338375  15480.190527  15480.190527  2100.852152   2100.852152   0.160520    True
43    ADM  12926.186045  12926.186045  13078.638508  13078.638508   152.452463    152.452463   0.014054    True
44   ANET   8948.708890  18107.049470   1581.017260  29862.229904 -7367.691630  11755.180434   0.246633    True
45    AJG  16850.081818  16850.081818  19126.581155  19126.581155  2276.499337   2276.499337   0.070428    True
46    AIZ  13811.718839  13811.718839  17403.818334  17403.818334  3592.099495   3592.099495   0.217548    True
47      T  10310.856264  10310.856264  10291.066634  10291.066634   -19.789630    -19.789630   0.159819   False
48    ATO  10201.643467  10201.643467  10000.000000  10000.000000  -201.643467   -201.643467   0.307759   False
49   ADSK   9243.019530   9243.019530   8557.247146   8557.247146  -685.772384   -685.772384   0.158918   False
```

### Summary Statistics

```python
Number of Positive Value Differences: 27
Number of Negative Value Differences: 23
Average Difference in Cash: 234.56
Average Difference in Value: 964.85
Average Gain (Positive Differences): 2166.85
Average Loss (Negative Differences): -446.19

Short period: 15, Long period: 30
Summary Statistics:
Total Tickers Processed: 498
Number of Positive Value Differences: 325
Number of Negative Value Differences: 173
Average Difference in Cash: 505.26
Average Difference in Value: 1105.02
Average Gain (Positive Differences): 2215.10
Average Loss (Negative Differences): -980.40
```

| **Metric** | **Current Results** | **Previous Results** | **Difference (Current - Previous)** |
| --- | --- | --- | --- |
| **Total Tickers Processed** | 50 | 50 | No Change |
| **Positive Value Differences** | 27 | 23 | +4 |
| **Negative Value Differences** | 23 | 27 | -4 |
| **Average Difference in Cash** | 234.56 | 120.09 | +114.47 |
| **Average Difference in Value** | 964.85 | 678.93 | +285.92 |
| **Average Gain** | 2166.85 | 2163.94 | +2.91 |
| **Average Loss** | -446.19 | -586.07 | -139.88 |