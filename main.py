import streamlit as st
import os
import json
from ollama_service import get_ollama_response

# กำหนดโฟลเดอร์เก็บแชท
CHAT_HISTORY_DIR = "chat_history"
DEFAULT_CHAT = "แชทแรกของเรา"

# สร้างโฟลเดอร์ถ้ายังไม่มี
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)

# ฟังก์ชันสร้างแชทเริ่มต้น (แชทแรกของเรา)
def create_default_chat():
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{DEFAULT_CHAT}.json")
    if not os.path.exists(file_path):  # ถ้ายังไม่มี ให้สร้างไฟล์
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump([("assistant", "สวัสดี! นี่คือแชทแรกของเรา 💖")], file, ensure_ascii=False, indent=4)

# โหลดรายการแชทเก่าทั้งหมด
def load_chat_list():
    return [f.replace(".json", "") for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith(".json")]

# ฟังก์ชันโหลดแชทจากไฟล์ JSON
def load_chat_history(chat_name):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# ฟังก์ชันบันทึกแชทลงไฟล์ JSON
def save_chat_history(chat_name, messages):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)

# สร้างแชทเริ่มต้นถ้ายังไม่มี
create_default_chat()

# โหลดรายการแชท
chat_files = load_chat_list()

# Sidebar: แสดงรายการแชท
st.sidebar.title("📂 แชทเก่า")
selected_chat = st.sidebar.selectbox("เลือกแชท", ["➕ สร้างแชทใหม่"] + chat_files, index=1 if DEFAULT_CHAT in chat_files else 0)

# ปุ่มลบแชท (แสดงเฉพาะเมื่อไม่ใช่แชทแรกของเรา)
if selected_chat != "➕ สร้างแชทใหม่" and selected_chat != DEFAULT_CHAT:
    if st.sidebar.button("🗑️ ลบแชทนี้"):
        os.remove(os.path.join(CHAT_HISTORY_DIR, f"{selected_chat}.json"))
        st.rerun()  # รีโหลดหน้า

# ถ้าผู้ใช้เลือก "สร้างแชทใหม่"
if selected_chat == "➕ สร้างแชทใหม่":
    new_chat_name = st.sidebar.text_input("ตั้งชื่อแชทใหม่")
    if st.sidebar.button("✅ สร้าง"):
        if new_chat_name:
            new_chat_file = os.path.join(CHAT_HISTORY_DIR, f"{new_chat_name}.json")
            with open(new_chat_file, "w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)  # สร้างไฟล์ใหม่
            st.rerun()

# โหลดแชทปัจจุบัน
if selected_chat != "➕ สร้างแชทใหม่":
    st.title(f"💬 {selected_chat}")
    st.session_state.messages = load_chat_history(selected_chat)
else:
    st.title("💬 มีอะไรให้ฉันช่วยบ้างครับ?")
    st.session_state.messages = []

# แสดงประวัติแชท
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

# ช่องป้อนข้อความ
user_input = st.chat_input("พิมพ์ข้อความที่นี่...")

if user_input:
    # แสดงข้อความของผู้ใช้
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # ใช้ spinner ขณะรอผลลัพธ์จาก DeepSeek-R1
    with st.spinner("🤖 DeepSeek-R1 กำลังคิด..."):
        response = get_ollama_response(user_input)

    # แสดงข้อความตอบกลับจาก AI
    st.session_state.messages.append(("assistant", response))
    with st.chat_message("assistant"):
        st.markdown(response)

    # บันทึกแชทลงไฟล์
    if selected_chat != "➕ สร้างแชทใหม่":
        save_chat_history(selected_chat, st.session_state.messages)
