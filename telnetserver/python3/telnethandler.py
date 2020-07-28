
class TelnetCMD(object):
    theNULL = b"\x00"
    SEND = b"\x01"
    BEL = b"\x07"
    EOF = b"\xec"  # end of file
    SUSP = b"\xed"
    ABORT = b"\xee"  # abort
    EOR = b"\xef"  # end of record
    SE = b"\xf0"  # Subnegotiation End
    NOP = b"\xf1"  # No Operation
    DM = b"\xf2"  # Data Mark
    BRK = b"\xf3"  # Break
    IP = b"\xf4"  # Interrupt process
    AO = b"\xf5"  # Abort output
    AYT = b"\xf6"  # Are You There
    EC = b"\xf7"  # Erase Character
    EL = b"\xf8"  # Erase Line
    GA = b"\xf9"  # Go Ahead
    SB = b"\xfa"  # Subnegotiation Begin
    WILL = b"\xfb"
    WONT = b"\xfc"
    DO = b"\xfd"
    DONT = b"\xfe"
    IAC = b"\xff"  # "Interpret As Command"


class TelnetCode(object):
    BINARY = b"\x00"  # 8-bit data path
    ECHO = b"\x01"  # echo
    RCP = b"\x02"  # prepare to reconnect
    SGA = b"\x03"  # suppress go ahead
    NAMS = b"\x04"  # approximate message size
    STATUS = b"\x05"  # give status
    TM = b"\x06"  # timing mark
    RCTE = b"\x07"  # remote controlled transmission and echo
    NAOL = b"\x08"  # negotiate about output line width
    NAOP = b"\x09"  # negotiate about output page size
    NAOCRD = b"\x0a"  # negotiate about CR disposition
    NAOHTS = b"\x0b"  # negotiate about horizontal tabstops
    NAOHTD = b"\x0c"  # negotiate about horizontal tab disposition
    NAOFFD = b"\x0d"  # negotiate about formfeed disposition
    NAOVTS = b"\x0e"  # negotiate about vertical tab stops
    NAOVTD = b"\x0f"  # negotiate about vertical tab disposition
    NAOLFD = b"\x10"  # negotiate about output LF disposition
    XASCII = b"\x11"  # extended ascii character set
    LOGOUT = b"\x12"  # force logout
    BM = b"\x13"  # byte macro
    DET = b"\x14"  # data entry terminal
    SUPDUP = b"\x15"  # supdup protocol
    SUPDUPOUTPUT = b"\x16"  # supdup output
    SNDLOC = b"\x17"  # send location
    TTYPE = b"\x18"  # terminal type
    EOR = b"\x19"  # end or record
    TUID = b"\x1a"  # TACACS user identification
    OUTMRK = b"\x1b"  # output marking
    TTYLOC = b"\x1c"  # terminal location number
    VT3270REGIME = b"\x1d"  # 3270 regime
    X3PAD = b"\x1e"  # X.3 PAD
    NAWS = b"\x1f"  # window size
    TSPEED = b"\x20"  # terminal speed
    LFLOW = b"\x21"  # remote flow control
    LINEMODE = b"\x22"  # Linemode option
    XDISPLOC = b"\x23"  # X Display Location
    OLD_ENVIRON = b"\x24"  # Old - Environment variables
    AUTHENTICATION = b"\x25"  # Authenticate
    ENCRYPT = b"\x26"  # Encryption option
    NEW_ENVIRON = b"\x27"  # New - Environment variables
    TN3270E = b"\x28"  # TN3270E
    XAUTH = b"\x29"  # XAUTH
    CHARSET = b"\x2a"  # CHARSET
    RSP = b"\x2b"  # Telnet Remote Serial Port
    COM_PORT_OPTION = b"\x2c"  # Com Port Control Option
    SUPPRESS_LOCAL_ECHO = b"\x2d"  # Telnet Suppress Local Echo
    TLS = b"\x2e"  # Telnet Start TLS
    KERMIT = b"\x2f"  # KERMIT
    SEND_URL = b"\x30"  # SEND-URL
    FORWARD_X = b"\x31"  # FORWARD_X
    PRAGMA_LOGON = b"\x8a"  # TELOPT PRAGMA LOGON
    SSPI_LOGON = b"\x8b"  # TELOPT SSPI LOGON
    PRAGMA_HEARTBEAT = b"\x8c"  # TELOPT PRAGMA HEARTBEAT
    EXOPL = b"\xff"  # Extended-Options-List
    NOOPT = b"\x00"


class SpecialKey(object):
    ESC = b'\x1b'
    ARROW_UP = b'\x1b[A'
    ARROW_DOWN = b'\x1b[B'
    ARROW_LEFT = b'\x1b[D'
    ARROW_RIGHT = b'\x1b[C'
    LDEL = b'\x1b[3~'
    END = b'\x1b[4~'
    HOME = b'\x1b[1~'
    PAGE_UP = b'\x1b[5~'
    PAGE_DOWN = b'\x1b[6~'
    DELETE = b'\x7f'
    BACKSPACE = b'\x08'
    Tab = b'\t'
    CTRL_Z = b'\x1a'
    CTRL_C = b'\x03'
    W_ENTER = b'\r\n'
    L_ENTER = b'\r\x00'


class SpecialSymbol(object):
    CLEAR_CURRENT_LINE = b'\x1b[2K'
    DEL_LEFT = b'\x1b[D\x1b[K'
    MOVE_LEFT = b'\x1b[D'
    MOVE_RIGHT = b'\x1b[C'
    DEL_RIGHT = b'\x1b[K'
    EXIT = b'exit()'
    QUIT = b'quit()'


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
        self.sbdataq = b''
        self.iac_sq = b''

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
            SpecialKey.CTRL_C: self.handle_exit,
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
                self.iac_sq = b''
                if c == TelnetCMD.SB:
                    self.if_sb = True
                    self.sbdataq = b''
                elif c == TelnetCMD.SE:
                    self.if_sb = False
                    self.negotiation_handler(c, TelnetCode.NOOPT)
                idx += 1
            elif len(self.iac_sq) == 2:
                cmd = self.iac_sq[1]
                self.iac_sq = b''
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
        sursor_str = SpecialSymbol.MOVE_LEFT * \
            self.get_line_len(self.current_line[:self.cursor_index])
        del_right_str = SpecialSymbol.DEL_RIGHT * \
            self.get_line_len(self.current_line)
        if 0 <= self.history_index < len(self.history):
            history_line = self.history[self.history_index][:]
        if history_line != self.current_line:
            self.set_cur_line(history_line)
            send_str = b''.join(self.current_line)
            move_str = b''.join([sursor_str, del_right_str, send_str])
        return move_str

    # sepcial count for tab
    def get_line_len(self, line):
        ret_len = 0
        if line and isinstance(line, list):
            ret_len = len(line)
            if SpecialKey.Tab in line:
                for i in line:
                    ret_len += Const.TAB_TO_SPACE_NUM - 1 if i == SpecialKey.Tab else 0
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
        if SpecialKey.Tab in data:
            data = data.replace(SpecialKey.Tab, b' ' * Const.TAB_TO_SPACE_NUM)
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
        script_str = b"".join(self.current_line)
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
            ch = raw_line[idx:idx+1]
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
                b''.join(self.current_line[self.cursor_index:]))
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
            send_str = TelnetCMD.IAC + cmd + opt
        elif cmd in TelnetCMD.__dict__.values():
            send_str = TelnetCMD.IAC + cmd
        self.send_text(send_str)

    def send_text(self, text):
        if self.conn_handler and text:
            self.conn_handler.send_data(text)

    # old_byte 只支持单字节
    def bytes_replace(self, bs, old_byte, new_byte):
        ret_bytes = b''
        if old_byte not in bs:
            return bs

        for i in bs:
            if i == old_byte:
                ret_bytes += new_byte
            else:
                ret_bytes += i
        return ret_bytes

    def prepare_send_text(self, text):
        text = self.bytes_replace(text, TelnetCMD.IAC, TelnetCMD.IAC*2)
        text = self.bytes_replace(text, TelnetCode.NAOCRD,
                                  TelnetCode.NAOFFD + TelnetCode.NAOCRD)
        self.send_text(text)

    def setup_protocl(self):
        for k, v in Const.DOACK.items():
            self.send_command(v, k)
        for k, v in Const.WILLACK.items():
            self.send_command(v, k)
