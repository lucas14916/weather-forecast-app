import streamlit as st
import requests
import pathlib
import os
from huggingface_hub import InferenceClient
from streamlit_javascript import st_javascript


# Function to load CSS from the 'assets' folder
def load_css(file_path):
   with open(file_path) as f:
       st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Load external CSS
css_path = pathlib.Path("assets/styles.css")
load_css(css_path)


# Inject Google Fonts CSS
st.markdown("""
   <style>
   @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,100..900;1,100..900&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');


   html, body, [class*="css"]  {
       font-family: 'Inter', sans-serif;
   }
   </style>
""", unsafe_allow_html=True)


# Page configuration
st.set_page_config(page_title="Lark Weather Forecast App", page_icon="☁️", layout="centered", initial_sidebar_state="collapsed")


logo = "https://i.imgur.com/tyvV4FZ.png"
st.logo(logo, size = "large")


os.environ["HF_TOKEN"] = st.secrets["HF_TOKEN"] # Stored in .streamlit/secrets.toml


client = InferenceClient(
   provider="featherless-ai",
   api_key=os.environ["HF_TOKEN"],
)


def call_qwen2_api(prompt):
   try:
       completion = client.chat.completions.create(
           model="Qwen/Qwen2-7B-Instruct",
           messages=[
               {"role": "user", "content": prompt}
           ],
           max_tokens=200,
           temperature=0
       )
       return completion.choices[0].message.content
   except Exception as e:
       st.error(f"API Error: {e}")
       return "Sorry, something went wrong."


# Display recommendations inside styled container
def recommendation(response):
   paragraphs = response.split('\n\n')
   formatted_paragraphs = ''.join(
       f'<p style="margin-top: 10px; color: #ffffff;">{p}</p>' for p in paragraphs
   )
   with st.container():
       st.markdown(
           f"""
           <div style="
               background-color: #1e90ff;
               padding: 16px;
               border-radius: 16px;
               border: 2px solid #1e90ff;
           ">
               <span class="blue-markdown">&thinsp; <strong>Outfit and Activity Recommendations</strong> &thinsp;</span>
               {formatted_paragraphs}
           </div>
           """,
           unsafe_allow_html=True
       )


# Generate weather-based outfit/activity prompt
def generate_weather_description(data):
   try:
       temperature = data['main']['temp'] - 273.15
       description = data['weather'][0]['description']
       city = data['name']


       prompt = (
           f"Use third person. Use a maximum of 100 words. Human asks: Suggest an outfit and an activity for someone in {city} where the weather is "
           f"{description} and the temperature is {temperature:.0f}°C. AI responds: For {city} with {description} and a temperature of {temperature:.0f}°C, the following is suggested."
       )


       response = call_qwen2_api(prompt)
       return recommendation(response)


   except Exception as e:
       st.error(f"Error processing weather data: {e}")


# Text
st.markdown("""
   <style>
   .border-markdown {
       display: inline-block;
       text-align: center;
       font-style: normal;
       font-size: 13px;
       font-family: 'Inter', sans-serif;     
       color: #000000;
       background-color: #ffffff;
       border: 1px solid #d0d0d0;
       border-radius: 20px;
       padding: 5px;
       margin: 0 auto;
       margin-bottom: 20px;
   }
   .center-wrapper {
       text-align: center;
   }
   .center-header-wrapper {
       text-align: center;
       margin-bottom: 15px;
   }
   </style>
""", unsafe_allow_html=True)


st.markdown("""
   <div class="center-wrapper">
       <div class="border-markdown">
           <span>&ensp;</span>
           <img src = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/cpu.svg" width = "18">
           <span>&thinsp; API- and LLM-based recommender &ensp;</span>
       </div>
   </div>
""", unsafe_allow_html=True)


st.markdown("""
   <div class='center-header-wrapper'>
       <span class='blue-header-text'>Lark </span>
       <span class='header-text'>Weather Forecast App</span>
   </div>
""", unsafe_allow_html=True)


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
   result = st_javascript("""await navigator.userAgent;""")


   if result:
       if "Mobi" in result: # Check if user is on mobile
           city = st.text_input(label="", label_visibility="collapsed", placeholder="Enter a city")


           # Loading animation
           if city:
               st.spinner('Fetching weather data...')
               weather_data = get_weather_data(city, weather_api_key)

               # Check if city is found and display weather data
               if(
                   isinstance(weather_data, dict) and
                   weather_data.get("cod") == 200 and
                   "weather" in weather_data and
                   isinstance(weather_data["weather"], list) and
                   len(weather_data["weather"]) > 0
               ):

                   icon_id = weather_data['weather'][0]['icon']
                   icon_url = f"http://openweathermap.org/img/wn/{icon_id}@4x.png"
      
                   city = weather_data['name']
                   description = weather_data['weather'][0]['description']
                   temperature = weather_data['main']['temp'] - 273.15


                   st.markdown("""
                       <style>
                       .center-wrapper {
                           display: flex;
                           flex-direction: column;
                           align-items: center;
                           text-align: center;
                           padding: 10px;
                       }
                       </style>
                   """, unsafe_allow_html=True)                   


                   st.markdown(f"""
                       <div class="center-wrapper">
                           <span class="city-text"><strong>{city}</strong></span>
                           <img src="{icon_url}" width="300" style="margin: 10px 0;">
                           <span class="temp-text"><strong>{temperature:.0f}°C</strong></span>
                           <span class="white-markdown">&ensp;{description}&ensp;</span>
                       </div>
                   """, unsafe_allow_html=True)
                  
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
                   icon_id = None

       else:
           # Alignment of search bar and button
           col0, col1, col2, col3 = st.columns([1, 3, 2, 1])


           with col0:
               st.write("")


           with col1:
               city = st.text_input(label = "", label_visibility = "collapsed", placeholder="Enter a city")


           with col2:
               submit = st.button("Search weather", key="blue")


           with col3:
               st.write("")
  
           # Loading animation
           if submit or city:
               st.spinner('Fetching weather data...')
               weather_data = get_weather_data(city, weather_api_key)

               # Check if city is found and display weather data
               if (
                   isinstance(weather_data, dict) and
                   weather_data.get("cod") == 200 and
                   "weather" in weather_data and
                   isinstance(weather_data["weather"], list) and
                   len(weather_data["weather"]) > 0
               ):

                   icon_id = weather_data['weather'][0]['icon']
                   icon_url = f"http://openweathermap.org/img/wn/{icon_id}@4x.png"

                   a, b, c = st.columns([1,4,6], vertical_alignment="center")

                   with a:
                       st.write("")

                   with b:
                       city = weather_data['name']
                       st.markdown(
                           f'<span class="header-text"><strong>{city}</strong></span>',
                           unsafe_allow_html=True,
                       )

                       st.markdown(
                               f"<span class='big-text'><strong>{weather_data['main']['temp'] - 273.15:.0f}°C</strong></span>",
                               unsafe_allow_html=True,
                       )     

                       description = weather_data['weather'][0]['description']
                       st.markdown(
                           f'<span class="white-markdown">&ensp;{description}&ensp;</span>',
                           unsafe_allow_html=True,
                       )
        
                   with c:
                       st.image(icon_url, width=400)

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
                   icon_id = None




if __name__ == "__main__":
   main()
