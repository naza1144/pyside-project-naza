import streamlit as st
import os
import json
from ollama_service import get_ollama_response

# URLs หรือ Path ของรูปโปรไฟล์
USER_AVATAR = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTo9Mw4GhrGCmoZPMCedud0jCIyEGRhB6OIwQ&s"
AI_AVATAR = "https://tr.rbxcdn.com/180DAY-a0a46bc4bb969aabc6133811ec8ff505/420/420/LayeredAccessory/Webp/noFilter"

# CSS + JavaScript สำหรับ Animation ของ Title
st.markdown(f"""
    <style>
        .fade-out {{
            animation: fadeUp 1s forwards;
        }}

        @keyframes fadeUp {{
            0% {{ opacity: 1; transform: translateY(0px); }}
            100% {{ opacity: 0; transform: translateY(-50px); }}
        }}
        
        .chat-container {{ display: flex; flex-direction: column; gap: 10px; }}
        .message-container {{ display: flex; align-items: center; margin-bottom: 10px; }}
        .user-message {{ background-color: #504f4f; color: white; padding: 10px 15px; border-radius: 10px; max-width: 60%; word-wrap: break-word; }}
        .assistant-message {{ background-color: transparent; padding: 10px 15px; border-radius: 10px; max-width: 60%; word-wrap: break-word; }}
        .avatar {{ width: 40px; height: 40px; border-radius: 50%; margin: 0 10px; }}
        .user-container {{ justify-content: flex-end; }}
        .assistant-container {{ justify-content: flex-start; }}
    </style>
""", unsafe_allow_html=True)

# กำหนดโฟลเดอร์สำหรับเก็บแชทเก่า
CHAT_HISTORY_DIR = "chat_history"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# โหลดรายการแชทเก่าทั้งหมด
chat_files = [f.replace(".json", "") for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith(".json")]

# Sidebar: เลือกแชทเก่าหรือสร้างแชทใหม่
st.sidebar.title("📂 Chat History")
selected_chat = st.sidebar.selectbox("Select a chat", ["➕ Create New Chat"] + chat_files)

# ปุ่มลบแชท
if selected_chat != "➕ Create New Chat":
    if st.sidebar.button("🗑️ Delete This Chat"):
        os.remove(os.path.join(CHAT_HISTORY_DIR, f"{selected_chat}.json"))
        st.rerun()

# ปุ่มสร้างแชทใหม่
if selected_chat == "➕ Create New Chat":
    new_chat_name = st.sidebar.text_input("Enter new chat name")
    if st.sidebar.button("✅ Create"):
        if new_chat_name:
            with open(os.path.join(CHAT_HISTORY_DIR, f"{new_chat_name}.json"), "w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)
            st.rerun()

# ฟังก์ชันโหลดและบันทึกแชท
def load_chat_history(chat_name):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json")
    return json.load(open(file_path, "r", encoding="utf-8")) if os.path.exists(file_path) else []

def save_chat_history(chat_name, messages):
    with open(os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json"), "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)

# โหลดแชทปัจจุบัน
if "messages" not in st.session_state:
    st.session_state.messages = []

if selected_chat != "➕ Create New Chat":
    st.session_state.messages = load_chat_history(selected_chat)

# **แสดง Title พร้อม Animation เมื่อเริ่มต้น และหายไปหลังจากเริ่มแชท**
if not st.session_state.messages:
    st.markdown(
        f"""
        <h1 id="title" style="font-size:35px; color:#ffff;">
            HI, what do you want me to help with? {selected_chat if selected_chat != '➕ Create New Chat' else ''}
        </h1>
        <script>
            function removeTitle() {{
                document.getElementById("title").classList.add("fade-out");
                setTimeout(() => {{
                    document.getElementById("title").style.display = "none";
                }}, 15000);
            }}
        </script>
        """, 
        unsafe_allow_html=True
    )

# กล่องแสดงแชท
with st.container():
    chat_box = st.container()
    with chat_box:
        for role, content in st.session_state.messages:
            if role == "user":
                st.markdown(
                    f"""
                    <div class="message-container user-container">
                        <div class="user-message">{content}</div>
                        <img src="{USER_AVATAR}" class="avatar">
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="message-container assistant-container">
                        <img src="{AI_AVATAR}" class="avatar">
                        <div class="assistant-message">{content}</div>
                    </div>
                    """, unsafe_allow_html=True
                )

# ช่องป้อนข้อความ
user_input = st.chat_input("Type a message...")

if user_input:
    # เมื่อมีข้อความแรก ให้เรียก JavaScript เพื่อลบ Title
    st.components.v1.html("<script>removeTitle();</script>", height=0)

    # แสดงข้อความของผู้ใช้ (ฝั่งขวา)
    st.session_state.messages.append(("user", user_input))
    with chat_box:
        st.markdown(
            f"""
            <div class="message-container user-container">
                <div class="user-message">{user_input}</div>
                <img src="{USER_AVATAR}" class="avatar">
            </div>
            """, unsafe_allow_html=True
        )

    # ใช้ spinner ขณะรอผลลัพธ์
    with st.spinner("🤖 Thinking..."):
        response = get_ollama_response(user_input)

    # แสดงข้อความตอบกลับจาก AI (ฝั่งซ้าย)
    st.session_state.messages.append(("assistant", response))
    with chat_box:
        st.markdown(
            f"""
            <div class="message-container assistant-container">
                <img src="{AI_AVATAR}" class="avatar">
                <div class="assistant-message">{response}</div>
            </div>
            """, unsafe_allow_html=True
        )

    # บันทึกแชท
    if selected_chat != "➕ Create New Chat":
        save_chat_history(selected_chat, st.session_state.messages)

    st.rerun()  # รีโหลดหน้าเพื่อให้ข้อความใหม่ปรากฏ
