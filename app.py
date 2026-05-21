import streamlit as st
import json

st.set_page_config(page_title="অফলাইন ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 নন-স্টপ ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>প্রশ্ন-উত্তর কোডের ভেতরেই সেট করা আছে।</p>", unsafe_allow_html=True)
st.write("---")

# 🔴 এখানে আপনার ইচ্ছেমতো প্রশ্ন ও উত্তর পরিবর্তন বা যোগ করতে পারবেন 🔴
# (মনে রাখবেন: ইংরেজি প্রশ্নগুলো সবসময় ছোট হাতের অক্ষরে লিখবেন)
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

# জাভাস্ক্রিপ্টের জন্য ডাটাবেজটিকে রেডি করা
qa_json = json.dumps(qa_database, ensure_ascii=False)

# মূল বাটন-লুপ এবং ব্রাউজার লেভেল ভয়েস কোড
custom_robot_html = """
<div style="font-family: Arial, sans-serif; text-align: center; padding: 25px; background: #ffffff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eef2f5; max-width: 450px; margin: auto;">
    <div id="status-box" style="font-size: 18px; color: #2c3e50; margin: 20px 0; font-weight: bold; padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #3498db; transition: all 0.3s;">
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
    // কোড থেকে সরাসরি আসা ডাটাবেজ
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

        // কোনো কথা না শুনলে বা এরর হলে বাটন না টিপেই অটো রিস্টার্ট হবে
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
            statusBox.style.backgroundColor = "#f8f9fa";
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
        let cleanQuestion = question.replace(/[?.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").trim();
        let foundAnswer = "দুঃখিত, এই প্রশ্নের উত্তর আমার কোডে সেট করা নেই।";

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
        if (speechRecognitionEngine) speechRecognitionEngine.abort(); // কথা বলার সময় মাইক মিউট
        
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
            setTimeout(() => { autoRestartListening(); }, 800); // উত্তর শেষ করে বাটন ছাড়াই আবার শোনা শুরু
        };

        speechUtterance.onerror = function() {
            isRobotSpeakingNow = false;
            autoRestartListening();
        };

        window.speechSynthesis.speak(speechUtterance);
    }
</script>
"""

# আইফ্রেমকে সরাসরি মেইন উইন্ডোর মাইক্রোফোন পারমিশন পাস করা হলো
import base64
b64_code = base64.b64encode(custom_robot_html.encode('utf-8')).decode('utf-8')
iframe_link = f'<iframe src="data:text/html;base64,{b64_code}" height="380" width="100%" style="border:none;" allow="microphone"></iframe>'

st.markdown(iframe_link, unsafe_allow_html=True)
