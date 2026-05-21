import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

st.set_page_config(page_title="স্মার্ট ডাইনামিক রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 ডাইনামিক ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>কোডে হাত না দিয়ে গুগল শিট থেকে প্রশ্ন-উত্তর আপডেট করুন</p>", unsafe_allow_html=True)
st.write("---")

# সরাসরি গুগল শিটের পাবলিক এক্সপোর্ট লিঙ্ক
CSV_URL = "https://google.com"

# গুগল শিট থেকে ডাটা রিড করা এবং জাভা-স্ক্রিপ্টের জন্য ফরম্যাট করা
try:
    df = pd.read_csv(CSV_URL, on_bad_lines='skip')
    
    # কলামের সব নামকে ট্রিম এবং ছোট হাতের অক্ষরে রূপান্তর (যেমন: Question -> question)
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    # কলামের নাম সরাসরি ইনডেক্স দিয়ে ধরা (১ম কলাম প্রশ্ন, ২য় কলাম উত্তর) যাতে নাম ভুল হলেও ক্র্যাশ না করে
    questions = df.iloc[:, 0].astype(str).str.lower().str.strip()
    answers = df.iloc[:, 1].astype(str).str.strip()
    
    qa_dict = dict(zip(questions, answers))
    qa_json = json.dumps(qa_dict, ensure_ascii=False)
except Exception as e:
    st.error(f"গুগল শিট থেকে ডাটা লোড করা যাচ্ছে না! সমস্যা: {e}")
    qa_json = "{}"

# কাস্টম এইচটিএমএল ও জাভাস্ক্রিপ্ট কোড
custom_robot_html = """
<div style="font-family: Arial, sans-serif; text-align: center; padding: 20px; background: #ffffff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eef2f5; max-width: 450px; margin: auto;">
    <div id="status-box" style="font-size: 18px; color: #2c3e50; margin: 20px 0; font-weight: bold; padding: 12px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #3498db;">
        🤖 রোবট বর্তমানে বন্ধ আছে
    </div>
    <button id="action-btn" onclick="toggleRobotSystem()" style="background-color: #2ecc71; color: white; padding: 15px 40px; font-size: 18px; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; box-shadow: 0 5px 15px rgba(46, 204, 113, 0.3); transition: all 0.3s ease;">
        রোবট চালু করুন
    </button>
    
    <div id="display-box" style="margin-top: 25px; text-align: left; background: #f1f2f6; padding: 15px; border-radius: 12px; height: 160px; overflow-y: auto; font-size: 15px; border: 1px solid #e4e7eb;">
        <p style="color: #7f8c8d; margin: 0;"><strong>রোবট:</strong> কথা বলা শুরু করতে উপরের সবুজ বাটনে একবার চাপুন।</p>
    </div>
</div>

<script>
    const qaDatabase = """ + qa_json + """;

    let speechRecognitionEngine = null;
    let isSystemActive = false;
    let isRobotSpeakingNow = false;
    
    const actionBtn = document.getElementById('action-btn');
    const statusBox = document.getElementById('status-box');
    const displayBox = document.getElementById('display-box');

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        speechRecognitionEngine = new SpeechRecognition();
        speechRecognitionEngine.continuous = false; 
        speechRecognitionEngine.interimResults = false;
        speechRecognitionEngine.lang = 'bn-BD'; 

        speechRecognitionEngine.onstart = function() {
            if (isSystemActive && !isRobotSpeakingNow) {
                statusBox.style.borderLeft = "5px solid #e74c3c";
                statusBox.style.color = "#e74c3c";
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
    } else {
        statusBox.innerText = "🚨 ব্রাউজার ভয়েস সাপোর্ট করে না। গুগল ক্রোম ব্যবহার করুন।";
    }

    function toggleRobotSystem() {
        if (!isSystemActive) {
            isSystemActive = true;
            isRobotSpeakingNow = false;
            actionBtn.innerText = "রোবট বন্ধ করুন";
            actionBtn.style.backgroundColor = "#e74c3c";
            actionBtn.style.boxShadow = "0 5px 15px rgba(231, 76, 60, 0.3)";
            safeStartListening();
        } else {
            isSystemActive = false;
            isRobotSpeakingNow = false;
            actionBtn.innerText = "রোবট চালু করুন";
            actionBtn.style.backgroundColor = "#2ecc71";
            actionBtn.style.boxShadow = "0 5px 15px rgba(46, 204, 113, 0.3)";
            statusBox.style.borderLeft = "5px solid #3498db";
            statusBox.style.color = "#2c3e50";
            statusBox.innerText = "🤖 রোবট বর্তমানে বন্ধ আছে";
            if(speechRecognitionEngine) speechRecognitionEngine.abort();
            window.speechSynthesis.cancel();
        }
    }

    function safeStartListening() {
        if (!isSystemActive || isRobotSpeakingNow) return;
        try { speechRecognitionEngine.start(); } catch (e) {}
    }

    function autoRestartListening() {
        if (isSystemActive && !isRobotSpeakingNow && !window.speechSynthesis.speaking) {
            setTimeout(() => { safeStartListening(); }, 400);
        }
    }

    function updateChatLog(sender, text) {
        displayBox.innerHTML += `<p style='margin: 5px 0;'><strong>` + sender + `:</strong> ` + text + `</p>`;
        displayBox.scrollTop = displayBox.scrollHeight;
    }

    function findAndProcessAnswer(question) {
        let cleanQuestion = question.replace(/[?.,\/#!$%\^&\*;:{}=\-_`~()]/g,"");
        let foundAnswer = "দুঃখিত, এই প্রশ্নের উত্তর আমার গুগল শিটে সেট করা নেই।";

        for (let key in qaDatabase) {
            if (cleanQuestion.includes(key) || key.includes(cleanQuestion)) {
                foundAnswer = qaDatabase[key];
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
            setTimeout(() => { autoRestartListening(); }, 1000); 
        };

        speechUtterance.onerror = function() {
            isRobotSpeakingNow = false;
            autoRestartListening();
        };

        window.speechSynthesis.speak(speechUtterance);
    }
</script>
"""
components.html(custom_robot_html, height=350, scrolling=False, allow_output_interaction=True)

