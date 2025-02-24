from ollama import chat

def get_ollama_response(user_message):
    """ ส่งข้อความไปยัง Ollama และรับข้อความตอบกลับ โดยตัด Think: ออก """
    full_response = ""
    for chunk in chat(model="deepseek-r1", messages=[{'role': 'user', 'content': user_message}], stream=True):
        full_response += chunk["message"]["content"]

    full_response = full_response.replace("<think>", "").replace("</think>", "").strip()

    return full_response
