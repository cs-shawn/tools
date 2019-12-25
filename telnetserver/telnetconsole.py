import sys
import asyncore
import traceback
import socket
import code
import threading
from collections import Iterable
from cStringIO import StringIO
import telnethandler


DEFAULT_RECV_BUFFER = 2048


class SimulateConsole(code.InteractiveConsole):
    def __init__(self, client, locals=None, filename='<console>'):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.client = client

    def interact(self, banner=None):
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = '... '
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            self.write("Python %s on %s\n%s\n%s" %
                       (sys.version, sys.platform, cprt, sys.ps1))
        else:
            self.write("%s\n" % str(banner))

    def write(self, line):
        line = line.replace('\r\n', '\n').replace('\n', '\r\n')
        if getattr(self.client, "send_data", None):
            self.client.send_data(line)


class TelnetConn(asyncore.dispatcher):

    def __init__(self, addr, sock, remove_handler, local_dict={}):
        asyncore.dispatcher.__init__(self, sock=sock)
        self.addr = addr
        self.remove_handler = remove_handler
        self.buffer = ""
        self.if_talked = False
        self.local_dict = local_dict
        self.telnet_handler = telnethandler.TelnetHandler(self)
        self.interactive_console = SimulateConsole(
            self, locals=self.local_dict)
        self.interactive_console.interact()

    def send_data(self, data):
        try:
            self.buffer += data
        except:
            traceback.print_exc()

    def run_script(self, cmd_str):
        encoding = getattr(sys.stdin, "encoding", None)
        if encoding and not isinstance(cmd_str, unicode):
            cmd_str = cmd_str.decode(encoding)
        back_out, output_str = sys.stdout, StringIO()
        sys.stdout = output_str
        more = self.interactive_console.push(cmd_str)
        sys.stdout = back_out
        self.interactive_console.write(output_str.getvalue())
        if more:
            self.send_data(sys.ps2)
        else:
            self.send_data(sys.ps1)

    def writable(self):
        return len(self.buffer) > 0

    def handle_read(self):
        recv_data = self.recv(DEFAULT_RECV_BUFFER)
        if recv_data and self.telnet_handler:
            self.telnet_handler.handle_input(recv_data)

    def handle_write(self):
        if self.buffer:
            sent_len = self.send(self.buffer)
            self.buffer = self.buffer[sent_len:]

    def handle_close(self):
        self.remove_handler(self.addr)


# manager telnet connect
class TelnetServer(asyncore.dispatcher):

    def __init__(self, host, port, local_dict={}, whitelist=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = host
        self._port = port
        self._if_bind = False
        self._switch = False
        self.clients = {}
        self._whitelist = whitelist
        self.local_dict = local_dict

    def print_server_msg(self):
        print "telnet server bind host:%s port:%s" % (self._host, self._port)

    @property
    def switch(self):
        return self._switch

    @switch.setter
    def switch(self, if_open):
        self._switch = if_open

    def try_bind(self):
        if self._if_bind:
            return True
        port = self._port
        while True:
            try:
                self.bind((self._host, port))
                self.set_reuse_addr()
                break
            except:
                if port >= 65535:
                    traceback.print_exc()
                    return False
                else:
                    port += 1
        self._port = port
        self._if_bind = True
        self.print_server_msg()
        return True

    def start_service(self, count=0):
        if self.try_bind():
            self.listen(count)

    def stop_service(self):
        self.switch = False
        for client in self.clients.itervalues():
            client.close()
        self.clients = {}
        self.close()
        self._if_bind = False

    def break_one_conn(self, addr):
        if addr in self.clients:
            client = self.clients.get(addr)
            print "telnet disconnect client: ", addr
            try:
                if client:
                    client.close()
                del self.clients[addr]
            except Exception as e:
                traceback.print_exc()

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            return
        sock, addr = pair
        host, port = addr
        if not self.switch or (addr in self.clients and self.clients[addr]) or (host != "127.0.0.1" and host not in self._whitelist):
            sock.close()
        else:
            client = TelnetConn(
                addr, sock, self.break_one_conn, self.local_dict)
            print "telnet connect client: ", addr
            self.clients[addr] = client

    def update_whitelist(self, whitelist):
        if not whitelist or not isinstance(whitelist, Iterable) or whitelist == self._whitelist:
            return False
        self._whitelist = whitelist
        del_addrs = []
        for addr in self.clients.iterkeys():
            if addr != "127.0.0.1" and addr not in self._whitelist:
                del_addrs.append(addr)
        for addr in del_addrs:
            self.break_one_conn(addr)
        return True


class TelnetConsole(object):
    def __init__(self, port, host="127.0.0.1", local_dict={}):
        self._running = False
        self._whitelist = None
        self.local_dict = local_dict
        self._telnet_handler = TelnetServer(host, port, self.local_dict)
        self.start_loop()

    @property
    def switch(self):
        return self._telnet_handler and self._telnet_handler.switch

    @switch.setter
    def switch(self, if_open):
        if self._telnet_handler:
            if if_open:
                self._telnet_handler.start_service()
            self._telnet_handler.switch = if_open

    def set_whitelist(self, whitelist):
        if whitelist and isinstance(whitelist, Iterable):
            self._whitelist = tuple(ip for ip in whitelist)
            if self._telnet_handler:
                self._telnet_handler.update_whitelist(whitelist)

    def start_service(self):
        self.switch = True

    def stop_service(self):
        self.switch = False
        if self._telnet_handler:
            self._telnet_handler.stop_service()

    def replace_service(self, host, port):
        if self._telnet_handler \
                and self._telnet_handler._host == host \
                and self._telnet_handler._port == port:
            return
        self.stop_service()
        self._telnet_handler = TelnetServer(host, port, self.local_dict)
        self.switch = True

    def loop(self):
        if self._running:
            return
        self._running = True
        try:
            asyncore.loop()
        except:
            traceback.print_exc()
        self._running = False

    def start_loop(self):
        t = threading.Thread(target=self.loop, name="telnet_console")
        t.start()

import time
if __name__ == "__main__":
    test = TelnetConsole(port=12345, local_dict=locals())
    test.switch = True
    while True:
        time.sleep(60)
