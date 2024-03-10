import os
import zipfile
import glob

import pandas
import numpy as np
import matplotlib.pyplot as plt


def prepare_data():
    extract_zip_files("data/zipped_data", "data/unzipped_data")

    csv_files = get_sorted_csv_files("data/unzipped_data")
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


def print_close_price(data_frame):
    plt.figure(figsize=(24, 12))
    plt.plot(data_frame["close_time"], data_frame["close"], label="Close Price", color="cornflowerblue")
    place_xticks(data_frame)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("Close Price Of The ETHUSDC Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("close_price_plot.png")
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


def calculate_signal_line(macd_line):
    signal_line = []
    for i in range(len(macd_line)):
        if i < 9:
            signal_line.append(None)
            continue
        ema_9 = exponential_moving_average(macd_line, i, 9)
        signal_line.append(ema_9)
    return signal_line


def print_macd_indicator(data_frame, macd_line, signal_line):
    plt.figure(figsize=(24, 12))
    plt.plot(data_frame["close_time"], macd_line, label="MACD Line", color="mediumorchid")
    plt.plot(data_frame["close_time"], signal_line, label="Signal Line", color="dodgerblue")
    place_xticks(data_frame)
    plt.title("MACD Indicator For The ETHUSDC Over Time")
    plt.xlabel("Time")
    plt.ylabel("MACD Value")
    plt.legend()
    plt.grid(True)
    plt.savefig("macd_plot.png")
    plt.close()


def place_xticks(data_frame):
    date_range = pandas.date_range(start=data_frame["close_time"].min(), end=data_frame["close_time"].max(), freq='D')
    plt.xticks(date_range, rotation=45)
    plt.xticks(rotation=45)


if __name__ == "__main__":
    data = prepare_data()
    macd = calculate_macd_line(data)
    signal = calculate_signal_line(macd)

    print_close_price(data)
    print_macd_indicator(data, macd, signal)
