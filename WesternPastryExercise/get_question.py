
import json
import traceback


def save_question_data(questions):
    save_str = json.dumps(questions)
    with open("qd.py", 'w', encoding='utf-8') as f:
        f.write("Qdata=")
        f.write(save_str)


def deal_quest_data():
    questions = {}
    with open("Q.txt", encoding="utf-8") as f:
        q_no, q = None, {
            "description": "",
            "id": "",
            "choose": {},
            "answer": ""
        }
        for line in f.readlines():
            line = line.strip()
            try:
                if q_no:
                    if line.startswith('正确答案:'):
                        t = line.split(":")
                        q["answer"] = t[1].strip()
                        questions[q_no] = q
                        q_no = None
                        q = {
                            "description": "",
                            "id": "",
                            "choose": {},
                            "answer": ""
                        }
                    elif '.' in line:
                        t = line.split(".")
                        q["choose"][t[0].strip()] = ".".join(t[1:]).strip()
                elif '()' in line:
                    t = line.split(".")
                    q_no = t[0].strip()
                    q["description"], q["id"] = line, q_no

            except:
                traceback.print_exc()
                break
    return questions


if __name__ == "__main__":
    q = deal_quest_data()
    save_question_data(q)
