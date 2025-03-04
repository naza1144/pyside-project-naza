from ollama import chat

def get_ollama_response(user_message):
    """ ส่งข้อความไปยัง Ollama และรับข้อความตอบกลับ โดยตัด Think: ออก """
    full_response = ""
    
    try:
        for chunk in chat(model="phi3", messages=[{'role': 'user', 'content': user_message}], stream=True):
            if "message" in chunk and "content" in chunk["message"]:
                full_response += chunk["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"  # ส่งข้อความ error กลับไปถ้าเกิดข้อผิดพลาด

    # ลบ Think Tags และคืนค่าข้อความที่สะอาด
    return full_response.replace("<think>", "").replace("</think>", "").strip()