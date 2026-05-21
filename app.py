import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="স্মার্ট ডাইনামিক রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 শতভাগ সচল ডাইনামিক ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>গুগল শিটের ডাটাবেজ সরাসরি ব্রাউজার থেকে লাইভ লোড হচ্ছে।</p>", unsafe_allow_html=True)
st.write("---")

# সরাসরি গুগল শিটের পাবলিক এক্সপোর্ট ইউআরএল
CSV_URL = "https://google.com"

# পাইথন দিয়ে সেফলি ডাটা রিড করা এবং ব্ল্যাঙ্ক এরর দূর করা
try:
    df = pd.read_csv(CSV_URL, on_bad_lines='skip')
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    # ইনডেক্স ভিত্তিক ডাটা কালেকশন (যাতে কলামের নামের বানান ভুল হলেও ডাটা মিস না হয়)
    questions = df.iloc[:, 0].astype(str).str.lower().str.strip()
    answers = df.iloc[:, 1].astype(str).str.strip()
    
    # ডাটা ক্লিন করে ডিকশনারিতে রূপান্তর
    qa_dict = {}
    for q, a in zip(questions, answers):
        if q and q != "nan" and q != "question":
            qa_dict[q] = a
            
    qa_json = json.dumps(qa_dict, ensure_ascii=False)
except Exception as e:
    st.error(f"গুগল শিট লোড এরর: {e}")
    qa_json = "{}"

# বাটন-মুক্ত ব্যাকগ্রাউন্ড লাইভ ভয়েস লুপ কোড
custom_robot_html = """
<div style="font-family: Arial, sans-serif; text-align: center; padding: 25px; background: #ffffff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eef2f5; max-width: 450px; margin: auto;">
    <div id="status-box" style="font-size: 18px; color: #e74c3c; margin-bottom: 20px; font-weight: bold; padding: 15px; background: #fdf2f2; border-radius: 10px; border-left: 5px solid #e74c3c;">
        🎤 আমি শুনছি... আপনার প্রশ্নটি বলুন...
    </div>
    
    <div id="display-box" style="text-align: left; background: #f1f2f6; padding: 15px; border-radius: 12px; height: 180px; overflow-y: auto; font-size: 15px; border: 1px solid #e4e7eb;">
        <p style="color: #7f8c8d; margin: 0;"><strong>রোবট:</strong> কোনো বাটন না চেপে সরাসরি কথা বলুন।</p>
    </div>
</div>

<script>
    // পাইথন থেকে সফলভাবে পাস হওয়া ডাটাবেজ
    const qaDatabase = """ + qa_json + """;

    let speechRecognitionEngine = null;
    let isRobotSpeakingNow = false;
    
    const statusBox = document.getElementById('status-box');
    const displayBox = document.getElementById('display-box');

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        speechRecognitionEngine = new SpeechRecognition();
        speechRecognitionEngine.continuous = false; 
        speechRecognitionEngine.interimResults = false;
        speechRecognitionEngine.lang = 'bn-BD'; 

        speechRecognitionEngine.onstart = function() {
            if (!isRobotSpeakingNow) {
                statusBox.style.borderLeft = "5px solid #e74c3c";
                statusBox.style.color = "#e74c3c";
                statusBox.style.backgroundColor = "#fdf2f2";
                statusBox.innerText = "🎤 আমি শুনছি... আপনার প্রশ্নটি বলুন...";
            }
        };

        speechRecognitionEngine.onresult = function(event) {
            let userSpeechText = event.results.transcript.toLowerCase().trim();
            if (userSpeechText.length > 0) {
                updateChatLog('আপনি', userSpeechText);
                findAndProcessAnswer(userSpeechText);
            }
        };

        speechRecognitionEngine.onerror = function() { autoRestartListening(); };
        speechRecognitionEngine.onend = function() { autoRestartListening(); };
        
        // ১ সেকেন্ডের মধ্যে স্বয়ংক্রিয়ভাবে ভয়েস রিকগনিশন চালু করা
        setTimeout(() => { safeStartListening(); }, 1000);
    } else {
        statusBox.innerText = "🚨 ব্রাউজার ভয়েস সাপোর্ট করে না। গুগল ক্রোম ব্যবহার করুন।";
    }

    function safeStartListening() {
        if (isRobotSpeakingNow) return;
        try { speechRecognitionEngine.start(); } catch (e) {}
    }

    function autoRestartListening() {
        if (!isRobotSpeakingNow && !window.speechSynthesis.speaking) {
            setTimeout(() => { safeStartListening(); }, 400);
        }
    }

    function updateChatLog(sender, text) {
        displayBox.innerHTML += `<p style='margin: 6px 0;'><strong>` + sender + `:</strong> ` + text + `</p>`;
        displayBox.scrollTop = displayBox.scrollHeight;
    }

    function findAndProcessAnswer(question) {
        let cleanQuestion = question.replace(/[?.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").trim();
        let foundAnswer = "দুঃখিত, এই প্রশ্নের উত্তর আমার গুগল শিটে সেট করা নেই।";

        for (let key in qaDatabase) {
            let cleanKey = key.trim();
            if (cleanQuestion.includes(cleanKey) || cleanKey.includes(cleanQuestion)) {
                foundAnswer = qaDatabase[cleanKey];
                break;
            }
        }

        updateChatLog('রোবট', foundAnswer);
        triggerVoiceOutput(foundAnswer);
    }

    function triggerVoiceOutput(text) {
        isRobotSpeakingNow = true;
        if (speechRecognitionEngine) speechRecognitionEngine.abort(); 
        
        statusBox.style.borderLeft = "5px solid #2ecc71";
        statusBox.style.color = "#2ecc71";
        statusBox.style.backgroundColor = "#f2fdf5";
        statusBox.innerText = "📢 রোবট মুখে উত্তর দিচ্ছে...";

        const speechUtterance = new SpeechSynthesisUtterance(text);
        
        if(/[a-zA-Z]/.test(text)) {
            speechUtterance.lang = 'en-US';
        } else {
            speechUtterance.lang = 'bn-BD';
        }
        
        speechUtterance.rate = 1.0;

        speechUtterance.onend = function() {
            isRobotSpeakingNow = false;
            setTimeout(() => { autoRestartListening(); }, 800); 
        };

        speechUtterance.onerror = function() {
            isRobotSpeakingNow = false;
            autoRestartListening();
        };

        window.speechSynthesis.speak(speechUtterance);
    }
</script>
"""

# আইফ্রেম ছাড়াই সরাসরি ইন্টারফেসটি জেনারেট করা হলো
st.components.v1.html(custom_robot_html, height=360, scrolling=False)
