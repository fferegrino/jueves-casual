import os

from PIL import Image
import numpy as np
from blend_modes import divide, overlay, multiply, darken_only, normal, dodge
import requests
from io import BytesIO
import re
import streamlit as st
import math


doll = Image.open("doll.png")
letters1 = Image.open("letters.png")
vingette = Image.open("vingette.png").convert("RGBA")
stroke = Image.open("stroke.png")

url = st.text_input(
    "Base image", placeholder="https://...", value="https://images.unsplash.com/photo-1638913970961-1946e5ee65c4"
)

urls_sizes = ["raw", "full", "regular", "small", "thumb"]


UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
if UNSPLASH_ACCESS_KEY is None:
    st.text("There is no API key for Unsplash, this integration will not work")


video_id_re = re.compile(r"(?P<video_id>[\w-]+)\/?$")


def download_unsplash_picture(url, **kwargs):
    match = video_id_re.search(url)
    video_id = match.group().strip("/")
    response = requests.get(
        f"https://api.unsplash.com/photos/{video_id}", headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    )
    json = response.json()
    for url_type in urls_sizes:
        if url_type in json["urls"]:
            img_url = json["urls"][url_type]
            return img_url


url = download_unsplash_picture(url)


response = requests.get(url)
bg = Image.open(BytesIO(response.content)).convert("RGBA")

desired_width = 1920
desired_height = 1080

ratio = desired_width / bg.size[0]

width = int(math.ceil(bg.size[0] * ratio))
height = int(max(bg.size[1] * ratio, 1080))

resized = bg.resize((width, height))
crop_loc = (height / 2) - (desired_height / 2)
bg = resized.crop((0, crop_loc, desired_width, crop_loc + desired_height))


def tf(img):
    foreground_img = np.array(img)  # Inputs to blend_modes need to be numpy arrays.
    return foreground_img.astype(float)  # Inputs to blend_modes need to be floats.


vignette_intensity = st.slider("Vingette", min_value=0.0, max_value=1.0, step=0.1, value=0.7)

blend_stroke = st.checkbox("Blend stroke")

blend = overlay(tf(bg), tf(vingette), vignette_intensity)
blend = overlay(blend, tf(letters1), 1)
if blend_stroke:
    blend = darken_only(blend, tf(stroke), 1)
else:
    blend = normal(blend, tf(stroke), 1)
blend = normal(blend, tf(doll), 1)


blended_img = np.uint8(blend)
blended_img_raw = Image.fromarray(blended_img).convert("RGB")

# Display blended image
st.image(blended_img_raw)


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1000)))
    p = math.pow(1000, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


image_quality = st.slider("Quality", min_value=10, max_value=95, step=5, value=95)

buffered = BytesIO()
blended_img_raw.save(buffered, format="JPEG", quality=image_quality)
byte_im = buffered.getvalue()
bb = buffered.tell()
mb = convert_size(bb)

st.download_button(label=f"Download image ({mb})", data=byte_im, file_name="thumbnail.jpg", mime="image/jpeg")
