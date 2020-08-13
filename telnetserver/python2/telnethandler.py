
class TelnetCMD(object):
    theNULL = chr(0)
    SEND = chr(1)
    BEL = chr(7)
    EOF = chr(236)  # end of file
    SUSP = chr(237)
    ABORT = chr(238)  # abort
    EOR = chr(239)  # end of record
    SE = chr(240)  # Subnegotiation End
    NOP = chr(241)  # No Operation
    DM = chr(242)  # Data Mark
    BRK = chr(243)  # Break
    IP = chr(244)  # Interrupt process
    AO = chr(245)  # Abort output
    AYT = chr(246)  # Are You There
    EC = chr(247)  # Erase Character
    EL = chr(248)  # Erase Line
    GA = chr(249)  # Go Ahead
    SB = chr(250)  # Subnegotiation Begin
    WILL = chr(251)
    WONT = chr(252)
    DO = chr(253)
    DONT = chr(254)
    IAC = chr(255)  # "Interpret As Command"


class TelnetCode(object):
    BINARY = chr(0)  # 8-bit data path
    ECHO = chr(1)  # echo
    RCP = chr(2)  # prepare to reconnect
    SGA = chr(3)  # suppress go ahead
    NAMS = chr(4)  # approximate message size
    STATUS = chr(5)  # give status
    TM = chr(6)  # timing mark
    RCTE = chr(7)  # remote controlled transmission and echo
    NAOL = chr(8)  # negotiate about output line width
    NAOP = chr(9)  # negotiate about output page size
    NAOCRD = chr(10)  # negotiate about CR disposition
    NAOHTS = chr(11)  # negotiate about horizontal tabstops
    NAOHTD = chr(12)  # negotiate about horizontal tab disposition
    NAOFFD = chr(13)  # negotiate about formfeed disposition
    NAOVTS = chr(14)  # negotiate about vertical tab stops
    NAOVTD = chr(15)  # negotiate about vertical tab disposition
    NAOLFD = chr(16)  # negotiate about output LF disposition
    XASCII = chr(17)  # extended ascii character set
    LOGOUT = chr(18)  # force logout
    BM = chr(19)  # byte macro
    DET = chr(20)  # data entry terminal
    SUPDUP = chr(21)  # supdup protocol
    SUPDUPOUTPUT = chr(22)  # supdup output
    SNDLOC = chr(23)  # send location
    TTYPE = chr(24)  # terminal type
    EOR = chr(25)  # end or record
    TUID = chr(26)  # TACACS user identification
    OUTMRK = chr(27)  # output marking
    TTYLOC = chr(28)  # terminal location number
    VT3270REGIME = chr(29)  # 3270 regime
    X3PAD = chr(30)  # X.3 PAD
    NAWS = chr(31)  # window size
    TSPEED = chr(32)  # terminal speed
    LFLOW = chr(33)  # remote flow control
    LINEMODE = chr(34)  # Linemode option
    XDISPLOC = chr(35)  # X Display Location
    OLD_ENVIRON = chr(36)  # Old - Environment variables
    AUTHENTICATION = chr(37)  # Authenticate
    ENCRYPT = chr(38)  # Encryption option
    NEW_ENVIRON = chr(39)  # New - Environment variables
    TN3270E = chr(40)  # TN3270E
    XAUTH = chr(41)  # XAUTH
    CHARSET = chr(42)  # CHARSET
    RSP = chr(43)  # Telnet Remote Serial Port
    COM_PORT_OPTION = chr(44)  # Com Port Control Option
    SUPPRESS_LOCAL_ECHO = chr(45)  # Telnet Suppress Local Echo
    TLS = chr(46)  # Telnet Start TLS
    KERMIT = chr(47)  # KERMIT
    SEND_URL = chr(48)  # SEND-URL
    FORWARD_X = chr(49)  # FORWARD_X
    PRAGMA_LOGON = chr(138)  # TELOPT PRAGMA LOGON
    SSPI_LOGON = chr(139)  # TELOPT SSPI LOGON
    PRAGMA_HEARTBEAT = chr(140)  # TELOPT PRAGMA HEARTBEAT
    EXOPL = chr(255)  # Extended-Options-List
    NOOPT = chr(0)


class SpecialKey(object):
    ESC = '\x1b'
    ARROW_UP = '\x1b[A'
    ARROW_DOWN = '\x1b[B'
    ARROW_LEFT = '\x1b[D'
    ARROW_RIGHT = '\x1b[C'
    LDEL = '\x1b[3~'
    END = '\x1b[4~'
    HOME = '\x1b[1~'
    PAGE_UP = '\x1b[5~'
    PAGE_DOWN = '\x1b[6~'
    DELETE = '\x7f'
    BACKSPACE = '\x08'
    Tab = '\t'
    CTRL_Z = '\x1a'
    CTRL_C = '\x03'
    W_ENTER = '\r\n'
    L_ENTER = '\r\x00'


class SpecialSymbol(object):
    CLEAR_CURRENT_LINE = '\x1b[2K'
    DEL_LEFT = '\x1b[D\x1b[K'
    MOVE_LEFT = '\x1b[D'
    MOVE_RIGHT = '\x1b[C'
    DEL_RIGHT = '\x1b[K'
    EXIT = 'exit()'
    QUIT = 'quit()'


class Const(object):
    MAX_HISTORY_NUMS = 20
    TAB_TO_SPACE_NUM = 4

    USEFUL_CMDS = (
        TelnetCMD.DO,
        TelnetCMD.DONT,
        TelnetCMD.WILL,
        TelnetCMD.WONT
    )

    DOACK = {
        TelnetCode.ECHO: TelnetCMD.WILL,
        TelnetCode.SGA: TelnetCMD.WILL
    }

    WILLACK = {
        TelnetCode.ECHO: TelnetCMD.DONT,
        TelnetCode.SGA: TelnetCMD.DO,
        TelnetCode.LINEMODE: TelnetCMD.DONT
    }


class TelnetHandler(object):

    def __init__(self, conn_handler):
        self.conn_handler = conn_handler
        self.will_opts = {}
        self.do_opts = {}
        self.history_index = 0
        self.history = []
        self.cursor_index = 0
        self.current_line = []
        self.if_sb = False
        self.sbdataq = ''
        self.iac_sq = ''

        self.CMD_HANDLER = {
            TelnetCMD.NOP: self.handle_nop,
            TelnetCMD.WILL: self.handle_will_wont,
            TelnetCMD.WONT: self.handle_will_wont,
            TelnetCMD.DO: self.handle_do_dont,
            TelnetCMD.DONT: self.handle_do_dont,
            TelnetCMD.SE: self.handle_se,
            TelnetCMD.SB: self.handle_sb
        }

        self.special_char = {
            SpecialKey.ESC: self.handle_esc,
            SpecialKey.BACKSPACE: self.handle_backspace,
            SpecialKey.DELETE: self.handle_w_delete,
            SpecialKey.CTRL_Z: self.handle_exit,
            SpecialKey.CTRL_C: self.handle_exit
        }

        self.key_3_chars = {
            SpecialKey.ARROW_UP: self.handle_arrow_up,
            SpecialKey.ARROW_DOWN: self.handle_arrow_down,
            SpecialKey.ARROW_LEFT: self.handle_arrow_left,
            SpecialKey.ARROW_RIGHT: self.handle_arrow_right
        }

        self.key_4_chars = {
            SpecialKey.END: self.handle_end,
            SpecialKey.HOME: self.handle_home,
            SpecialKey.PAGE_UP: self.handle_pageup,
            SpecialKey.PAGE_DOWN: self.handle_pagedown,
            SpecialKey.LDEL: self.handle_delete
        }

        self.setup_protocl()

    def process_cmd(self, cmd_str):
        idx = 0
        while idx < len(cmd_str):
            c = cmd_str[idx]
            if not self.iac_sq:
                if c == TelnetCMD.IAC:
                    self.iac_sq += c
                else:
                    if self.if_sb:
                        self.sbdataq += c
                idx += 1
            elif len(self.iac_sq) == 1:
                if c in Const.USEFUL_CMDS:
                    self.iac_sq += c
                self.iac_sq = ''
                if c == TelnetCMD.SB:
                    self.if_sb = True
                    self.sbdataq = ''
                elif c == TelnetCMD.SE:
                    self.if_sb = False
                    self.negotiation_handler(c, TelnetCode.NOOPT)
                idx += 1
            elif len(self.iac_sq) == 2:
                cmd = self.iac_sq[1]
                self.iac_sq = ''
                if cmd in Const.USEFUL_CMDS:
                    self.negotiation_handler(cmd, c)
                    idx += 1
        return idx

    def negotiation_handler(self, cmd, opt):
        if cmd in self.special_key_dict:
            self.special_key_dict[cmd](cmd, opt)

    def handle_exit(self, raw_line=None, idx=0):
        self.send_command(TelnetCMD.IP)
        self.conn_handler.handle_close()
        return 1

    def handle_end(self):
        move_str = TelnetCMD.BEL
        if self.cursor_index < len(self.current_line):
            rmove_len = len(self.current_line) - self.cursor_index
            move_str = SpecialSymbol.MOVE_RIGHT * rmove_len
            self.cursor_index = len(self.current_line)
        self.prepare_send_text(move_str)

    def handle_home(self):
        move_str = TelnetCMD.BEL
        if 0 < self.cursor_index:
            move_str = SpecialSymbol.MOVE_LEFT * self.cursor_index
            self.cursor_index = 0
        self.prepare_send_text(move_str)

    def handle_backspace(self, raw_line, idx):
        if self.cursor_index > 0:
            self.prepare_send_text(SpecialSymbol.DEL_LEFT)
            self.cursor_index -= 1
            del self.current_line[self.cursor_index]
            self.deal_right_line()
        return 1

    def handle_w_delete(self, raw_line, idx):
        self.handle_delete()
        return 1

    def handle_delete(self):
        if self.cursor_index < len(self.current_line):
            self.prepare_send_text(SpecialSymbol.DEL_RIGHT)
            del self.current_line[self.cursor_index]
            self.deal_right_line()

    def get_history_line(self):
        move_str, history_line = TelnetCMD.BEL, []
        sursor_str = SpecialSymbol.MOVE_LEFT * self.get_line_len(self.current_line[:self.cursor_index])
        del_right_str = SpecialSymbol.DEL_RIGHT * self.get_line_len(self.current_line)
        if 0 <= self.history_index < len(self.history):
            history_line = self.history[self.history_index][:]
        if history_line != self.current_line:
            self.set_cur_line(history_line)
            send_str = ''.join(self.current_line)
            move_str = "%s%s%s" % (sursor_str, del_right_str, send_str)
        return move_str

    # sepcial count for tab
    def get_line_len(self, line):
        ret_len = 0
        if line and isinstance(line, list):
            for i in line:
                ret_len += Const.TAB_TO_SPACE_NUM if i == '\t' else 1
        return ret_len

    def handle_arrow_left(self):
        move_str = TelnetCMD.BEL
        if self.cursor_index > 0:
            self.cursor_index -= 1
            move_str = SpecialSymbol.MOVE_LEFT
        self.prepare_send_text(move_str)

    def handle_arrow_right(self):
        move_str = TelnetCMD.BEL
        if self.cursor_index < len(self.current_line):
            self.cursor_index += 1
            move_str = SpecialSymbol.MOVE_RIGHT
        self.prepare_send_text(move_str)

    def handle_arrow_up(self):
        move_str = TelnetCMD.BEL
        if 0 < self.history_index <= len(self.history):
            self.history_index -= 1
            move_str = self.get_history_line()
        self.prepare_send_text(move_str)

    def handle_arrow_down(self):
        move_str = TelnetCMD.BEL
        if 0 <= self.history_index < len(self.history):
            self.history_index += 1
            move_str = self.get_history_line()
        self.prepare_send_text(move_str)

    # goto the first cmd history record!
    def handle_pageup(self):
        if 0 < self.history_index <= len(self.history):
            self.history_index = 0
        self.prepare_send_text(self.get_history_line())

    # goto the last cmd history record!
    def handle_pagedown(self):
        if 0 <= self.history_index < len(self.history) - 1:
            self.history_index = len(self.history) - 1
        self.prepare_send_text(self.get_history_line())

    def handle_nop(self, cmd, opt):
        self.send_command(TelnetCMD.NOP)

    def handle_will_wont(self, cmd, opt):
        if opt in self.WILLACK:
            self.send_command(self.WILLACK[opt], opt)
        else:
            self.send_command(TelnetCMD.DONT, opt)
        if cmd == TelnetCMD.WILL and opt == TelnetCMD.TTYPE:
            self.send_text(TelnetCMD.IAC + TelnetCMD.SB + TelnetCMD.TTYPE +
                           TelnetCMD.SEND + TelnetCMD.IAC + TelnetCMD.SE)

    def handle_do_dont(self, cmd, opt):
        if opt in Const.DOACK.keys():
            self.send_command(Const.DOACK[opt], opt)
        else:
            self.send_command(TelnetCMD.WONT, opt)

    def handle_se(self, cmd, opt):
        subreq = self.read_sb_data()
        if subreq[0] == TelnetCMD.TTYPE and subreq[1] == TelnetCMD.IS:
            pass

    def handle_sb(self, cmd, opt):
        pass

    def handle_default_char(self, ch):
        self.current_line.insert(self.cursor_index, ch)
        self.cursor_index += 1
        self.prepare_send_text(ch)
        self.deal_right_line()
        return 1

    def handle_esc(self, raw_line, idx):
        cmd_str = raw_line[idx: idx + 3]
        if cmd_str in self.key_3_chars:
            self.key_3_chars[cmd_str]()
            return 3
        cmd_str = raw_line[idx: idx + 4]
        if cmd_str in self.key_4_chars:
            self.key_4_chars[cmd_str]()
            return 4
        return 1

    def handle_input(self, data):
        if SpecialKey.W_ENTER in data:
            cmd_list = data.split(SpecialKey.W_ENTER)
        elif SpecialKey.L_ENTER in data:
            cmd_list = data.split(SpecialKey.L_ENTER)
        else:
            cmd_list = [data]
        cmd_len = len(cmd_list)
        for i in range(cmd_len):
            self.process_raw_line(cmd_list[i])
            if i < cmd_len - 1:
                self.run_current_cmd()

    def run_current_cmd(self):
        script_str = "".join(self.current_line)
        if script_str != SpecialSymbol.EXIT and script_str != SpecialSymbol.QUIT and self.conn_handler:
            self.send_text(SpecialKey.W_ENTER)
            self.conn_handler.run_script(script_str)
            self.add_cmd_to_history(self.current_line)
            self.set_cur_line()
        else:
            self.handle_exit()

    def process_raw_line(self, raw_line):
        idx = 0
        while idx < len(raw_line):
            ch = raw_line[idx]
            if ch == TelnetCMD.IAC or len(self.iac_sq) > 0 or self.if_sb:
                idx_offset = self.process_cmd(raw_line)
                idx += idx_offset
                continue
            if ch in self.special_char:
                idx_offset = self.special_char[ch](raw_line, idx)
            else:
                idx_offset = self.handle_default_char(ch)
            idx += idx_offset

    def add_cmd_to_history(self, cmd_str):
        if cmd_str and (not self.history or self.history[-1] != cmd_str):
            self.history.append(cmd_str)
            if len(self.history) > Const.MAX_HISTORY_NUMS:
                self.history = self.history[-Const.MAX_HISTORY_NUMS:]
        self.history_index = len(self.history)

    def set_cur_line(self, char_list=[]):
        if not char_list or not isinstance(char_list, list):
            char_list = []
        self.current_line = char_list
        self.cursor_index = len(char_list)

    def deal_right_line(self):
        if self.cursor_index < len(self.current_line):
            self.prepare_send_text(
                ('').join(self.current_line[self.cursor_index:]))
            cursor_offset = len(self.current_line) - self.cursor_index
            self.prepare_send_text(SpecialSymbol.MOVE_LEFT * cursor_offset)

    def send_command(self, cmd, opt=None):
        if cmd in Const.USEFUL_CMDS:
            if opt not in TelnetCode.__dict__.values():
                return
            if cmd == TelnetCMD.DO or cmd == TelnetCMD.DONT:
                tmp = (cmd == TelnetCMD.DO)
                if opt in self.do_opts and self.do_opts[opt] == tmp:
                    return
                self.do_opts[opt] = tmp
            elif cmd == TelnetCMD.WILL or cmd == TelnetCMD.WONT:
                tmp = (cmd == TelnetCMD.WILL)
                if opt in self.will_opts and self.will_opts[opt] == tmp:
                    return
                self.will_opts[opt] = tmp
            self.send_text(TelnetCMD.IAC + cmd + opt)
        elif cmd in TelnetCMD.__dict__.values():
            self.send_text(TelnetCMD.IAC + cmd)

    def send_text(self, text):
        if self.conn_handler and text:
            self.conn_handler.send_data(text)

    def prepare_send_text(self, text):
        text = str(text)
        text = text.replace(TelnetCMD.IAC, TelnetCMD.IAC*2)
        text = text.replace(chr(10), chr(13) + chr(10))
        self.send_text(text)

    def setup_protocl(self):
        for k, v in Const.DOACK.iteritems():
            self.send_command(v, k)
        for k, v in Const.WILLACK.iteritems():
            self.send_command(v, k)
