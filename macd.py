import os
import sys
import zipfile
import glob

import pandas
import matplotlib.pyplot as plt


def prepare_data(coin_pair_name):
    extract_zip_files(f"data/zipped_data/{coin_pair_name}", f"data/unzipped_data/{coin_pair_name}")

    csv_files = get_sorted_csv_files(f"data/unzipped_data/{coin_pair_name}")
    data_frames = [pandas.read_csv(csv_file, header=None) for csv_file in csv_files]
    add_headers(data_frames)

    data_frame = concatenate_data(data_frames)
    data_frame = get_last_n_rows(data_frame, 1000)
    data_frame = convert_to_datetime(data_frame)

    return data_frame


def extract_zip_files(source_directory, destination_directory):
    for zip_filename in os.listdir(source_directory):
        zip_directory = os.path.join(source_directory, zip_filename)
        with zipfile.ZipFile(zip_directory, "r") as zip_file:
            zip_file.extractall(destination_directory)


def get_sorted_csv_files(source_directory):
    csv_files = glob.glob(f"{source_directory}/*.csv")
    csv_files.sort()
    return csv_files


def concatenate_data(data_frames):
    return pandas.concat(data_frames, ignore_index=True)


def get_last_n_rows(data_frame, n):
    last_n_rows = data_frame.tail(n)
    return last_n_rows.reset_index(drop=True)


def add_headers(data_frames):
    for data_frame in data_frames:
        data_frame.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
                              "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
    return data_frames


def convert_to_datetime(data_frame):
    data_frame["open_time"] = pandas.to_datetime(data_frame["open_time"], unit="ms")
    data_frame["close_time"] = pandas.to_datetime(data_frame["close_time"], unit="ms")
    return data_frame


def print_close_price(data_frame, coin_pair_name):
    plt.figure(figsize=(24, 12))
    plt.plot(data_frame["close_time"], data_frame["close"], label="Close Price", color="cornflowerblue")
    place_xticks(data_frame)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.gca().yaxis.set_major_formatter("${:,.0f}".format)
    plt.title(f"Close Price Of The {coin_pair_name} Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"plots/{coin_pair_name}/close_price_plot_.png")
    plt.close()


def exponential_moving_average(data_iterable, start, n):
    alpha = 2 / (n + 1)

    numerator = 0
    denominator = 0
    for i in range(n + 1):
        if start - i < 0:
            break
        numerator += data_iterable[start - i] * (1 - alpha) ** i
        denominator += (1 - alpha) ** i

    ema = numerator / denominator

    return ema


def moving_average_convergence_divergence(data_frame, start):
    ema_12 = exponential_moving_average(data_frame, start, 12)
    ema_26 = exponential_moving_average(data_frame, start, 26)
    macd_value = ema_12 - ema_26
    return macd_value


def calculate_macd_line(data_frame):
    return [moving_average_convergence_divergence(data_frame["close"], i) for i in range(len(data))]


def calculate_signal_line(macd_values):
    signal_line = []
    for i in range(len(macd_values)):
        if i < 9:
            signal_line.append(None)
            continue
        ema_9 = exponential_moving_average(macd_values, i, 9)
        signal_line.append(ema_9)
    return signal_line


def print_macd_indicator(data_frame, macd_values, signal_values, coin_pair_name, buy_points, sell_points):
    plt.figure(figsize=(24, 12))
    plt.plot(data_frame["close_time"], macd_values, label="MACD Line", color="mediumorchid")
    plt.plot(data_frame["close_time"], signal_values, label="Signal Line", color="dodgerblue")

    # Plot buy points
    buy_times = [data_frame["close_time"].iloc[i] for i in buy_points]
    buy_macd = [macd_values[i] for i in buy_points]
    plt.scatter(buy_times, buy_macd, color="olivedrab", marker="^", label="Buy")

    # Plot sell points
    sell_times = [data_frame["close_time"].iloc[i] for i in sell_points]
    sell_macd = [macd_values[i] for i in sell_points]
    plt.scatter(sell_times, sell_macd, color="red", marker="v", label="Sell")

    place_xticks(data_frame)
    plt.title(f"MACD Indicator For The {coin_pair_name} Over Time")
    plt.xlabel("Time")
    plt.ylabel("MACD Value")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"plots/{coin_pair_name}/macd_plot.png")
    plt.close()


def print_portfolio(data_frame, portfolio_values, coin_pair_name):
    plt.figure(figsize=(24, 12))
    plt.plot(data_frame["close_time"], portfolio_values, label="Total Value Of Portfolio", color="mediumorchid")
    place_xticks(data_frame)
    plt.title(f"Portfolio Value Over Time While Investing In The {coin_pair_name} Using Algorithm Based On The MACD")
    plt.xlabel("Time")
    plt.ylabel("Portfolio Value")
    plt.gca().yaxis.set_major_formatter("${:,.0f}".format)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"plots/{coin_pair_name}/portfolio_plot.png")
    plt.close()


def place_xticks(data_frame):
    date_range = pandas.date_range(start=data_frame["close_time"].min(), end=data_frame["close_time"].max(), freq="D")
    plt.xticks(date_range, rotation=45)
    plt.xticks(rotation=45)


def create_dirs(coin_pair_name):
    if not os.path.exists(f"plots/{coin_pair_name}"):
        os.makedirs(f"plots/{coin_pair_name}")
    if not os.path.exists(f"unzipped_data/{coin_pair_name}"):
        os.makedirs(f"unzipped_data/{coin_pair_name}")


def investing_algorithm(initial_funds, prices, macd_values, signal_values):
    funds = initial_funds
    coins = 0
    portfolio_values = [initial_funds]
    buy_points = []
    sell_points = []

    for i in range(1, len(macd_values)):
        if any(x is None for x in [macd_values[i], macd_values[i - 1], signal_values[i], signal_values[i - 1]]):
            portfolio_values.append(funds + coins * prices[i])
            continue
        if macd_values[i] > signal_values[i] and macd_values[i - 1] <= signal_values[i - 1]:
            # Buy signal
            if funds > 0:
                buy_points.append(i)
                coins_to_buy = funds / prices[i]
                coins += coins_to_buy
                funds -= coins_to_buy * prices[i]
        elif macd_values[i] < signal_values[i] and macd_values[i - 1] >= signal_values[i - 1]:
            # Sell signal
            if coins > 0:
                sell_points.append(i)
                funds += coins * prices[i]
                coins = 0
        portfolio_values.append(funds + coins * prices[i])

    final_funds = funds + coins * prices.iloc[-1]
    return final_funds, portfolio_values, buy_points, sell_points


def simple_algorithm(initial_funds, prices):
    funds = initial_funds
    coins = 0

    # Buy all the coins at the beginning
    if funds > 0:
        coins_to_buy = funds / prices[0]
        coins += coins_to_buy
        funds -= coins_to_buy * prices[0]

    final_funds = funds + coins * prices.iloc[-1]
    return final_funds


def print_information(data, initial_funds, final_funds, simple_final_funds):
    final_change = final_funds / initial_funds * 100
    simple_final_change = simple_final_funds / initial_funds * 100

    print(data)

    print(f"In the end, funds invested at the beginning of the value of ${initial_funds:,.2f}, "
          f"are worth ${final_funds:,.2f} after using the algorithm based on the MACD index.\n"
          f"The change is {final_change:,.2f}% of the initial value.\n")

    print(f"If we simply bought all the coins at the beginning (with ${initial_funds:,.2f} for the initial funds) "
          f"and sold them at the end, the value would be ${simple_final_funds:,.2f}.\n"
          f"The change is {simple_final_change:,.2f}% of the initial value.\n")

    if final_change > simple_final_change:
        print(f"The algorithm based on the MACD index outperformed the simple algorithm by "
              f"{final_change - simple_final_change:,.2f} percentage points of the change.")
    elif final_change < simple_final_change:
        print(f"The simple algorithm outperformed the algorithm based on the MACD index by "
              f"{simple_final_change - final_change:,.2f} percentage points of the change.")
    else:
        print("The algorithm based on the MACD index performed equally well as the simple algorithm.")


if __name__ == "__main__":
    coin_pair_name = str(sys.argv[1])
    initial_funds = float(sys.argv[2])

    create_dirs(coin_pair_name)

    data = prepare_data(coin_pair_name)
    macd = calculate_macd_line(data)
    signal = calculate_signal_line(macd)
    final_funds, portfolio, buy_points, sell_points = investing_algorithm(initial_funds, data["close"], macd, signal)
    simple_final_funds = simple_algorithm(initial_funds, data["close"])

    print_close_price(data, coin_pair_name)
    print_macd_indicator(data, macd, signal, coin_pair_name, buy_points, sell_points)
    print_portfolio(data, portfolio, coin_pair_name)

    print_information(data, initial_funds, final_funds, simple_final_funds)
