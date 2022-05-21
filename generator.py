from PIL import Image
import numpy as np
from blend_modes import divide, overlay, multiply, darken_only,normal
import requests
from io import BytesIO
import streamlit as st
from traitlets import default


doll = Image.open("doll.png")
letters1 = Image.open("letters.png")
vingette = Image.open("vingette.png").convert("RGBA")
stroke = Image.open("stroke.png")


url = st.text_input('Base image', placeholder='https://...', value='https://images.unsplash.com/photo-1638913970961-1946e5ee65c4')
response = requests.get(url)
bg = Image.open(BytesIO(response.content)).convert("RGBA")



thumbnail = 1920,1080
crop = (0,0,*thumbnail)
bg= bg.crop(crop)


def tf(img):
    foreground_img = np.array(img)  # Inputs to blend_modes need to be numpy arrays.
    return foreground_img.astype(float)  # Inputs to blend_modes need to be floats.


vignette_intensity = st.slider('Vingette', min_value=0.0, max_value=1.0, step=0.1, value=0.7)

blend = overlay(tf(bg), tf(vingette), vignette_intensity)
blend = overlay(blend, tf(letters1), 1)
blend = darken_only(blend, tf(stroke), 1)
blend = normal(blend, tf(doll), 1)


blended_img = np.uint8(blend)
blended_img_raw = Image.fromarray(blended_img)

# Display blended image
st.image(blended_img_raw)

buffered = BytesIO()
blended_img_raw.save(buffered, format="PNG")
byte_im = buffered.getvalue()


st.download_button(
    label="Download image",
    data=byte_im,
    file_name='thumbnail.png',
    mime="image/x-png"
)


