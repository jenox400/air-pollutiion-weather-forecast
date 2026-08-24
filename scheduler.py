from apscheduler.schedulers.blocking import BlockingScheduler

from src.data_collector import collect_data


LATITUDE = 28.0229
LONGITUDE = 73.3119


def run_collection():

    print("\n==============================")
    print("Scheduled data collection")
    print("==============================")

    collect_data(
        LATITUDE,
        LONGITUDE
    )


scheduler = BlockingScheduler()


scheduler.add_job(
    run_collection,
    "interval",
    hours=1
)


if __name__ == "__main__":

    print("Data collector scheduler started.")

    # Run once immediately
    run_collection()

    print("Waiting for next collection...")

    scheduler.start()