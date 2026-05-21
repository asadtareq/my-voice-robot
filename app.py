import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import time

st.set_page_config(page_title="অটো-লুপ ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 অটো-লুপ ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("---")

# প্রশ্ন ও উত্তরের ডাটাবেজ
qa_database = {
    "হ্যালো": "হ্যালো! আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
    "তোমার নাম কি": "আমার নাম কথা বলা রোবট।",
    "কেমন আছো": "আমি খুব ভালো আছি, ধন্যবাদ! আপনি কেমন আছেন?",
    "তুমি কি করতে পারো": "আমি আপনার ভয়েস শুনে উত্তর দিতে পারি।",
    "ধন্যবাদ": "আপনাকেও অনেক ধন্যবাদ!",
    "hello": "Hello! How can I help you?",
    "what is your name": "My name is Talking Robot.",
    "how are you": "I am doing great, thank you!",
    "fine": "That is great to hear!"
}

if 'bot_speaking' not in st.session_state:
    st.session_state.bot_speaking = False

# নিখুঁত বাংলা ও ইংরেজি ভয়েস ফাংশন
def speak_out(text):
    st.session_state.bot_speaking = True
    
    # উত্তরটিতে ইংরেজি অক্ষর থাকলে ইংরেজি ভয়েস, নয়তো বাংলা ভয়েস
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
    
    time.sleep(2.5) # রোবটকে কথা শেষ করার পর্যাপ্ত সময় দেওয়া
    st.session_state.bot_speaking = False

st.subheader("🎤 রোবটের সাথে কথা বলুন")
st.info("একবার নিচের বাটনে ক্লিক করে কথা বলুন।")

# মাইক্রোফোন রেকর্ডার উইজেট
audio = mic_recorder(
    start_prompt="🔴 রোবট চালু করুন (একবার চাপুন)",
    stop_prompt="🟢 কথা শেষ করুন",
    format="wav",
    key='recorder'
)

if audio and not st.session_state.bot_speaking:
    audio_bio = io.BytesIO(audio['bytes'])
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_bio) as source:
        # চারপাশের নয়েজ অ্যাডজাস্ট করা
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        audio_data = recognizer.record(source)
    
    user_text = ""
    
    # স্মার্ট ডাবল-চেক লজিক: প্রথমে বাংলা ট্রাই করবে, কোনো ইংরেজি শব্দ থাকলে তা ইংরেজিতে ক্যাচ করবে
    try:
        # বাংলা ভাষার জন্য প্রথম ট্রাই
        user_text = recognizer.recognize_google(audio_data, language="bn-BD").lower().strip()
    except:
        try:
            # বাংলা না বুঝলে ইংরেজি হিসেবে ট্রাই করবে
            user_text = recognizer.recognize_google(audio_data, language="en-US").lower().strip()
        except sr.UnknownValueError:
            st.error("দুঃখিত, আপনার কথাটি স্পষ্ট বোঝা যায়নি। আবার চেষ্টা করুন।")
        except sr.RequestError:
            st.error("সার্ভার সমস্যা।")

    if user_text:
        st.success(f"**আপনি বলেছেন:** {user_text}")
        
        # ডাটাবেজ থেকে নিখুঁতভাবে উত্তর মেলানোর লজিক
        answer = "দুঃখিত, এই প্রশ্নের উত্তর আমার কোডে সেট করা নেই।"
        
        # ম্যাচিং সিস্টেম আরও উন্নত করা হলো
        for key in qa_database:
            if key in user_text or user_text in key:
                answer = qa_database[key]
                break
                
        st.warning(f"**রোবট:** {answer}")
        
        # উত্তরটি মুখে বলা
        speak_out(answer)
        
        # স্বয়ংক্রিয়ভাবে আবার মাইক অন করার জাভাস্ক্রিপ্ট ট্রিকস
        st.markdown("""
            <script>
                setTimeout(function(){
                    window.parent.document.querySelector('.stButton button').click();
                }, 1200);
            </script>
        """, unsafe_allow_html=True)
