import sys
from PyQt5.QtWidgets import QMessageBox, QLabel, QTextEdit, QPushButton, QCheckBox, QWidget, QApplication, QDesktopWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPixmap
import answer_modle as AM
import const


class ChooseWin(QCheckBox):
    def __init__(self, parent, str_t, ans):
        super().__init__(parent)
        self._text = QLabel(str_t, parent)
        self._answer = ans

    def set_info(self, str_t, ans):
        self._text.setText(str_t)
        self._answer = ans

    def move(self, x, y):
        super().move(x, y)
        self._text.move(x+20, y)

    def resize(self, x, y):
        super().resize(20, y)
        self._text.resize(x, y)

    def setVisible(self, if_show):
        super().setVisible(if_show)
        self._text.setVisible(if_show)


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self._menue_bts = []
        self._back_manue_bt = None
        self._user_data = AM.UserData()
        self.initUI()

   # 控制窗口显示在屏幕中心的方法
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_wind_size(self):
        self.resize(800, 400)
        self.setMinimumSize(800, 400)
        self.setMaximumSize(800, 400)

    def initUI(self):
        self.setWindowTitle("初级西点师答题器@csshawn")
        self.set_wind_size()
        self.center()
        # self.setToolTip('1. 为了方便同学进行练习制作的小工具，题目来源于微信小程序\n2.答题数据没有持久化，打开软件会重新记录\n3.本工具只是方便练习不保证题目正确性')
        self.init_menue_button()
        self.init_question_label()
        self.init_states()
        self.init_answer_result()
        self.refresh_data()

    # 回答结果显示
    def init_answer_result(self):
        self._answer_ret = QLabel(self)
        self._right_png = QPixmap(const.right_path)
        self._wrong_png = QPixmap(const.wrong_path)

        self._answer_ret.move(300, 150)
        self._answer_ret.resize(100, 100)

        op = QGraphicsOpacityEffect()
        op.setOpacity(0.3)
        self._answer_ret.setGraphicsEffect(op)

        self._answer_ret.setAutoFillBackground(True)
        self._answer_ret.setScaledContents(True)
        self._answer_ret.setPixmap(self._wrong_png)
        self._answer_ret.setVisible(False)

    # 初始化状态栏
    def init_states(self):
        self._states_panel = QTextEdit(self)
        self._states_panel.setReadOnly(True)
        self._states_panel.resize(180, 300)
        self._states_panel.move(580, 20)
        self._states_panel.setText(self._user_data.get_all_status())

    # 初始化选择菜单
    def init_menue_button(self):
        for i in range(len(const.btn_str_list)):
            btn = QPushButton(const.btn_str_list[i], self)
            btn.setCheckable(True)
            if i == self._user_data._cur_mode:
                btn.setChecked(True)
            else:
                btn.setChecked(False)
            btn.autoExclusive()
            btn.move(20, 20+60*i)
            btn.clicked.connect(self.wichBtn)
            self._menue_bts.append(btn)

    # 初始化答题区
    def init_question_label(self):
        self._text_question = QTextEdit(self)
        self._text_question.setReadOnly(True)
        self._text_question.resize(370, 100)
        self._text_question.move(150, 20)

        self._choose_wind = []
        for i in range(len(const.answer_choose_dict)):
            cbx = ChooseWin(
                self, const.answer_choose_dict[i], const.answer_choose_dict[i])
            cbx.setChecked(False)
            cbx.resize(400, 50)
            cbx.move(150, 120 + i * 50)
            cbx.clicked.connect(self.answer)
            self._choose_wind.append(cbx)

        self._answer_wind = QLabel(self)
        self._answer_wind.resize(200, 20)
        self._answer_wind.move(150, 350)

        self._next_qs = QPushButton("下一题", self)
        self._next_qs.setCheckable(True)
        self._next_qs.resize(80, 30)
        self._next_qs.move(420, 340)
        self._next_qs.clicked.connect(self.next)

    # 设置问题
    def set_question(self, q):
        if not q:
            return
        dsp = "(选择题)" if q["choose"] else "(判断题)"
        self._text_question.setText("%s\n\n%s" % (dsp, q["description"]))
        for i in range(len(const.answer_choose_dict)):
            self._choose_wind[i].setChecked(False)
            self._choose_wind[i].setVisible(False)
            show_txt, ans = None, ""
            if q["choose"]:
                str_a = const.answer_choose_dict.get(i)
                ans, show_txt = str_a, "%s. %s" % (
                    str_a, q["choose"].get(str_a)) if str_a else None
            else:
                ans = show_txt = const.answer_judge_dict.get(i)
            if show_txt:
                self._choose_wind[i].set_info(show_txt, ans)
                self._choose_wind[i].setVisible(True)

    def wichBtn(self):
        sender = self.sender()
        for btn in self._menue_bts:
            if btn != sender:
                btn.setChecked(False)
            else:
                btn.setChecked(True)
        if_change = self._user_data.set_modle(sender.text())
        if if_change:
            self.refresh_data()

    def answer(self):
        sender = self.sender()
        if not self._user_data.check_can_answer():
            return
        ret, right_an = self._user_data.answer(sender._answer)
        if ret is None:
            return
        elif ret:
            self._answer_ret.setPixmap(self._right_png)
        else:
            self._answer_ret.setPixmap(self._wrong_png)
        self._answer_ret.setVisible(True)
        self._next_qs.setVisible(True)
        self._answer_wind.setText("正确答案：%s" % right_an)
        self._states_panel.setText(self._user_data.get_all_status())

    def refresh_data(self):
        self._answer_ret.setVisible(False)
        self._answer_wind.setText("")
        self._next_qs.setVisible(False)
        self.set_question(self._user_data.get_cur_q_data())
        self._states_panel.setText(self._user_data.get_all_status())

    def next(self):
        self._user_data.next()
        self.refresh_data()

    def closeEvent(self, event):
        reply = QMessageBox.question(self,
                                     '本程序',
                                     "是否要退出程序？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        self._user_data.save_data()
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    # 初始化题库
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
