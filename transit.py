import geocoder

# Get the current location using IP address
g = geocoder.ip('me')

# Print latitude and longitude
print(f"Latitude: {g.latlng[0]}, Longitude: {g.latlng[1]}")
