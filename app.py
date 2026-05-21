import streamlit as st
import pandas as pd
import io
import base64
import time
from google.protobuf.json_format import MessageToDict

st.set_page_config(page_title="স্মার্ট ডাইনামিক রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 নন-স্টপ ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>গুগল শিট কানেক্টেড টকিং রোবট।</p>", unsafe_allow_html=True)
st.write("---")

# ১. সরাসরি গুগল শিটের পাবলিক এক্সপোর্ট লিঙ্ক থেকে ডাটা রিড করা
CSV_URL = "https://google.com"

try:
    df = pd.read_csv(CSV_URL, on_bad_lines='skip')
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    # ১ম কলাম প্রশ্ন, ২য় কলাম উত্তর ধরা হলো
    questions = df.iloc[:, 0].astype(str).str.lower().str.strip()
    answers = df.iloc[:, 1].astype(str).str.strip()
    qa_database = dict(zip(questions, answers))
except Exception as e:
    st.error(f"গুগল শিট লোড এরর: {e}")
    qa_database = {}

# ২. টেক্সট থেকে খাঁটি বাংলা/ইংরেজি ভয়েস প্লে করার ফাংশন
def speak_out(text):
    from gtts import gTTS
    lang = 'en' if (any(c.isalpha() for c in text) and not any(0x0980 <= ord(c) <= 0x09FF for c in text)) else 'bn'
    tts = gTTS(text=text, lang=lang, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_bytes = fp.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

# ৩. Streamlit-এর নিজস্ব অফিশিয়াল অলওয়েজ-অন ভয়েস রিকগনিশন (যা ব্রাউজার কখনো ব্লক করবে না)
st.subheader("🎤 রোবট সচল আছে, কথা বলুন:")
audio_file = st.audio_input("কথা বলতে নিচের মাইক আইকনে ক্লিক করুন")

if audio_file is not None:
    import speech_recognition as sr
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
        
        # ৪. গুগল শিটের ডাটার সাথে নিখুঁতভাবে প্রশ্ন মেলানো
        answer = "দুঃখিত, এই প্রশ্নের উত্তর আমার গুগল শিটে সেট করা নেই।"
        for key in qa_database:
            if str(key) in user_text or user_text in str(key):
                answer = qa_database[key]
                break
                
        st.warning(f"**রোবট:** {answer}")
        
        # ৫. উত্তর মুখে বলা
        speak_out(answer)
        
        # ৬. স্বয়ংক্রিয়ভাবে আবার শোনার লুপ তৈরি করা (টাইম ডিলেসহ)
        time.sleep(2.5)
        st.rerun()
