import re
from ollama import chat

def clean_latex(text):
    """ ลบโค้ด LaTeX และ Markdown ออกจากข้อความ """
    text = re.sub(r"\\\(.+?\\\)", "", text)  # ลบ \( ... \)
    text = re.sub(r"\\\[(.+?)\\\]", "", text)  # ลบ \[ ... \]
    text = re.sub(r"\{(.+?)\}", "", text)  # ลบ {...} ที่ใช้ใน LaTeX
    text = re.sub(r"\$\$(.+?)\$\$", "", text)  # ลบ $$ ... $$ (MathJax)
    text = re.sub(r"\$(.+?)\$", "", text)  # ลบ $ ... $ (inline math)
    text = re.sub(r"\\boxed{(.+?)}", r"\1", text)  # เอาค่าภายใน \boxed{} ออกมา
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # ลบ **...** (Markdown Bold)
    
    return text.strip()

def get_ollama_response(user_message):
    """ ส่งข้อความไปยัง Ollama และรับข้อความตอบกลับ โดยตัด Think: ออก และลบ LaTeX """
    full_response = ""
    for chunk in chat(model="deepseek-r1", messages=[{'role': 'user', 'content': user_message}], stream=True):
        full_response += chunk["message"]["content"]

    full_response = full_response.replace("<think>", "").replace("</think>", "").strip()

    return clean_latex(full_response)  # ลบ LaTeX ออกจากข้อความ
