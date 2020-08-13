from qd import Qdata
import random
import const
import json


class AnswerMode:
    def __init__(self, name):
        self._name = name
        self._cur_index = 0
        self._questions = []
        self._right_indexs = []
        self._his_answer_num = 0
        self._his_right_num = 0
        self.restart()

    def restart(self):
        pass

    def answer(self, answer_str):
        q = self.get_cur()
        if_right = False
        if answer_str == q["answer"]:
            self._right_indexs.append(self._cur_index)
            self._his_right_num += 1
            if_right = True
        self._his_answer_num += 1
        return if_right, q["answer"]

    def next(self):
        self._cur_index += 1
        self._cur_index %= len(self._questions)

    def get_cur(self):
        id = self.get_cur_id()
        if not id:
            return None
        return Qdata.get(str(id))

    def get_cur_id(self):
        if not self._questions or self._cur_index >= len(self._questions):
            self.restart()
        if not self._questions:
            return None
        id = self._questions[self._cur_index]
        return id

    def __str__(self):
        s = "%s:\n  当前题/题数：%s/%s\n  正确数/答题数：%s/%s" % (self._name,
                                                      self._cur_index+1, len(self._questions), self._his_right_num, self._his_answer_num)
        return s

    def get_save_data(self):
        ret = {
            "nm": self._name,
            "ci": self._cur_index,
            "qs": self._questions,
            "ris": self._right_indexs,
            "han": self._his_answer_num,
            "hrn": self._his_right_num
        }
        return ret

    def read_data(self, d):
        if not (d and isinstance(d, dict)):
            return
        name = d.get("nm")
        if name != self._name:
            return
        self._cur_index = d.get("ci", 0)
        self._questions = d.get("qs", [])
        self._right_indexs = d.get("ris", 0)
        self._his_answer_num = d.get("han", 0)
        self._his_right_num = d.get("hrn", 0)


class RandomModle(AnswerMode):
    def __init__(self, name):
        super().__init__(name)

    def restart(self):
        num = len(Qdata.keys()) + 1
        temp_list = [str(i) for i in range(1, num)]
        for i in range(num - 1):
            temp_index = random.randint(0, num-2)
            temp_list[i], temp_list[temp_index] = temp_list[temp_index], temp_list[i]
        self._questions = temp_list
        self._cur_index = 0
        self._right_indexs = []


class OderedModle(AnswerMode):
    def __init__(self, name):
        super().__init__(name)

    def restart(self):
        if not self._questions:
            num = len(Qdata.keys()) + 1
            self._questions = [str(i) for i in range(1, num)]
        self._cur_index = 0
        self._right_indexs = []


class TestModle(AnswerMode):
    def __init__(self, name):
        super().__init__(name)
        self._grades = []

    def restart(self):
        num = len(Qdata.keys()) + 1
        self._questions = random.choices(
            [str(i) for i in range(1, num)], k=100)
        self._cur_index = 0


class WrongPickModle(AnswerMode):
    def __init__(self, name):
        super().__init__(name)

    def restart(self):
        self._his_answer_num = 0
        self._his_right_num = 0

    def add_wrong_q(self, id):
        if id and id not in self._questions:
            self._questions.append(id)


class UserData:
    def __init__(self):
        self._modles = [RandomModle(const.btn_str_list[0]), OderedModle(
            const.btn_str_list[1]), TestModle(const.btn_str_list[2]), WrongPickModle(const.btn_str_list[3])]
        self._cur_mode = 0
        self._total_aq = 0
        self._total_ra = 0
        self._if_can_answer = True
        self.read_data()

    def get_all_status(self):
        s = ""
        for i in self._modles:
            s += str(i)
            s += "\n\n"
        r_p = self._total_ra / self._total_aq if self._total_aq else 0
        s += "总答题数：%s\n答对题数：%s\n正确率：%.2f%%\n\n" % (
            self._total_aq, self._total_ra, r_p*100)
        return s

    def get_cur_mod_data(self):
        if self._cur_mode > len(self._modles):
            self._cur_mode %= len(self._modles)
        return self._modles[self._cur_mode]

    def get_cur_q_data(self):
        mod = self.get_cur_mod_data()
        return mod.get_cur()

    def set_modle(self, modle):
        for i, m in enumerate(self._modles):
            if m._name == modle and i != self._cur_mode:
                self._cur_mode = i
                self._if_can_answer = True
                return True
        return False

    def answer(self, an):
        data = self.get_cur_mod_data()
        if not data:
            return
        self._if_can_answer = False
        self._total_aq += 1
        if_right, right_as = data.answer(an)
        if if_right:
            self._total_ra += 1
        else:
            s, qid = self._modles[3], data.get_cur_id()
            s.add_wrong_q(qid)

        return if_right, right_as

    def next(self):
        data = self.get_cur_mod_data()
        if not data:
            return
        self._if_can_answer = True
        data.next()

    def check_can_answer(self):
        return self._if_can_answer

    def save_data(self):
        data = {
            "cd": self._cur_mode,
            "raq": self._total_aq,
            "tra": self._total_ra,
            "mds": {}
        }

        for m in self._modles:
            data[m._name] = m.get_save_data()
        ret_str = json.dumps(data)
        with open(const.config_path, 'w', encoding="utf-8") as f:
            f.write(ret_str)

    def read_data(self):
        try:
            with open(const.config_path, 'r', encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if not (data and isinstance(data, dict)):
                            continue

                        self._cur_mode = data.get("cd", 0)
                        self._total_aq = data.get("raq", 0)
                        self._total_ra = data.get("tra", 0)

                        for m in self._modles:
                            m.read_data(data.get(m._name))
                    except:
                        continue
                    break
        except:
            pass
