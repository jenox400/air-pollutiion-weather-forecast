from src.training_data import (
    load_training_data,
    create_features
)


def main():

    print("Loading data...")

    df = load_training_data()

    print(
        f"Raw records: {len(df)}"
    )

    df = create_features(df)

    print(
        f"ML-ready records: {len(df)}"
    )

    print("\nDataset preview:\n")

    print(
        df.head().to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()