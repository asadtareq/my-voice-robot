import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from gtts import gTTS
import io
import base64

st.set_page_config(page_title="ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 ভয়েস টু ভয়েস টকিং রোবট</h2>", unsafe_allow_html=True)
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
    "how are you": "I am doing great, thank you!"
}

# টেক্সট থেকে ভয়েস তৈরি ও অটো-প্লে করার ফাংশন
def speak_out(text):
    lang = 'en' if any(c.isalpha() for c in text) else 'bn'
    tts = gTTS(text=text, lang=lang, slow=False)
    
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    audio_bytes = fp.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)

st.subheader("🎤 রোবটের সাথে কথা বলুন")
st.info("নিচের বাটনে ক্লিক করে কথা বলা শুরু করুন এবং কথা শেষ হলে আবার চাপুন।")

# মাইক্রোফোন রেকর্ডার উইজেট
audio = mic_recorder(
    start_prompt="🔴 রেকর্ড শুরু করুন",
    stop_prompt="🟢 রেকর্ড শেষ করুন",
    key='recorder'
)

if audio:
    # রেকর্ড করা অডিও ডেটা প্রসেস করা
    audio_bio = io.BytesIO(audio['bytes'])
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_bio) as source:
        audio_data = recognizer.record(source)
    
    try:
        # অডিও থেকে টেক্সট কনভার্ট করা (প্রথমে বাংলা, ব্যর্থ হলে ইংরেজি ট্রাই করবে)
        try:
            user_text = recognizer.recognize_google(audio_data, language="bn-BD").lower().strip()
        except:
            user_text = recognizer.recognize_google(audio_data, language="en-US").lower().strip()
            
        st.success(f"**আপনি বলেছেন:** {user_text}")
        
        # ডাটাবেজ থেকে উত্তর খোঁজা
        answer = "দুঃখিত, এই প্রশ্নের উত্তর আমার কোডে সেট করা নেই।"
        for key in qa_database:
            if key in user_text:
                answer = qa_database[key]
                break
                
        st.warning(f"**রোবট:** {answer}")
        
        # রোবটের উত্তর প্লে করা
        speak_out(answer)
        
    except sr.UnknownValueError:
        st.error("দুঃখিত, আপনার কথাটি স্পষ্ট বোঝা যায়নি। আবার চেষ্টা করুন।")
    except sr.RequestError:
        st.error("সার্ভার সমস্যা। অনুগ্রহ করে ইন্টারনেট কানেকশন চেক করুন।")
