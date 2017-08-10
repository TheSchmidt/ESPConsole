#!/usr/bin/python
# Program: this shall be a console to communicate via serial line
# It shall implement a simple line editing mechanism.
#
# Trs  2017-08-09  Creation

import sys
import select
import timeoutinput
import serial

def Trace(str):
    sys.stderr.write( str + "\n")

class ReadlineConsole:
    '''A terminal-like console for a character channel.'''
    def __init__(self, path):
        if isinstance(path, str):
            Trace("Opening file")
            self.Handle = open(path, "rw")
        else:
            Trace("using provided file handle")
            self.Handle = path
        self.TimedInput = timeoutinput.TimeoutInput()
        self.Lines=[
          "AT"
        , "ATE0"
        , "AT+GMR"
        , "AT+CWLAP"
        , ""
        ]
        self.Pos=len(self.Lines)-1
        print("<ctrl-p> for previous line, <ctrl-n> for next line")

    def Prompt(self):
        self.TimedInput.ClearLine()
        sys.stdout.write("[{0:3}] ".format(self.Pos))
        sys.stdout.write(self.Lines[self.Pos])
        sys.stdout.flush()

    def ReadWrite(self):
        self.Prompt()
        while True:
            c = self.TimedInput.ReadKey(100, [self.Handle])
            if c is None:
                return None # should be continue!
            if type(c) == type('c'):
#                Trace("Character " + c + " (" + str(ord(c)) + ")")
                if ord(c) == 3 or ord(c) == 4:     # ctrl-c, ctrl-d
                    return None
                elif ord(c) == 10 or ord(c) == 13:  # Enter
                    print("")
                    line = self.Lines[self.Pos]
                    self.Pos += 1
                    if self.Pos == len(self.Lines):
                        self.Lines.append("")
                    return line
                elif ord(c) == 127:   # Backspace
                    if len(self.Lines[self.Pos]) == 0:
                        continue
                    self.Lines[self.Pos]=self.Lines[self.Pos][:-1]
                    sys.stdout.write('\b \b')
                elif ord(c) == 21:   # ctrl-u
                    self.Lines[self.Pos] = ""
                    return self.ReadWrite()
                elif ord(c) == 16:   # ctrl-p
                    if self.Pos <= 0:
                        continue
                    self.Pos -= 1
                    return self.ReadWrite()
                elif ord(c) == 14:   # ctrl-n
                    if self.Pos >= len(self.Lines) - 1:
                        continue
                    self.Pos += 1
                    return self.ReadWrite()
                elif ord(c) == 27:   # ESC
                    # clear input from escape sequence
                    c=self.TimedInput.ReadKey(0)
                    c=self.TimedInput.ReadKey(0)
                    continue
                elif ord(c) < 32 or ord(c) > 127:
                    Trace("Character " + c + " (" + str(ord(c)) + ")")
                    continue
                else:
                    self.Lines[self.Pos] += c
                    sys.stdout.write(c)
                sys.stdout.flush()
            else:
                print("")
                while True:
                    toOutput = self.Handle.read()
                    sys.stdout.write(toOutput)
                    sys.stdout.flush()
                    r,w,x = select.select([self.Handle], [], [], 0.2)
                    if len(r) == 0:
                        self.Prompt()
                        break


def StartConsole(fifo):
    Trace("Starting console")
    cons = ReadlineConsole(fifo)
    while True:
        l = cons.ReadWrite()
        if l == None:
            break
        fifo.write(l + '\r\n')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # default: raspberry pi serial port, connected to ESP8266
        with serial.Serial('/dev/serial0', 115200) as fifo:
            StartConsole(fifo)
    else:
        with open(sys.argv[1], 'rw+') as fifo:
            StartConsole(fifo)
