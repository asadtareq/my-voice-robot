import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="স্মার্ট ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 নন-স্টপ ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>একবার অন করুন, তারপর অনবরত কথা বলতে থাকুন।</p>", unsafe_allow_html=True)
st.write("---")

# সম্পূর্ণ ভয়েস লুপটি হ্যান্ডেল করার জন্য কাস্টম এইচটিএমএল ও জাভাস্ক্রিপ্ট কোড
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
    // আপনার প্রশ্ন ও উত্তরের ডাটাবেজ
    const qaDatabase = {
        "হ্যালো": "হ্যালো! আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
        "তোমার নাম কি": "আমার নাম কথা বলা রোবট।",
        "কেমন আছো": "আমি খুব ভালো আছি, ধন্যবাদ! আপনি কেমন আছেন?",
        "তুমি কি করতে পারো": "আমি আপনার কথা শুনে সরাসরি মুখে উত্তর দিতে পারি।",
        "ধন্যবাদ": "আপনাকেও অনেক অনেক ধন্যবাদ!",
        "দিনাজপুর কি": "দিনাজপুর একটি জেলার নাম",
        "hello": "Hello! How can I help you?",
        "what is your name": "My name is Talking Robot.",
        "how are you": "I am doing great, thank you!",
        "fine": "That is wonderful to hear!"
    };

    let speechRecognitionEngine = null;
    let isSystemActive = false;
    let isRobotSpeakingNow = false;
    
    const actionBtn = document.getElementById('action-btn');
    const statusBox = document.getElementById('status-box');
    const displayBox = document.getElementById('display-box');

    // ব্রাউজারের ভয়েস ইঞ্জিন অ্যাক্টিভেট করা
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        speechRecognitionEngine = new SpeechRecognition();
        speechRecognitionEngine.continuous = false; 
        speechRecognitionEngine.interimResults = false;
        
        // বাংলা ও ইংরেজি দুই ভাষাই যাতে একসাথে ক্যাচ করতে পারে
        speechRecognitionEngine.lang = 'bn-BD'; 

        // মাইক যখন সক্রিয়ভাবে আপনার কথা শুনবে
        speechRecognitionEngine.onstart = function() {
            if (isSystemActive && !isRobotSpeakingNow) {
                statusBox.style.borderLeft = "5px solid #e74c3c";
                statusBox.style.color = "#e74c3c";
                statusBox.innerText = "🎤 আমি শুনছি... আপনার প্রশ্নটি বলুন...";
            }
        };

        // আপনি কথা বলার পর ব্রাউজার যখন টেক্সট উদ্ধার করবে
        speechRecognitionEngine.onresult = function(event) {
            let userSpeechText = event.results[0][0].transcript.toLowerCase().trim();
            if (userSpeechText.length > 0) {
                updateChatLog('আপনি', userSpeechText);
                findAndProcessAnswer(userSpeechText);
            }
        };

        // কোনো কথা না শুনলে বা এরর হলে স্বয়ংক্রিয়ভাবে আবার শোনা শুরু করবে (বারবার বাটন চাপার অবসান)
        speechRecognitionEngine.onerror = function() {
            autoRestartListening();
        };

        speechRecognitionEngine.onend = function() {
            autoRestartListening();
        };
    } else {
        statusBox.innerText = "🚨 আপনার ব্রাউজারটি ভয়েস সাপোর্ট করে না। গুগল ক্রোম ব্যবহার করুন।";
    }

    // অন/অফ বাটন কন্ট্রোল
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
        try {
            speechRecognitionEngine.start();
        } catch (e) {
            // অলরেডি রানিং থাকলে যাতে ক্র্যাশ না করে
        }
    }

    function autoRestartListening() {
        if (isSystemActive && !isRobotSpeakingNow && !window.speechSynthesis.speaking) {
            setTimeout(() => {
                safeStartListening();
            }, 400); // হালকা ডিলে টাইম যাতে সিস্টেম স্মুথ থাকে
        }
    }

    function updateChatLog(sender, text) {
        displayBox.innerHTML += `<p style='margin: 5px 0;'><strong>${sender}:</strong> ${text}</p>`;
        displayBox.scrollTop = displayBox.scrollHeight;
    }

    // প্রশ্ন ম্যাচিং ইঞ্জিন
    function findAndProcessAnswer(question) {
        // প্রশ্ন থেকে দাড়ি, কমা বা প্রশ্নবোধক চিহ্ন পরিষ্কার করা
        let cleanQuestion = question.replace(/[?.,\/#!$%\^&\*;:{}=\-_`~()]/g,"");
        let foundAnswer = "দুঃখিত, এই প্রশ্নের উত্তর আমার কোডে সেট করা নেই।";

        for (let key in qaDatabase) {
            if (cleanQuestion.includes(key) || key.includes(cleanQuestion)) {
                foundAnswer = qaDatabase[key];
                break;
            }
        }

        updateChatLog('রোবট', foundAnswer);
        triggerVoiceOutput(foundAnswer);
    }

    // নিখুঁত টেক্সট-টু-স্পীচ কথা বলা ফাংশন
    function triggerVoiceOutput(text) {
        isRobotSpeakingNow = true;
        if (speechRecognitionEngine) speechRecognitionEngine.abort(); // রোবট কথা বলার সময় মাইক শতভাগ অফ
        
        statusBox.style.borderLeft = "5px solid #2ecc71";
        statusBox.style.color = "#2ecc71";
        statusBox.innerText = "📢 রোবট মুখে উত্তর দিচ্ছে...";

        const speechUtterance = new SpeechSynthesisUtterance(text);
        
        // টেক্সটে ইংরেজি বর্ণ থাকলে ইংরেজি টোন, নয়তো বাংলাদেশি বাংলা টোন
        if(/[a-zA-Z]/.test(text)) {
            speechUtterance.lang = 'en-US';
        } else {
            speechUtterance.lang = 'bn-BD';
        }
        
        speechUtterance.rate = 1.0;

        // কথা বলা শেষ হওয়ার ঠিক ১ সেকেন্ড পর স্বয়ংক্রিয়ভাবে মাইক আবার চালু হবে
        speechUtterance.onend = function() {
            isRobotSpeakingNow = false;
            setTimeout(() => {
                autoRestartListening();
            }, 1000); 
        };

        speechUtterance.onerror = function() {
            isRobotSpeakingNow = false;
            autoRestartListening();
        };

        window.speechSynthesis.speak(speechUtterance);
    }
</script>
"""

# Streamlit-এর ভেতর কাস্টম এইচটিএমএল ইন্টারফেসটি রেন্ডার করা
components.html(custom_robot_html, height=350)
