import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="স্মার্ট ভয়েস রোবট", page_icon="🤖", layout="centered")

st.markdown("<h2 style='text-align: center;'>🤖 ডাইনামিক ভয়েস টু ভয়েস রোবট</h2>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: gray;'>গুগল শিট কানেক্টেড নন-স্টপ টকিং রোবট।</p>", unsafe_allow_html=True)
st.write("---")

# সরাসরি গুগল শিটের পাবলিক এক্সপোর্ট লিঙ্ক (ক্যাশ ছাড়া নতুন ডাটা টানার জন্য ট্রিকস)
CSV_URL = "https://google.com"

try:
    # গুগল শিট রিড করা
    df = pd.read_csv(CSV_URL, on_bad_lines='skip')
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    # ১ম কলাম প্রশ্ন, ২য় কলাম উত্তর ধরা হলো
    questions = df.iloc[:, 0].astype(str).str.lower().str.strip()
    answers = df.iloc[:, 1].astype(str).astype(str).str.strip()
    
    qa_dict = dict(zip(questions, answers))
    qa_json = json.dumps(qa_dict, ensure_ascii=False)
except Exception as e:
    st.error(f"গুগল শিট লোড এরর: {e}")
    qa_json = "{}"

# সম্পূর্ণ বাটন-মুক্ত ব্যাকগ্রাউন্ড লুপ কোড (যা ডিরেক্ট ক্রোম ব্রাউজারে রান করবে)
non_stop_robot_code = """
<div style="font-family: Arial, sans-serif; text-align: center; padding: 25px; background: #ffffff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eef2f5; max-width: 450px; margin: auto;">
    <div id="status-display" style="font-size: 18px; color: #e74c3c; margin-bottom: 20px; font-weight: bold; padding: 15px; background: #fdf2f2; border-radius: 10px; border-left: 5px solid #e74c3c; transition: all 0.3s;">
        🎤 আমি শুনছি... আপনার প্রশ্নটি বলুন...
    </div>
    
    <div id="chat-log" style="text-align: left; background: #f1f2f6; padding: 15px; border-radius: 12px; height: 180px; overflow-y: auto; font-size: 15px; border: 1px solid #e4e7eb;">
        <p style="color: #7f8c8d; margin: 0;"><strong>রোবট:</strong> পেজটি লোড হয়েছে। সরাসরি কথা বলা শুরু করুন (কোনো বাটন চাপতে হবে না)।</p>
    </div>
</div>

<script>
    // গুগল শিট থেকে আসা লাইভ ডাটাবেজ
    const qaDatabase = """ + qa_json + """;

    let recognition = null;
    let isSpeaking = false;
    
    const statusDisplay = document.getElementById('status-display');
    const chatLog = document.getElementById('chat-log');

    // স্পীচ রিকগনিশন ইনিশিয়াল করা
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false; 
        recognition.interimResults = false;
        recognition.lang = 'bn-BD'; 

        // অনবরত শোনার জন্য স্টার্ট ইভেন্ট
        recognition.onstart = function() {
            if (!isSpeaking) {
                statusDisplay.style.borderLeft = "5px solid #e74c3c";
                statusDisplay.style.color = "#e74c3c";
                statusDisplay.style.backgroundColor = "#fdf2f2";
                statusDisplay.innerText = "🎤 আমি শুনছি... আপনার প্রশ্নটি বলুন...";
            }
        };

        recognition.onresult = function(event) {
            let transcript = event.results[0][0].transcript.toLowerCase().trim();
            if (transcript.length > 0) {
                addLog('আপনি', transcript);
                processAnswer(transcript);
            }
        };

        // কথা বলা শেষ হলে বা সাইলেন্ট থাকলে অটোমেটিক লুপ রিস্টার্ট (বাটন চাপার ঝামেলা মুক্তি)
        recognition.onerror = function() { restartListening(); };
        recognition.onend = function() { restartListening(); };
        
        // প্রথমবার পেজ খোলার সাথে সাথে স্বয়ংক্রিয়ভাবে চালু হবে
        setTimeout(() => { recognition.start(); }, 1000);
    } else {
        statusDisplay.innerText = "🚨 গুগল ক্রোম ব্রাউজার ব্যবহার করুন।";
    }

    function restartListening() {
        if (!isSpeaking && !window.speechSynthesis.speaking) {
            try { recognition.start(); } catch (e) {}
        }
    }

    function addLog(sender, text) {
        chatLog.innerHTML += `<p style='margin: 8px 0;'><strong>` + sender + `:</strong> ` + text + `</p>`;
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function processAnswer(question) {
        // প্রশ্ন থেকে বিরামচিহ্ন পরিষ্কার করা
        let cleanQ = question.replace(/[?.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").trim();
        let answer = "দুঃখিত, এই প্রশ্নের উত্তর আমার গুগল শিটে সেট করা নেই।";

        // শিটের ডাটার সাথে নিখুঁত ম্যাচিং লজিক
        for (let key in qaDatabase) {
            let cleanKey = key.trim();
            if (cleanQ.includes(cleanKey) || cleanKey.includes(cleanQ)) {
                answer = qaDatabase[cleanKey];
                break;
            }
        }

        addLog('রোবট', answer);
        speak(answer);
    }

    function speak(text) {
        isSpeaking = true;
        try { recognition.abort(); } catch (e) {} // কথা বলার সময় মাইক বন্ধ
        
        statusDisplay.style.borderLeft = "5px solid #2ecc71";
        statusDisplay.style.color = "#2ecc71";
        statusDisplay.style.backgroundColor = "#f2fdf5";
        statusDisplay.innerText = "📢 রোবট মুখে উত্তর দিচ্ছে...";

        const utterance = new SpeechSynthesisUtterance(text);
        
        // ভাষা নির্ধারণ
        if(/[a-zA-Z]/.test(text)) {
            utterance.lang = 'en-US';
        } else {
            utterance.lang = 'bn-BD';
        }
        utterance.rate = 1.0;

        utterance.onend = function() {
            isSpeaking = false;
            setTimeout(() => { restartListening(); }, 800); // উত্তর শেষ করে আবার শোনা শুরু
        };

        utterance.onerror = function() {
            isSpeaking = false;
            restartListening();
        };

        window.speechSynthesis.speak(utterance);
    }
</script>
"""

# Streamlit-এর মূল বডিতে সরাসরি স্ক্রিপ্ট রান করানো হলো (আইফ্রেমের পারমিশন ব্লক এড়াতে)
st.components.v1.html(non_stop_robot_code, height=360, scrolling=False)
