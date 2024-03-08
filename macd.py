import os
import zipfile
import glob

import pandas


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


def get_last_n_rows(data_frames, n):
    return data_frames.tail(n)


def add_headers(data_frames):
    for data_frame in data_frames:
        data_frame.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
                              "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
    return data_frames


def convert_to_datetime(data_frame):
    data_frame["open_time"] = pandas.to_datetime(data_frame["open_time"], unit="ms")
    data_frame["close_time"] = pandas.to_datetime(data_frame["close_time"], unit="ms")
    return data_frame


if __name__ == "__main__":
    data = prepare_data()
    print(data)
