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

    # user_budget = st.text_input("Enter the Flight Class(Economy, First or Business Class) you prefer to Travel.")
    user_budget = ""

    user_car_availability = st.text_input("Do you prefer your personnel car for travel ?")

    # user_car_max_distance = st.text_input("If answer to above question is yes, "
    #                                       "then how much distance you would prefer to travel by your personnel car?")
    user_car_max_distance = ""

    # origin = "The Old Schools, Trinity Ln, Cambridge"
    # destination = "Dumbreck Rd, Bellahouston, Glasgow"
    # origin = "Langton Pl, Bury Saint Edmunds, UK"
    # destination = "Dumbreck Rd, Glasgow, UK"
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
        car_status = False
        if user_car_availability in ["Yes", "yes", "Y", "y"]:
            car_status = True
        print(f"\nReceived Journey Request from {user_origin} to {user_destination}\n")

        if user_travel_preference == "Rail":
            train_option = get_train_route(user_origin, user_destination, car_status)
            print("Train Option: \n", train_option, "\n\n")
            st.markdown(''':green[Train Option:] ''')
            for i in range(0, len(train_option.split(','))):
                st.markdown(train_option.split(',')[i], unsafe_allow_html=True)
        elif user_travel_preference == "Flight":
            flight_option = get_flight_route(user_origin, user_destination, car_status, user_budget)
            print("Flight Option: \n", flight_option, "\n\n")
            st.markdown(''':green[Flight Option:]''')
            for i in range(0, len(flight_option.split('*'))):
                st.markdown(flight_option.split('*')[i], unsafe_allow_html=True)
        else:
            cab_option = get_road_route(user_origin, user_destination, car_status)
            print("Cab Option: \n", cab_option, "\n\n")
            st.markdown(''':green[Cab Option:] ''')
            st.markdown(cab_option)


if __name__ == '__main__':
    main()
