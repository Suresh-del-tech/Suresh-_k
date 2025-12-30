import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

API_KEY = "a91570ba0abd028f5d257cc2506209a7"

# Function to fetch weather by city name
def get_weather():
    city = city_entry.get()
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if 'main' in data and 'weather' in data:
            show_weather(data)
        else:
            result_label.config(text=f"Error: {data.get('message', 'No data')}")
            map_label.config(image="", text="No Map")
    except Exception as e:
        result_label.config(text="Error: " + str(e))
        map_label.config(image="", text="No Map")

# Function to display weather and map
def show_weather(data):
    temp = data['main']['temp']
    condition = data['weather'][0]['description']
    lat = data['coord']['lat']
    lon = data['coord']['lon']

    result_label.config(text=f"Temperature: {temp} °C\nCondition: {condition}")

    # Load map
    map_url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z=10&size=450,250&l=map&pt={lon},{lat},pm2rdm"
    map_response = requests.get(map_url)
    map_img = Image.open(BytesIO(map_response.content))
    map_img_tk = ImageTk.PhotoImage(map_img)

    map_label.config(image=map_img_tk, text="")
    map_label.image = map_img_tk  # Keep reference

# Function to get weather when clicking on map (convert pixel to geo approx)
def map_click(event):
    try:
        # Get last known lat/lon from result label
        if "Temperature" not in result_label.cget("text"):
            return  # no weather yet, nothing to convert

        # Extract center lat/lon
        city = city_entry.get()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        lat = data['coord']['lat']
        lon = data['coord']['lon']

        # Map size (must match static map request)
        width, height = 450, 250

        # Convert pixel click → geo approx (basic linear conversion)
        dx = (event.x - width/2) / (width/2) * 0.5  # small range shift
        dy = (event.y - height/2) / (height/2) * 0.5

        clicked_lon = lon + dx * 5   # rough adjust
        clicked_lat = lat - dy * 5

        # Get weather for clicked point
        url2 = f"https://api.openweathermap.org/data/2.5/weather?lat={clicked_lat}&lon={clicked_lon}&appid={API_KEY}&units=metric"
        response2 = requests.get(url2)
        data2 = response2.json()
        if 'main' in data2 and 'weather' in data2:
            show_weather(data2)
    except Exception as e:
        result_label.config(text="Click Error: " + str(e))

# GUI setup
root = tk.Tk()
root.title("Weather App with Map")
root.geometry("500x500")

tk.Label(root, text="Enter City:").pack(pady=5)
city_entry = tk.Entry(root)
city_entry.pack(pady=5)

tk.Button(root, text="Get Weather", command=get_weather).pack(pady=5)
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

map_label = tk.Label(root)
map_label.pack()

# Bind mouse click on map
map_label.bind("<Button-1>", map_click)

root.mainloop()
