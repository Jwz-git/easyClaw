import os
from openai import OpenAI
import json
import subprocess
import platform
import re
from datetime import datetime

COMMAND_TIMEOUT_SECONDS = 120

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


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt():
    sys_info = f"""
            Operating System: {platform.system()}\n
            OS Version: {platform.version()}\n
            Architecture: {platform.machine()}\n
            Python Version: {platform.python_version()}\n
            """

    agentmd = read_text("md/Agent.md")
    skillmd = read_text("md/Skill.md")
    return f"{skillmd}\n{agentmd}\n{sys_info}"


def get_history_files(history_dir="history"):
    files = []
    for name in os.listdir(history_dir):
        if name.endswith(".json"):
            full_path = os.path.join(history_dir, name)
            if os.path.isfile(full_path):
                files.append(full_path)
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files


def choose_and_load_history(system_message):
    answer = input("\n是否加载历史对话？(y/N)\n").strip().lower()
    if answer not in {"y", "yes"}:
        return [system_message]

    history_files = get_history_files("history")
    if not history_files:
        print("\n【Agent】\nhistory/ 目录中没有可用历史记录，将使用新会话。")
        return [system_message]

    print("\n可用历史记录（按最近修改排序）：")
    for idx, path in enumerate(history_files, start=1):
        print(f"{idx}. {path}")

    selection = input("\n选择序号(直接回车=最新, 输入 n=不加载)：\n").strip().lower()
    if selection == "n":
        return [system_message]

    selected_path = history_files[0]
    if selection:
        if not selection.isdigit():
            print("\n【Agent】\n输入无效，将使用新会话。")
            return [system_message]
        index = int(selection) - 1
        if index < 0 or index >= len(history_files):
            print("\n【Agent】\n序号越界，将使用新会话。")
            return [system_message]
        selected_path = history_files[index]

    loaded_messages = loadHistory(selected_path)
    if not isinstance(loaded_messages, list) or not loaded_messages:
        print("\n【Agent】\n历史记录为空或格式无效，将使用新会话。")
        return [system_message]

    first = loaded_messages[0]
    if isinstance(first, dict) and first.get("role") == "system":
        messages = loaded_messages
    else:
        messages = [system_message] + loaded_messages

    print(f"\n【Agent】\n已加载历史记录: {selected_path}（共 {len(messages)} 条消息）")
    return messages


def saveHistory(messages, filename="history.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def _sanitize_filename(text, max_len=40):
    text = text.strip().replace(" ", "_")
    # 保留中英文、数字、下划线和短横线，避免非法文件名。
    text = re.sub(r"[^\w\-\u4e00-\u9fff]", "", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_-")
    if not text:
        text = "对话"
    return text[:max_len]


def _extract_latest_task_text(messages):
    ignored_prefixes = ("执行结果：", "你的输出格式错误")
    for item in reversed(messages):
        if item.get("role") != "user":
            continue
        content = (item.get("content") or "").strip()
        if not content:
            continue
        if content.startswith(ignored_prefixes):
            continue
        return content
    return "对话"


def save_history_by_content(messages, history_dir="history"):
    os.makedirs(history_dir, exist_ok=True)
    task_text = _extract_latest_task_text(messages)
    title = _sanitize_filename(task_text)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.json"
    path = os.path.join(history_dir, filename)
    saveHistory(messages, path)
    return path


def loadHistory(filename="history.json"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            print("历史记录文件格式错误，无法加载。")
            return []


def judgeCommand(command):
    # 这里可以添加一些简单的规则来判断命令是否合法
    if not command or not command.strip():
        return False, "命令为空"

    forbidden_commands = ["rm -rf /", "shutdown", "reboot"]
    lowered = command.lower()
    for forbidden in forbidden_commands:
        if forbidden in lowered:
            return False, f"命令包含禁止的内容: {forbidden}"
    return True, "命令合法"


def executeCommand(cmd):
    is_valid, message = judgeCommand(cmd)
    if not is_valid:
        return f"错误: {message}"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.join(base_dir, "workspace")
    run_dir = base_dir if "skill/" in cmd else workspace_dir

    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            cwd=run_dir,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"错误: 命令执行超时({COMMAND_TIMEOUT_SECONDS}s)"
    except Exception as e:
        return f"错误: 命令执行失败: {e}"

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    output = "\n".join(part for part in [stdout, stderr] if part)

    if completed.returncode != 0:
        return f"命令执行失败(退出码 {completed.returncode})\n{output}".strip()

    return output if output else "命令执行成功(无输出)"


def judgeFolder():
    required_dirs = [
        "history",
        "workspace",
        "workspace/videos",
        "workspace/archive",
        "workspace/edit",
        "workspace/scripts",
    ]
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
    return True
