import json
import Func
import platform

sys_info = f"""
            Operating System: {platform.system()}\n
            OS Version: {platform.version()}\n
            Architecture: {platform.machine()}\n
            Python Version: {platform.python_version()}\n
            """

agentmd = open("md/Agent.md", "r").read()
skillmd = open("md/Skill.md", "r").read()

messages = [{"role": "system", "content": f"{skillmd}\n{agentmd}\n{sys_info}"}]

while True:

    user_input = input("\n 【你】\n")
    messages.append({"role": "user", "content": user_input})

    while True:
        response = Func.sendMessages(messages=messages)

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print(f"\n【AI】\n{reply}")

        if reply.strip().startswith("完成："):
            print("\n----------Agent 循环结束----------")
            print(f"\n【AI】\n{reply.strip().split('完成：')[1].strip()}")

            # Func.save_history(messages=messages)
            break

        command = reply.strip().split("命令：")[1].strip()
        command_result = Func.execute_command(command)

        content = f"执行结果：{command_result}"
        print(f"\n【Agent】\n{content}")
        messages.append({"role": "user", "content": content})
