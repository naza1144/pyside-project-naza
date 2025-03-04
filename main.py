import streamlit as st
import os
import json
from ollama_service import get_ollama_response

st.markdown("""
    <style>
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# กำหนดโฟลเดอร์สำหรับเก็บแชทเก่า
CHAT_HISTORY_DIR = "chat_history"
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)

# โหลดรายการแชทเก่าทั้งหมด
chat_files = [f.replace(".json", "") for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith(".json")]

# Sidebar: เลือกแชทเก่าหรือสร้างใหม่
st.sidebar.title("📂 แชทเก่า")
selected_chat = st.sidebar.selectbox("เลือกแชท", ["➕ สร้างแชทใหม่"] + chat_files)

# ปุ่มลบแชท
if selected_chat != "➕ สร้างแชทใหม่":
    if st.sidebar.button("🗑️ ลบแชทนี้"):
        os.remove(os.path.join(CHAT_HISTORY_DIR, f"{selected_chat}.json"))
        st.rerun()

# ฟังก์ชันโหลดและบันทึกแชท
def load_chat_history(chat_name):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_chat_history(chat_name, messages):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)

# กรณีสร้างแชทใหม่
if selected_chat == "➕ สร้างแชทใหม่":
    new_chat_name = st.sidebar.text_input("ตั้งชื่อแชทใหม่")
    if st.sidebar.button("✅ สร้าง"):
        if new_chat_name:
            new_chat_file = os.path.join(CHAT_HISTORY_DIR, f"{new_chat_name}.json")
            with open(new_chat_file, "w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)
            st.rerun()

# โหลดแชทปัจจุบัน
if "messages" not in st.session_state:
    st.session_state.messages = []

if selected_chat != "➕ สร้างแชทใหม่":
    st.session_state.messages = load_chat_history(selected_chat)

st.title(f"DeepSeek-r1: {selected_chat if selected_chat != '➕ สร้างแชทใหม่' else'╰(*°▽°*)╯' }")

# กล่องแสดงแชทที่สามารถเลื่อนดูได้
with st.container():
    chat_box = st.container()
    with chat_box:
        for role, content in st.session_state.messages:
            with st.chat_message(role):
                st.markdown(content)

# ช่องป้อนข้อความ
user_input = st.chat_input("พิมพ์ข้อความที่นี่...")

if user_input:
    # แสดงข้อความของผู้ใช้
    st.session_state.messages.append(("user", user_input))
    with chat_box:
        with st.chat_message("user"):
            st.markdown(user_input)

    # ใช้ spinner ขณะรอผลลัพธ์
    with st.spinner("🤖 กำลังคิด..."):
        response = get_ollama_response(user_input)

    # แสดงข้อความตอบกลับจาก AI
    st.session_state.messages.append(("assistant", response))
    with chat_box:
        with st.chat_message("assistant"):
            st.markdown(response)

    # บันทึกแชท
    if selected_chat != "➕ สร้างแชทใหม่":
        save_chat_history(selected_chat, st.session_state.messages)

    st.rerun()  # รีโหลดหน้าเพื่อให้ข้อความใหม่ปรากฏ