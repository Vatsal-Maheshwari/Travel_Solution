from flight_route import get_flight_route
from roud_route import get_road_route
from train_route import get_train_route


def main():
    """

    """
    # origin = "The Old Schools, Trinity Ln, Cambridge"
    # destination = "Dumbreck Rd, Bellahouston, Glasgow"
    origin = "Langton Pl, Bury Saint Edmunds, UK"
    destination = "Dumbreck Rd, Glasgow, UK"
    # origin = "Katwaria Sarai"
    # destination = "IIT Bombay"
    # origin = "The Old Schools, Trinity Ln, Cambridge"
    # destination = "Broadway 10012, New York"
    # origin = "New Street, Birmingham"
    # destination = "Dumbreck Rd, Bellahouston, Glasgow"
    # origin = "Near Oxford Street, Soho, London"
    # destination = "Lombard Street, San Francisco, California"
    # origin = "Croydon High Street, Croydon"
    # destination = "Hollywood Boulevard, Los Angeles"

    print(f"\nReceived Journey Request from {origin} to {destination}\n")

    train_option = get_train_route(origin, destination)

    cab_option = get_road_route(origin, destination)

    flight_option = get_flight_route(origin, destination)

    print("Cab Option: \n", cab_option, "\n\n")

    print("Train Option: \n", train_option, "\n\n")

    print("Flight Option: \n", flight_option, "\n\n")


if __name__ == '__main__':
    main()
