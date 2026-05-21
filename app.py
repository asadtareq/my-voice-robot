import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import time

st.set_page_config(page_title="নন-স্টপ ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 শতভাগ সচল ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("---")

# কোডের ভেতরের ডাটাবেজ (এখানে আপনি প্রশ্ন-উত্তর পরিবর্তন করতে পারবেন)
qa_database = {
    "হ্যালো": "হ্যালো! আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
    "তোমার নাম কি": "আমার নাম কথা বলা রোবট।",
    "কেমন আছো": "আমি খুব ভালো আছি, ধন্যবাদ! আপনি কেমন আছেন?",
    "দিনাজপুর কি": "দিনাজপুর বাংলাদেশের একটি বিখ্যাত জেলা। দিনাজপুর লিচু ও কাটারিভোগ চালের জন্য বিখ্যাত।",
    "ধন্যবাদ": "আপনাকেও অনেক অনেক ধন্যবাদ!",
    "hello": "Hello! How can I help you?",
    "what is your name": "My name is Talking Robot.",
    "how are you": "I am doing great, thank you!"
}

# ফোর্সড অডিও প্লেয়ার ফাংশন (যা ক্লাউড সিকিউরিটি বাইপাস করবে)
def force_speak(text):
    lang = 'en' if (any(c.isalpha() for c in text) and not any(0x0980 <= ord(c) <= 0x09FF for c in text)) else 'bn'
    tts = gTTS(text=text, lang=lang, slow=False)
    
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_bytes = fp.read()
    
    # অডিও ফাইলটিকে বেস-৬৪ এ রূপান্তর করে ব্রাউজারের স্পিকারে পুশ করা
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

# সেশন স্টেট (অটোমেটিক লুপ চালু রাখার জন্য)
if 'listening' not in st.session_state:
    st.session_state.listening = True

st.subheader("🎤 মাইক্রোফোনে কথা বলুন")

# Streamlit-এর নিজস্ব অফিশিয়াল ইনপুট (যা ব্রাউজার কখনো ব্লক করে না)
audio_file = st.audio_input("কথা বলতে নিচের কালো মাইক আইকনে চাপুন", key="my_mic")

if audio_file is not None and st.session_state.listening:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    user_text = ""
    try:
        # প্রথমে বাংলা হিসেবে চেক করবে
        user_text = recognizer.recognize_google(audio_data, language="bn-BD").lower().strip()
    except:
        try:
            # বাংলা না বুঝলে ইংরেজি চেক করবে
            user_text = recognizer.recognize_google(audio_data, language="en-US").lower().strip()
        except:
            st.error("কথাটি স্পষ্ট নয়। আবার চেষ্টা করুন।")
            
    if user_text:
        st.success(f"**আপনি বলেছেন:** {user_text}")
        
        # ডাটা ম্যাচিং
        answer = "দুঃখিত, এই প্রশ্নের উত্তর আমার কোডে সেট করা নেই।"
        for key in qa_database:
            if key in user_text or user_text in key:
                answer = qa_database[key]
                break
                
        st.warning(f"**রোবট:** {answer}")
        
        # স্পিকারে আওয়াজ দেওয়া
        force_speak(answer)
        
        # ২ সেকেন্ড অপেক্ষা করে স্বয়ংক্রিয়ভাবে আবার মাইক রেডি করা (অটো-লুপ)
        time.sleep(2.0)
        st.rerun()
