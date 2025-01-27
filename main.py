import strategy
import company as cp
import a2
import pandas as pd

tickers = a2.get_tickers()

# Initialize an empty DataFrame to store results
columns = ["Ticker", "Old Cash", "Old Value", "New Cash", "New Value", "Diff Cash", "Diff Value","Sentiment", "Better?"]
results_df = pd.DataFrame(columns=columns)

for i in tickers[:50]:
    print(i)
    try:
        # Simulate cp.company and strategy.run logic
        comp = cp.company(i, "2020-01-01", "2025-01-01")

        imp = strategy.run(True, comp, 10000, 50, 1.9)
        old = strategy.run(False, comp, 10000, 50)

        imp_cash, imp_value = imp[0], imp[1]
        old_cash, old_value = old[0], old[1]

        dif_cash = imp_cash - old_cash
        dif_value = imp_value - old_value
        is_diff_positive = dif_value > 0
        sentiment = comp.get_score()

        # Insert the data into the DataFrame
        results_df = pd.concat(
            [
                results_df,
                pd.DataFrame(
                    {
                        "Ticker": [i],
                        "Old Cash": [old_cash],
                        "Old Value": [old_value],
                        "New Cash": [imp_cash],
                        "New Value": [imp_value],
                        "Diff Cash": [dif_cash],
                        "Diff Value": [dif_value],
                        "Sentiment": [sentiment],
                        "Better?": [is_diff_positive],
                    }
                ),
            ],
            ignore_index=True,
        )
    except:
        print(f"Error occured for {i}")
        continue

def analyze_results(results_df):
    """
    Analyze the results DataFrame and print summary statistics.
    - Count of tickers processed
    - Number of positive and negative differences
    - Average of differences in cash and value
    - Average gain for positive value differences
    - Average loss for negative value differences
    """
    # Total number of tickers processed
    total_tickers = len(results_df)

    # Count of positive and negative value differences
    positive_diff_count = results_df["Better?"].sum()
    negative_diff_count = total_tickers - positive_diff_count

    # Averages of differences in cash and value
    avg_diff_cash = results_df["Diff Cash"].mean()
    avg_diff_value = results_df["Diff Value"].mean()

    # Calculate average gain for positive differences and average loss for negative differences
    positive_diffs = results_df[results_df["Better?"] == True]["Diff Value"]
    negative_diffs = results_df[results_df["Better?"] == False]["Diff Value"]

    avg_gain = positive_diffs.mean() if not positive_diffs.empty else 0
    avg_loss = negative_diffs.mean() if not negative_diffs.empty else 0

    # Print summary
    print("Summary Statistics:")
    print(f"Total Tickers Processed: {total_tickers}")
    print(f"Number of Positive Value Differences: {positive_diff_count}")
    print(f"Number of Negative Value Differences: {negative_diff_count}")
    print(f"Average Difference in Cash: {avg_diff_cash:.2f}")
    print(f"Average Difference in Value: {avg_diff_value:.2f}")
    print(f"Average Gain (Positive Differences): {avg_gain:.2f}")
    print(f"Average Loss (Negative Differences): {avg_loss:.2f}")


# Call the function to analyze the results
analyze_results(results_df)
print(results_df)






