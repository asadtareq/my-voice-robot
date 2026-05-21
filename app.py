import streamlit as st
import json

st.set_page_config(page_title="নন-স্টপ ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 নন-স্টপ ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>প্রশ্ন-উত্তর কোডের ভেতরেই সেট করা আছে। একবার অন করে কথা বলতে থাকুন।</p>", unsafe_allow_html=True)
st.write("---")

# আপনার প্রশ্ন ও উত্তর ডাটাবেজ
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

# জাভাস্ক্রিপ্টের জন্য ডাটাবেজটিকে রেডি করা
qa_json = json.dumps(qa_database, ensure_ascii=False)

# মূল ইন্টারফেস এবং সচল লুপ কোড (কোনো base64 এনকোডিং ছাড়া সরাসরি ফিক্সড কোড)
robot_html_code = """
<div style="font-family: Arial, sans-serif; text-align: center; padding: 25px; background: #ffffff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eef2f5; max-width: 450px; margin: auto;">
    <div id="status-display" style="font-size: 18px; color: #2c3e50; margin-bottom: 20px; font-weight: bold; padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #3498db; transition: all 0.3s;">
        🤖 রোবট বর্তমানে বন্ধ আছে
    </div>
    <button id="main-action-btn" onclick="startRobotSystem()" style="background-color: #2ecc71; color: white; padding: 15px 40px; font-size: 18px; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; box-shadow: 0 5px 15px rgba(46, 204, 113, 0.3); transition: all 0.3s ease;">
        রোবট চালু করুন
    </button>
    
    <div id="chat-history-box" style="margin-top: 25px; text-align: left; background: #f1f2f6; padding: 15px; border-radius: 12px; height: 160px; overflow-y: auto; font-size: 15px; border: 1px solid #e4e7eb;">
        <p style="color: #7f8c8d; margin: 0;"><strong>রোবট:</strong> কথা বলা শুরু করতে উপরের সবুজ বাটনে একবার চাপুন।</p>
    </div>
</div>

<script>
    const robotQAData = """ + qa_json + """;

    let speechEngine = null;
    let isSystemRunning = false;
    let isRobotTalking = false;
    
    const actionBtn = document.getElementById('main-action-btn');
    const statusDisplay = document.getElementById('status-display');
    const chatHistoryBox = document.getElementById('chat-history-box');

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        speechEngine = new SpeechRecognition();
        speechEngine.continuous = false; 
        speechEngine.interimResults = false;
        speechEngine.lang = 'bn-BD'; 

        speechEngine.onstart = function() {
            if (isSystemRunning && !isRobotTalking) {
                statusDisplay.style.borderLeft = "5px solid #e74c3c";
                statusDisplay.style.color = "#e74c3c";
                statusDisplay.style.backgroundColor = "#fdf2f2";
                statusDisplay.innerText = "🎤 আমি শুনছি... আপনার প্রশ্নটি বলুন...";
            }
        };

        speechEngine.onresult = function(event) {
            let capturedText = event.results.transcript.toLowerCase().trim();
            if (capturedText.length > 0) {
                printChatLog('আপনি', capturedText);
                matchQuestionAndReply(capturedText);
            }
        };

        speechEngine.onerror = function() { triggerContinuousListen(); };
        speechEngine.onend = function() { triggerContinuousListen(); };
    } else {
        statusDisplay.innerText = "🚨 আপনার ব্রাউজারটি ভয়েস সাপোর্ট করে না। গুগল ক্রোম ব্যবহার করুন।";
    }

    function startRobotSystem() {
        if (!isSystemRunning) {
            isSystemRunning = true;
            isRobotTalking = false;
            actionBtn.innerText = "রোবট বন্ধ করুন";
            actionBtn.style.backgroundColor = "#e74c3c";
            actionBtn.style.boxShadow = "0 5px 15px rgba(231, 76, 60, 0.3)";
            executeListening();
        } else {
            isSystemRunning = false;
            isRobotTalking = false;
            actionBtn.innerText = "রোবট চালু করুন";
            actionBtn.style.backgroundColor = "#2ecc71";
            actionBtn.style.boxShadow = "0 5px 15px rgba(46, 204, 113, 0.3)";
            statusDisplay.style.borderLeft = "5px solid #3498db";
            statusDisplay.style.color = "#2c3e50";
            statusDisplay.style.backgroundColor = "#f8f9fa";
            statusDisplay.innerText = "🤖 রোবট বর্তমানে বন্ধ আছে";
            if(speechEngine) speechEngine.abort();
            window.speechSynthesis.cancel();
        }
    }

    function executeListening() {
        if (!isSystemRunning || isRobotTalking) return;
        try { speechEngine.start(); } catch (e) {}
    }

    function triggerContinuousListen() {
        if (isSystemRunning && !isRobotTalking && !window.speechSynthesis.speaking) {
            setTimeout(() => { executeListening(); }, 400);
        }
    }

    function printChatLog(sender, text) {
        chatHistoryBox.innerHTML += `<p style='margin: 5px 0;'><strong>` + sender + `:</strong> ` + text + `</p>`;
        chatHistoryBox.scrollTop = chatHistoryBox.scrollHeight;
    }

    function matchQuestionAndReply(question) {
        let cleanQ = question.replace(/[?.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").trim();
        let targetReply = "দুঃখিত, এই প্রশ্নের উত্তর আমার কোডে সেট করা নেই।";

        for (let key in robotQAData) {
            let cleanKey = key.trim();
            if (cleanQ.includes(cleanKey) || cleanKey.includes(cleanQ)) {
                targetReply = robotQAData[cleanKey];
                break;
            }
        }

        printChatLog('রোবট', targetReply);
        generateVoiceAudio(targetReply);
    }

    function generateVoiceAudio(text) {
        isRobotTalking = true;
        if (speechEngine) speechEngine.abort(); 
        
        statusDisplay.style.borderLeft = "5px solid #2ecc71";
        statusDisplay.style.color = "#2ecc71";
        statusDisplay.style.backgroundColor = "#f2fdf5";
        statusDisplay.innerText = "📢 রোবট মুখে উত্তর দিচ্ছে...";

        const speechUtterance = new SpeechSynthesisUtterance(text);
        
        if(/[a-zA-Z]/.test(text)) {
            speechUtterance.lang = 'en-US';
        } else {
            speechUtterance.lang = 'bn-BD';
        }
        
        speechUtterance.rate = 1.0;

        speechUtterance.onend = function() {
            isRobotTalking = false;
            setTimeout(() => { triggerContinuousListen(); }, 600); 
        };

        speechUtterance.onerror = function() {
            isRobotTalking = false;
            triggerContinuousListen();
        };

        window.speechSynthesis.speak(speechUtterance);
    }
</script>
"""

# সরাসরি অফিশিয়াল কম্পোনেন্ট দিয়ে কোনো প্রকার এনকোডিং ছাড়া রেন্ডার করা হলো
st.components.v1.html(robot_html_code, height=390, scrolling=False)
