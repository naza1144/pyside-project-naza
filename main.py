import streamlit as st
import os
import json
from ollama_service import get_ollama_response

st.set_page_config(
    page_title="Ratatouille",  # 🔹 เปลี่ยนเป็นชื่อที่คุณต้องการ
    page_icon="https://cdn-icons-png.flaticon.com/512/2297/2297338.png",  # 🔹 สามารถใช้ Emoji หรือ URL รูปภาพ
    layout="wide"  # 🔹 กำหนดให้เว็บแอปเต็มหน้าจอ
)

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

# ===== 🎨 ปรับ Sidebar ให้แสดงรายการแชทเป็นปุ่มที่กดได้ พร้อมปุ่มลบ ===== #
st.sidebar.title("📂 Chat History")

selected_chat = None  # ค่าเริ่มต้นของแชทที่เลือก

# แสดงแชทเป็นปุ่มกดเลือกได้ + ปุ่มลบแชท
for chat_name in sorted(chat_files, reverse=True):
    col1, col2 = st.sidebar.columns([0.8, 0.2])
    with col1:
        if st.button(f"📄 {chat_name}"):
            selected_chat = chat_name  # กำหนดว่าเลือกแชทไหน
    with col2:
        if st.button("🗑️", key=f"delete_{chat_name}"):  # ปุ่มลบแชท
            os.remove(os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json"))  # ลบไฟล์ JSON
            st.rerun()  # รีโหลด Sidebar เพื่ออัปเดตรายการแชท

st.sidebar.markdown("---")

# ปุ่มสร้างแชทใหม่
new_chat_name = st.sidebar.text_input("➕ Create New Chat")
if st.sidebar.button("✅ Create") and new_chat_name:
    # สร้างแชทใหม่และบันทึกเป็นไฟล์ JSON
    with open(os.path.join(CHAT_HISTORY_DIR, f"{new_chat_name}.json"), "w", encoding="utf-8") as file:
        json.dump([], file, ensure_ascii=False, indent=4)
    st.rerun()  # รีโหลดหน้าเพื่ออัปเดตรายการแชท

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

# หากเลือกแชทแล้วให้โหลดแชทนั้น
if selected_chat:
    st.session_state.messages = load_chat_history(selected_chat)
else:
    # ไม่มีแชทที่เลือกแสดงข้อความเพื่อให้ผู้ใช้สร้างแชทก่อน
    st.write("Please create or select a chat first.")

# **แสดง Title พร้อม Animation เมื่อเริ่มต้น และหายไปหลังจากเริ่มแชท**
if not st.session_state.messages:
    st.markdown(
        f"""
        <h1 id="title" style="font-size:35px; color:#ffff;">
            HI, what do you want me to help with? {selected_chat if selected_chat else ""}
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
    # ✅ แสดงข้อความของ User ทันที
    st.session_state.messages.append(("user", user_input))
    save_chat_history(selected_chat, st.session_state.messages)

    # แสดงข้อความของ User ก่อนรอ AI ตอบ
    with chat_box:
        st.markdown(
            f"""
            <div class="message-container user-container">
                <div class="user-message">{user_input}</div>
                <img src="{USER_AVATAR}" class="avatar">
            </div>
            """, unsafe_allow_html=True
        )

    # เรียกใช้ AI และแสดงผล
    with st.spinner("🤖 Thinking..."):
        try:
            response = get_ollama_response(user_input)
        except Exception as e:
            response = "⚠️ AI ไม่สามารถตอบกลับได้ โปรดตรวจสอบเซิร์ฟเวอร์!"
            print(f"Error: {e}")  # แสดง Error ใน console

    # แสดงข้อความของ AI และบันทึก
    st.session_state.messages.append(("assistant", response))
    save_chat_history(selected_chat, st.session_state.messages)

    # แสดงข้อความของ AI ทันที
    with chat_box:
        st.markdown(
            f"""
            <div class="message-container assistant-container">
                <img src="{AI_AVATAR}" class="avatar">
                <div class="assistant-message">{response}</div>
            </div>
            """, unsafe_allow_html=True
        )

    st.rerun()  # รีโหลดหน้าเพื่อให้ข้อความใหม่ปรากฏ