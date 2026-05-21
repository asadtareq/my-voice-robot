import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import time

st.set_page_config(page_title="অফলাইন ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 নন-স্টপ ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>প্রশ্ন-উত্তর কোডের ভেতরেই সেট করা আছে।</p>", unsafe_allow_html=True)
st.write("---")

# 🔴 এখানে আপনার ইচ্ছেমতো প্রশ্ন ও উত্তর পরিবর্তন বা যোগ করতে পারবেন 🔴
qa_database = {
    "হ্যালো": "হ্যালো! আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
    "তোমার নাম কি": "আমার নাম কথা বলা রোবট।",
    "কেমন আছো": "আমি খুব ভালো আছি, ধন্যবাদ! আপনি কেমন আছেন?",
    "দিনাজপুর কি": "দিনাজপুর বাংলাদেশের একটি বিখ্যাত জেলা। দিনাজপুর লিচু ও কাটারিভোগ চালের জন্য বিখ্যাত।",
    "তুমি কি করতে পারো": "আমি আপনার কথা শুনে সরাসরি মুখে উত্তর দিতে পারি।",
    "ধন্যবাদ": "আপনাকেও অনেক অনেক ধন্যবাদ!",
    "hello": "Hello! How can I help you?",
    "what is your name": "My name is Talking Robot.",
    "how are you": "I am doing great, thank you!"
}

# খাঁটি বাংলা ও ইংরেজি ভয়েস আউটপুট ফাংশন
def speak_out(text):
    # লেখাটিতে ইংরেজি বর্ণমালা থাকলে ইংরেজি ভয়েস, নতুবা নিখুঁত বাংলা ভয়েস
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
    
    # ব্রাউজারে সরাসরি অডিও ফাইলটি প্লে করার অফিশিয়াল মেকানিজম
    audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

st.subheader("🎤 রোবট সচল আছে, কথা বলুন")

# Streamlit-এর অফিশিয়াল অলওয়েজ-অন ভয়েস উইজেট (যা ব্রাউজার কখনো ব্লক করবে না)
audio_file = st.audio_input("কথা বলতে নিচের মাইক আইকনে ক্লিক করুন")

if audio_file is not None:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    user_text = ""
    try:
        # প্রথমে বাংলা হিসেবে ধরার চেষ্টা করবে
        user_text = recognizer.recognize_google(audio_data, language="bn-BD").lower().strip()
    except:
        try:
            # বাংলা না বুঝলে ইংরেজি হিসেবে ট্রাই করবে
            user_text = recognizer.recognize_google(audio_data, language="en-US").lower().strip()
        except:
            st.error("দুঃখিত, কথাটি স্পষ্ট নয়। দয়া করে আবার বলুন।")
            
    if user_text:
        st.success(f"**আপনি বলেছেন:** {user_text}")
        
        # কোডের ভেতরের ডাটাবেজ থেকে উত্তর মেলানো
        answer = "দুঃখিত, এই প্রশ্নের উত্তর আমার কোডে সেট করা নেই।"
        for key in qa_database:
            if key in user_text or user_text in key:
                answer = qa_database[key]
                break
                
        st.warning(f"**রোবট:** {answer}")
        
        # উত্তর মুখে বলা
        speak_out(answer)
        
        # কথা বলা শেষ করে ২ সেকেন্ড পর স্বয়ংক্রিয়ভাবে অ্যাপ রিস্টার্ট হয়ে আবার শুনবে (বারবার অন অফ করা লাগবে না)
        time.sleep(2.0)
        st.rerun()
