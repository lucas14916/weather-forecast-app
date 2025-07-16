import streamlit as st
import requests
import pathlib

# Function to load CSS from the 'assets' folder
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the external CSS
css_path = pathlib.Path("assets/styles.css")
load_css(css_path)

# Page configuration
st.set_page_config(page_title="Lark Weather Forecast App", page_icon="☁️", layout="centered", initial_sidebar_state="collapsed")

logo = "https://i.imgur.com/tyvV4FZ.png"
st.logo(logo, size = "large")

# Hugging Face Interface API Setup
API_URL = "https://router.huggingface.co/featherless-ai/v1/chat/completions"
HF_TOKEN = st.secrets["HF_TOKEN"] # Stored in .streamlit/secrets.toml

headers = {
    "Authorization": f"Bearer {HF_TOKEN}" # Authenticates request to Hugging Face API
} 

def call_qwen2_api(prompt):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "Qwen/Qwen2-7B-Instruct",
        "max_new_tokens": 10,
        "temperature": 0
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Recommendations for generate_weather_description(data) below
def recommendation(response):
    with st.container(border = True):
        st.markdown(
            '<span class="blue-markdown">&thinsp; <strong>Outfit and Activity Recommendations</strong> &thinsp;</span>',
            unsafe_allow_html=True,
        )
        st.write(response)

def generate_weather_description(data):
    try:
        temperature = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        city = data['name']

        prompt = (
            f"Use third person. Human asks: Suggest an outfit and an activity for someone in {city} where the weather is "
            f"{description} and the temperature is {temperature:.0f}°C. AI responds: For {city} with {description} and a temperature of {temperature:.0f}°C, the following is suggested."
        )

        response = call_qwen2_api(prompt)
        return recommendation(response)

    except Exception as e:
        st.error(f"Error: {e}")

# Text
st.markdown("<div class='header-text'>Lark Weather Forecast App</div>", unsafe_allow_html=True)
st.markdown("<div class='normal-text'>Get real-time weather updates and receive suitable outfit and activity recommendations.</div>", unsafe_allow_html=True)

def get_weather_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()

def get_minmaxtemp_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/forecast/daily?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()

# Main function
def main ():
    weather_api_key = "a0763ad3df6b1ba6a91207cc6788d66c"

    # Alignment of search bar and button
    col1, col2 = st.columns([3,1])

    with col1:
        city = st.text_input(label = "", label_visibility = "collapsed", placeholder="Enter a city")

    with col2:
        submit = st.button("Search weather", key="blue")

    # Loading animation
    if submit:
        st.spinner('Fetching weather data...')
        weather_data = get_weather_data(city, weather_api_key)

        # Check if city is found and display weather data
        if weather_data.get("cod") != 404:

            icon_id = weather_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_id}@4x.png"
    
            a, b, c = st.columns([3,2,2], vertical_alignment="center")

            with a:
                city = weather_data['name']
                st.markdown(
                    f'<span class="header-text"><strong>{city}</strong></span>',
                    unsafe_allow_html=True,
                )

                description = weather_data['weather'][0]['description']
                st.markdown(
                    f'<span class="white-markdown">&ensp;{description}&ensp;</span>',
                    unsafe_allow_html=True,
                )
            
            with st.container(border = True):
                with b:
                    st.image(icon_url, width = 200)
            
                with c:
                    st.markdown(
                        f"<span class='big-text'><strong>{weather_data['main']['temp'] - 273.15:.0f}°C</strong></span>",
                    unsafe_allow_html=True,
                )      

            d, e = st.columns(2)
            f, g = st.columns(2)

            d.metric("Humidity", f"{weather_data['main']['humidity']:.0f}%", border=True)
            e.metric("Wind", f"{weather_data['wind']['speed']} m/s", border=True)

            f.metric("Minimum daily temperature", f"{weather_data['main']['temp_min'] - 273.15:.0f} °C", border=True)
            g.metric("Maximum daily temperature", f"{weather_data['main']['temp_max'] - 273.15:.0f} °C", border=True)
                
            # Generate and display recommendation for weather
            weather_description = generate_weather_description(weather_data)

        else:
            # Display an error message if the city is not found
            st.error("City not found!")


if __name__ == "__main__":
    main()
