import os
import re
import math
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def calculator(expression: str) -> str:
    try:
        result= eval(expression, {"__builtins__": {}, "math": math})
        return str(result)
    except Exception as e:
        return f"Ошибка вычислений: {e}"

def get_current_date() -> str:
    return datetime.now().strftime("%d %B %Y, %A")

SYSTEM_PROMPT="""
Ты- автономный ИИ агент, работающий по фреймворку ReAct(Reason + Act).

Ты ОБЯЗАН следовать формату:

Мысль: ...
Действие: tool_name[arguments]

Или, если задача решена:

Финальный ответ: ...

Доступные инструменты:
1) calculator[математическое выражение]
2) get_current_date[]

Правила:
- Всегда начинай с шага "Мысль"
- Никогда не выдумывай результат инструмента
- После Действия жди Наблюдение
"""


def extract_action(text: str):
    """
    Извлекайте tool и аргументы из строки:
    Действие: calculator[math.sqrt(10)]
    """

    match= re.search(r"Действие:\s*(\w+)\[(.*)\]", text)
    if match:
        return match.group(1), match.group(2)
    return None, None

def run_agent(user_query: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    while True:
        response= client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
        assistant_message = response.choices[0].message.content
        print("\n"+ assistant_message)

        messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        if "Финальный ответ:" in assistant_message:
            break

        tool, argument=extract_action(assistant_message)

        if tool:
            if tool == "calculator":
                observation = calculator(argument)
            elif tool == "get_current_date":
                observation = get_current_date()
            else:
                observation="Нейзвестный инструмент"
            

            observation_message=f"Наблюдение: {observation}"
            print(observation_message)

            messages.append({
                "role": "assistant",
                "content": observation_message
            })


if __name__ == "__main__":
    print(" ReAct агент запущен")
    print("Введите вопрос (или 'exit' для выхода):\n")

    while True:
        query = input("Вы: ")

        if query.lower() in ("exit", "quit"):
            print("Агент завершён ")
            break

        run_agent(query)
        print("\n" + "-" * 50 + "\n")
