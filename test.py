import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)


user_lat = 49.79925
user_lon = -97.14087
load_dotenv()
my_api_key = os.getenv('API_KEY')

def stops():
    # Your Winnipeg Transit API key
    API_KEY = my_api_key

    # Base URL for the Winnipeg Transit API
    BASE_URL = 'https://api.winnipegtransit.com/v3/stops.json'

    # Coordinates for a specific location (Winnipeg)
    latitude =  user_lat
    longitude = user_lon

    # Define the parameters including a radius in meters (e.g., 500 meters)
    params = {
    'lat': latitude,
    'lon': longitude,
    'distance': 500,  # Radius in meters around the lat/lon point
    'api-key': API_KEY
    }

    # Make a GET request to the API
    response = requests.get(BASE_URL, params=params)

    # Check if the request was successfulS
    if response.status_code == 200:
        data = response.json()
        #print(data['locations'])
        print("Stops near the location:")
        count = 0

        for stop in data['stops']:
            
            stop_name = stop['name']
            stop_number = stop['key']
            street = stop['street']
            direction = stop['direction']
            #print(f" {count}: Stop Name: {stop_name} Stop Number: {stop_number} ", f"Street: {street} \n")
            schedule(API_KEY, stop_number)
            
            count += 1
    else:
        print(f"Failed to retrieve data: {response.status_code}, Reason: {response.text}")


def schedule(API_KEY, stop_number):

    BASE_URL = f"https://api.winnipegtransit.com/v3/stops/{stop_number}/schedule.json"
  
    params = {
    
    'api-key': API_KEY,
    'max-results-per-route': 2
    
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
       # print(data)
       # for schedule in data['route-schedules']:
       #S     print(len(data['route-schedules']))
        time = data['query-time']
        time_obj = datetime.strptime(time,"%Y-%m-%dT%H:%M:%S")
        time_am_pm = time_obj.strftime("%I:%M %p")
        print("current time: ",time_am_pm)
        
        stop= data['stop-schedule'].get('stop') 
        print(f"Stop Name: {stop['name']}, Stop Number: {stop['key']}")
        route = data['stop-schedule'].get('route-schedules')
        if len(route) == 0 :
            print("No Service at this stop at this time")
            return
        route_schedule = []
        for schedule_details in route:
            if 'route'  in schedule_details and 'key' in schedule_details['route'] and 'name' in schedule_details['route']:
                route_number= schedule_details['route']['key']
                route_name = schedule_details['route']['name']
                # List to hold the route details with time differences
                
                for stop_info in schedule_details['scheduled-stops']:
                #  print(stop_info)
                    if 'times'in stop_info and 'departure' in stop_info['times']:
                        stop_arrival_time = stop_info['times']['departure']
                        schedule_arrival_time=None
                        estimated_arrival_time=None
                        if 'scheduled' in stop_arrival_time and 'estimated' in stop_arrival_time:
                            schedule_arrival_time=stop_arrival_time['scheduled']
                            estimated_arrival_time=stop_arrival_time['estimated']
                        else:
                            logging.warning(f"Missing 'scheduled' or 'estimated' time for stop: {stop_info}")

                        
                        time1 = datetime.strptime(schedule_arrival_time,"%Y-%m-%dT%H:%M:%S")
                        time2 = datetime.strptime(estimated_arrival_time,"%Y-%m-%dT%H:%M:%S")
                        time_diff = time2 - time1
                        time_diff_minutes = int(time_diff.total_seconds() / 60)
                        if time_diff_minutes > 0:
                            late_time=time2-datetime.now()
                            late_time_minutes = int(late_time.total_seconds() / 60)
                            if late_time_minutes <=15:
                                route_schedule.append({
                                    "route_number": route_number,
                                    "route_name": route_name,
                                    "time_remaining": late_time_minutes,
                                    "time_string":f"late {late_time_minutes} mins"
                                })
                                #print("Route: ",route_name, " (",route_number,") : late",late_time_minutes,"mins")
                            else:
                                time2_am_pm = time2.strftime("%I:%M %p")
                                route_schedule.append({
                                    "route_number": route_number,
                                    "route_name": route_name,
                                    "time_remaining": late_time_minutes,
                                    "time_string":f"late {time2_am_pm} mins"
                                })
                                #print("Route: ",route_name, " (",route_number,") : late",time2_am_pm)
                        else:
                            on_time=int((time1-datetime.now()).total_seconds()/60)
                            if on_time <=15:
                                route_schedule.append({
                                    "route_number": route_number,
                                    "route_name": route_name,
                                    "time_remaining": on_time,
                                    "time_string":f" {on_time} mins"
                                })
                                #print("Route: ",route_name, " (",route_number,") : ",on_time," mins")
                            else:
                                time1_am_pm = time1.strftime("%I:%M %p")
                                route_schedule.append({
                                    "route_number": route_number,
                                    "route_name": route_name,
                                    "time_remaining": on_time,
                                    "time_string":f"late {time1_am_pm} mins"
                                })
                                #print("Route: ",route_name, " (",route_number,") : ",time1_am_pm,"mins")
                    else:
                        logging.warning(f"Missing 'times' or 'departure' for stop: {stop_info}")
            else:
                logging.warning(f"Missing 'route' or 'key' or 'name' for stop: {stop_info}")
        route_schedule_sorted = sorted(route_schedule, key=lambda x: x['time_remaining'])

        for item in route_schedule_sorted:
            print("Route: ",item['route_name'], " (",item['route_number'],") : ",item['time_string'])

             
    else:
        print(f"Failed to retrieve data: {response.status_code}, Reason: {response.text}")

   
if __name__ == "__main__":
    
    stop_number = 60079
   # schedule(API_KEY, stop_number)
    stops()