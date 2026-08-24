from src.data_collector import collect_data


LATITUDE = 28.0229
LONGITUDE = 73.3119


if __name__ == "__main__":

    collect_data(
        LATITUDE,
        LONGITUDE
    )