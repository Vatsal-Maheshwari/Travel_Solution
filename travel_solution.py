import streamlit as st
from flight_route import get_flight_route
from roud_route import get_road_route
from train_route import get_train_route


def main():
    """

    """
    st.title("Personal Trip Planner")

    user_origin = st.text_input("Enter the Place You Want to Start Your Journey.")

    user_destination = st.text_input("Enter the Place You Want to Visit")

    user_travel_preference = st.text_input("Enter the Travel Mode(Taxi, Rail or Flight) You Prefer for your Journey.")

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

    if st.button("Search"):
        print(f"\nReceived Journey Request from {user_origin} to {user_destination}\n")

        if user_travel_preference == "Rail":
            train_option = get_train_route(user_origin, user_destination)
            print("Train Option: \n", train_option, "\n\n")
            st.markdown(''':green[Train Option:] ''' + train_option)

        elif user_travel_preference == "Flight":
            flight_option = get_flight_route(user_origin, user_destination)
            print("Flight Option: \n", flight_option, "\n\n")
            st.markdown(''':green[Flight Option:] ''' + flight_option)
        else:
            cab_option = get_road_route(user_origin, user_destination)
            print("Cab Option: \n", cab_option, "\n\n")
            st.markdown(''':green[Cab Option:] ''' + cab_option)


if __name__ == '__main__':
    main()
