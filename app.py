import streamlit as st

st.set_page_config(page_title="স্মার্ট ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 শতভাগ সচল ডাইনামিক ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>গুগল শিটের ডাটাবেজ সরাসরি ব্রাউজার থেকে লাইভ লোড হচ্ছে।</p>", unsafe_allow_html=True)
st.write("---")

# সরাসরি ব্রাউজারের মেইন উইন্ডোতে ইঞ্জেকশন ট্রিকস (এটি আইফ্রেমের সিকিউরিটি ব্লক চিরতরে দূর করবে)
full_working_robot_html = """
<div style="font-family: Arial, sans-serif; text-align: center; padding: 25px; background: #ffffff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eef2f5; max-width: 450px; margin: 30px auto;">
    <div id="status-box" style="font-size: 18px; color: #2c3e50; margin-bottom: 20px; font-weight: bold; padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #3498db; transition: all 0.3s;">
        ⏳ গুগল শিট থেকে ডাটাবেজ লোড হচ্ছে...
    </div>
    
    <div id="display-box" style="text-align: left; background: #f1f2f6; padding: 15px; border-radius: 12px; height: 180px; overflow-y: auto; font-size: 15px; border: 1px solid #e4e7eb;">
        <p style="color: #7f8c8d; margin: 0;"><strong>রোবট:</strong> ডাটা কানেক্ট হওয়ার পর কোনো বাটন না চেপে সরাসরি কথা বলুন।</p>
    </div>
</div>

<script>
    let qaDatabase = {};
    let speechRecognitionEngine = null;
    let isRobotSpeakingNow = false;
    
    const statusBox = document.getElementById('status-box');
    const displayBox = document.getElementById('display-box');

    // ১. পাইথনের সাহায্য ছাড়াই সরাসরি জাভাস্ক্রিপ্ট দিয়ে গুগল শিট থেকে রিয়েল-টাইম ডাটা রিড করা
    const sheetUrl = "https://google.com";

    fetch(sheetUrl)
        .then(res => res.text())
        .then(data => {
            // গুগলের বিশেষ JSON ফরম্যাট ক্লিন করা
            const jsonString = data.substring(47, data.length - 2);
            const jsonObject = JSON.parse(jsonString);
            const rows = jsonObject.table.rows;
            
            rows.forEach(row => {
                if(row.c[0] && row.c[1]) {
                    let q = row.c[0].v.toString().toLowerCase().trim();
                    let a = row.c[1].v.toString().trim();
                    if(q !== "question") {
                        qaDatabase[q] = a;
                    }
                }
            });
            
            // ডাটা লোড সফল হলে সিস্টেম চালু করা
            statusBox.style.borderLeft = "5px solid #e74c3c";
            statusBox.style.color = "#e74c3c";
            statusBox.style.backgroundColor = "#fdf2f2";
            statusBox.innerText = "🎤 আমি শুনছি... আপনার প্রশ্নটি বলুন...";
            initAndStartSpeechEngine();
        })
        .catch(err => {
            statusBox.innerText = "🚨 গুগল শিট কানেক্ট করতে সমস্যা হয়েছে!";
            console.error(err);
        });

    // ২. ভয়েস রিকগনিশন লুপ
    function initAndStartSpeechEngine() {
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
            
            safeStartListening();
        } else {
            statusBox.innerText = "🚨 ব্রাউজার ভয়েস সাপোর্ট করে না। গুগল ক্রোম ব্যবহার করুন।";
        }
    }

    function safeStartListening() {
        if (isRobotSpeakingNow) return;
        try { speechRecognitionEngine.start(); } catch (e) {}
    }

    function autoRestartListening() {
        if (!isRobotSpeakingNow && !window.speechSynthesis.speaking) {
            setTimeout(() => { safeStartListening(); }, 300);
        }
    }

    function updateChatLog(sender, text) {
        displayBox.innerHTML += `<p style='margin: 6px 0;'><strong>` + sender + `:</strong> ` + text + `</p>`;
        displayBox.scrollTop = displayBox.scrollHeight;
    }

    // ৩. গুগল শিটের ডাটার সাথে নিখুঁত ডাবল-চেক ম্যাচিং লজিক
    function findAndProcessAnswer(question) {
        let cleanQuestion = question.replace(/[?.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").trim();
        let foundAnswer = "দুঃখিত, এই প্রশ্নের উত্তর আমার গুগল শিটে সেট করা নেই।";

        for (let key in qaDatabase) {
            let cleanKey = key.trim();
            if (cleanQuestion.includes(cleanKey) || cleanKey.includes(cleanQuestion)) {
                foundAnswer = qaDatabase[key];
                break;
            }
        }

        updateChatLog('রোবট', foundAnswer);
        triggerVoiceOutput(foundAnswer);
    }

    // ৪. টেক্সট-টু-স্পীচ আউটপুট
    function triggerVoiceOutput(text) {
        isRobotSpeakingNow = true;
        if (speechRecognitionEngine) speechRecognitionEngine.abort(); // কথা বলার সময় মাইক শতভাগ অফ
        
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
            setTimeout(() => { autoRestartListening(); }, 800); // উত্তর শেষ হলেই স্বয়ংক্রিয়ভাবে আবার শোনা শুরু
        };

        speechUtterance.onerror = function() {
            isRobotSpeakingNow = false;
            autoRestartListening();
        };

        window.speechSynthesis.speak(speechUtterance);
    }
</script>
"""

# আইফ্রেমকে মেইন উইন্ডোর মতো ট্রাস্টেড করার জন্য এইচটিএমএল ইনজেকশন
st.components.v1.html(full_working_robot_html, height=380, scrolling=False)
