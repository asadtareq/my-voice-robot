import streamlit as st
import pandas as pd
import json
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import time

st.set_page_config(page_title="স্মার্ট ডাইনামিক রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 ডাইনামিক ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>কোডে হাত না দিয়ে গুগল শিট থেকে প্রশ্ন-উত্তর আপডেট করুন</p>", unsafe_allow_html=True)
st.write("---")

# সরাসরি গুগল শিটের পাবলিক এক্সপোর্ট লিঙ্ক
CSV_URL = "https://google.com"

# গুগল শিট থেকে ডাটা রিড করা
try:
    df = pd.read_csv(CSV_URL, on_bad_lines='skip')
    df.columns = df.columns.astype(str).str.strip().str.lower()
    questions = df.iloc[:, 0].astype(str).str.lower().str.strip()
    answers = df.iloc[:, 1].astype(str).str.strip()
    qa_database = dict(zip(questions, answers))
except Exception as e:
    st.error(f"গুগল শিট থেকে ডাটা লোড করা যাচ্ছে না! সমস্যা: {e}")
    qa_database = {}

# ভয়েস প্লে করার ফাংশন
def speak_out(text):
    if any(c.isalpha() for c in text) and not any(0x0980 <= ord(c) <= 0x09FF for c in text):
        lang = 'en'
    else:
        lang = 'bn'
        
    tts = gTTS(text=text, lang=lang, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    audio_bytes = fp.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

# Streamlit-এর নিজস্ব অফিশিয়াল ভয়েস ইনপুট উইজেট (যা ব্রাউজার কখনো ব্লক করবে না)
st.subheader("🎤 মাইক্রোফোনে কথা বলুন")
audio_file = st.audio_input("কথা বলতে নিচের কালো মাইক আইকনে চাপুন")

if audio_file is not None:
    # অডিও প্রসেস করা
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    user_text = ""
    try:
        # প্রথমে বাংলা ডিক্টেশন ট্রাই করবে
        user_text = recognizer.recognize_google(audio_data, language="bn-BD").lower().strip()
    except:
        try:
            # বাংলা না হলে ইংরেজি ট্রাই করবে
            user_text = recognizer.recognize_google(audio_data, language="en-US").lower().strip()
        except:
            st.error("দুঃখিত, কথাটি স্পষ্ট বোঝা যায়নি।")
            
    if user_text:
        st.success(f"**আপনি বলেছেন:** {user_text}")
        
        # শিটের ডাটার সাথে মেলানো
        answer = "দুঃখিত, এই প্রশ্নের উত্তর আমার গুগল শিটে সেট করা নেই।"
        for key in qa_database:
            if key in user_text or user_text in key:
                answer = qa_database[key]
                break
                
        st.warning(f"**রোবট:** {answer}")
        
        # উত্তর মুখে বলা
        speak_out(answer)
        
        # কথা বলা শেষ করে ১.৫ সেকেন্ড পর স্বয়ংক্রিয়ভাবে অ্যাপ রিস্টার্ট হয়ে আবার শুনবে
        time.sleep(1.5)
        st.rerun()
