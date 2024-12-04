from flask import Flask, jsonify, redirect, request, session, url_for,render_template
from dotenv import load_dotenv
import requests
import os
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
load_dotenv()
my_api_key = os.getenv('API_KEY')
app = Flask(__name__)
app.config['SECRET_KEY'] =  os.urandom(24)

@app.route('/')
def index():
    latitude=session.get('latitude')
    longitude=session.get('longitude')
    html=stops(my_api_key,latitude,longitude)
    print(latitude,longitude)
    
    return render_template('index.html', lat=latitude, long=longitude, myhtml=html)  

def stops(API_KEY ,latitude,longitude):
    # Base URL for the Winnipeg Transit API
    BASE_URL = 'https://api.winnipegtransit.com/v3/stops.json'

    

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
    result=" "
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
            #result2 = schedule(API_KEY, stop_number)
            result += f"<a href='/stop_schedule' onclick='postStopNumber(\"{stop_number}\",\"{stop_name}\")'> <p>{count}: Stop Name: {stop_name} Stop Number: {stop_number} Street: {street} Direction: {direction} </p></a>"
            #result += result2
            
            count += 1
            
    else:
        print(f"Failed to retrieve data: {response.status_code}, Reason: {response.text}")

    return result
@app.route("/location", methods=["POST"])
def receive_location():
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    session["latitude"] = latitude
    session["longitude"] = longitude
    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "message": "Location received successfully"
    })



@app.route('/get_schedule', methods=["POST"])
def get_schedule():
    print(f"Request Method: {request.method}")

    data=request.get_json()
    if not data or "stop_number" not in data:
        return jsonify({"error": "stop_number is required"}), 400
    stop_number = data.get("stop_number")
    stop_name = data.get("stop_name")
    session["stop_name"] = stop_name
    session["stop_number"] = stop_number
    return jsonify({"stop_number": stop_number }), 200

@app.route('/stop_schedule')
def stop_schedule():
    print(session.get('stop_number'))
    html=schedule(my_api_key,session.get('stop_number'))
    latitude=session.get('latitude')
    longitude=session.get('longitude')
    name=session.get('stop_name')
    print(name)
    return render_template('stop_schedule.html', lat=latitude, long=longitude , myhtml=html,Stop_Name=name)
def schedule(API_KEY, stop_number):
    
    result=" "

    BASE_URL = f"https://api.winnipegtransit.com/v3/stops/{stop_number}/schedule.json"
  
    params = {
    
    'api-key': API_KEY,
    'max-results-per-route': 2
    
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
      
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
            #print(schedule_details)            
            if 'route'  in schedule_details :
                if 'key' in schedule_details['route']:
                    
                    route_number= schedule_details['route']['key']
                    rout_name=""
                    if 'name' not in schedule_details['route'] :
                        route_name=schedule_details['route']['key']
                    else:
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
                print("Missing 'route' or 'key' or 'name' for stop: ",stop_number)
        route_schedule_sorted = sorted(route_schedule, key=lambda x: x['time_remaining'])

        for item in route_schedule_sorted:
            print("Route: ",item['route_name'], " (",item['route_number'],") : ",item['time_string'])
            result+=f"<p>Route:{item['route_name']}, ({item['route_number']}) : {item['time_string']}</p>"

             
    else:
        print(f"Failed to retrieve data: {response.status_code}, Reason: {response.text}")
    return result
if __name__ == '__main__':
    app.run(debug=True)
    