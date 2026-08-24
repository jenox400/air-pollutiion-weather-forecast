from src.location import get_location


city = input("Enter city name: ")

location = get_location(city)

if location is None:
    print("Location not found.")

else:
    print("\nLocation found!")
    print("Name:", location["name"])
    print("Latitude:", location["latitude"])
    print("Longitude:", location["longitude"])