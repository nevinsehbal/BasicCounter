import streamlit as st
import time
from PIL import Image, ImageDraw, ImageFont
import base64

# --- Config ---
font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
progress_colors = [
    "#FF0000", "#FF3300", "#FF6600", "#FF8000", "#FF9900", "#FFB300",
    "#FFCC00", "#FFD900", "#FFFF00", "#CCFF00", "#99FF00", "#66FF00", "#33FF00"
]
transition_audio_path = "transition_beeps.mp3"

# --- Page Config ---
st.set_page_config(page_title="Circular Timer", page_icon="⏱", layout="centered")
st.title("🏋️ Exercise / Break Timer")

# --- Sidebar Inputs ---
exercise_time = st.number_input("Exercise time (seconds)", min_value=3, value=30, step=1)
break_time = st.number_input("Break time (seconds)", min_value=3, value=10, step=1)
num_cycles = st.number_input("Number of exercise cycles", min_value=1, value=5, step=1)

if "phase" not in st.session_state:
    st.session_state.phase = "Ready"
if "running" not in st.session_state:
    st.session_state.running = False
if "completed_cycles" not in st.session_state:
    st.session_state.completed_cycles = 0

# --- Audio loader ---
def load_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

transition_beep_b64 = load_audio_base64(transition_audio_path)

def play_transition_sound():
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{transition_beep_b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- Draw circular timer ---
def draw_circle(seconds_left, total_seconds, color):
    size = 300
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    draw.arc([10, 10, size-10, size-10], start=0, end=360, fill="#cccccc", width=20)
    angle = (seconds_left / total_seconds) * 360
    draw.arc([10, 10, size-10, size-10], start=90, end=90 - angle, fill=color, width=20)

    font = ImageFont.truetype(font_path, 100)
    text = str(seconds_left)
    w, h = draw.textsize(text, font=font)
    draw.text(((size-w)/2, (size-h)/2), text, font=font, fill="black")

    return img

# --- Draw colorful progress bar ---
def draw_progress_bar(current_cycle, total_cycles):
    bar_height = 50
    block_width = 40
    spacing = 5
    img_width = (block_width + spacing) * total_cycles - spacing
    img = Image.new("RGBA", (img_width, bar_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    for i in range(total_cycles):
        color = progress_colors[min(i, len(progress_colors)-1)] if i < current_cycle else "#dddddd"
        x0 = i * (block_width + spacing)
        draw.rounded_rectangle([x0, 0, x0 + block_width, bar_height], radius=10, fill=color)

    return img

placeholder_timer = st.empty()
placeholder_progress = st.empty()

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("▶ Start"):
        st.session_state.running = True
        st.session_state.completed_cycles = 0
with col2:
    if st.button("⏹ Stop"):
        st.session_state.running = False
        st.session_state.phase = "Ready"

# --- Main Loop ---
if st.session_state.running:
    for cycle in range(num_cycles):
        if not st.session_state.running:
            break

        # Exercise
        st.session_state.phase = "Exercise"
        for sec in range(exercise_time, 0, -1):
            if not st.session_state.running:
                break
            if sec == 4:
                play_transition_sound()
            img = draw_circle(sec, exercise_time, "#FF0000")
            placeholder_timer.image(img)
            placeholder_progress.image(draw_progress_bar(st.session_state.completed_cycles, num_cycles))
            time.sleep(1)

        # Break
        if st.session_state.running:
            st.session_state.phase = "Break"
            for sec in range(break_time, 0, -1):
                if not st.session_state.running:
                    break
                if sec == 4:
                    play_transition_sound()
                img = draw_circle(sec, break_time, "#007BFF")
                placeholder_timer.image(img)
                placeholder_progress.image(draw_progress_bar(st.session_state.completed_cycles, num_cycles))
                time.sleep(1)

        st.session_state.completed_cycles += 1
        placeholder_progress.image(draw_progress_bar(st.session_state.completed_cycles, num_cycles))

    st.success("✅ All cycles complete!")
    st.session_state.running = False
else:
    placeholder_timer.write(f"Status: **{st.session_state.phase}**")
    placeholder_progress.image(draw_progress_bar(st.session_state.completed_cycles, num_cycles))
