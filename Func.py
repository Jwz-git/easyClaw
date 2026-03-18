import os
from openai import OpenAI
import json

def execute_command(cmd):
    # 添加 2>&1 重定向错误输出到标准输出
    cmd_with_stderr = f"{cmd} 2>&1"
    # 用with语句自动管理文件对象
    with os.popen(cmd_with_stderr) as pipe:
        # 读取所有内容，strip()去除首尾空白（包括换行）
        result = pipe.read().strip()
    return result



client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

def sendMessages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False,
    )
    return response

def save_history(messages, filename="history.json"):
    with open(filename, "a", encoding="utf-8") as f:
        string = ""
        for item in messages:
            json_str = json.dumps(item, ensure_ascii=False, indent=4)
            string += json_str + ",\n"
        f.write(f"[{string}\n]")