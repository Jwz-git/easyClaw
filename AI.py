import Func


def main():
    system_message = {"role": "system", "content": Func.build_system_prompt()}
    messages = [system_message]

    if Func.judgeFolder():
        print("文件夹检查通过，继续执行。")

    messages = Func.choose_and_load_history(system_message)

    while True:
        user_input = input("\n 【你】\n").strip()
        if not user_input:
            print("\n【AI】\n请输入有效任务。")
            continue

        messages.append({"role": "user", "content": user_input})

        while True:
            try:
                response = Func.sendMessages(messages=messages)
                reply = (response.choices[0].message.content or "").strip()
            except Exception as e:
                print(f"\n【AI】\n调用模型失败：{e}")
                break

            messages.append({"role": "assistant", "content": reply})

            if reply.startswith("命令："):
                command = reply.partition("命令：")[2].strip()
                print(f"\n【AI】\n{command}")

                command_result = Func.executeCommand(command)
                content = f"执行结果：{command_result}"
                print(f"\n【Agent】\n{content}")

                messages.append({"role": "user", "content": content})
                continue

            if reply.startswith("完成："):
                print("\n----------Agent 循环结束----------")
                print(f"\n【AI】\n{reply.partition('完成：')[2].strip()}")
                history_path = Func.save_history_by_content(messages)
                print(f"\n【Agent】\n历史记录已更新：{history_path}")
                break

            # 输出不符合协议时，追加纠正提示，避免死循环
            fix_prompt = "你的输出格式错误。请只输出一行：命令：XXX 或 完成：XXX"
            print(f"\n【AI】\n{reply}")
            print(f"\n【Agent】\n{fix_prompt}")
            messages.append({"role": "user", "content": fix_prompt})


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断。")
