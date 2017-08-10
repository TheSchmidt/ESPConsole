# Module: TimeoutInput
#
# Allow waiting for a user key press or timeout
#
# Trs 2017-07-30

import select
import sys
import tty
import termios

class TimeoutInput:
    """Control stdin to wait for input or a timeout."""
    def __init__(self, raw=False):
        self.Input=sys.stdin
        self.OrigSettings=termios.tcgetattr(self.Input)
        tty.setcbreak(self.Input)
        if raw:
            tty.setraw(self.Input)

    def __del__(self):
        """Reset attributes of stdin."""
        termios.tcsetattr(self.Input, termios.TCSADRAIN, self.OrigSettings)
        #print "...cleaning up"

    def ReadKey(self, timeout, readSockets=[]):
        """Get the next char or return None if no key is pressed before timeout occurs.
           Optionally a list of file handles can be given which are also supervised and returned on read data ready
        """
        readSockets.append(self.Input)
        (readyRead, readyWrite, readyEx) = select.select(readSockets, [], [], timeout)
        #    print readyRead
        if self.Input in readyRead:
            return self.Input.read(1)
        elif len(readyRead) > 0:
            return readyRead[0]
        return None

    def ClearLine(self):
        # return to the left border and delete the line
        sys.stdout.write('\r\033[K')


# Sample program: show a receding bar and abort if a key is pressed
if __name__ == "__main__":
    timedInput=TimeoutInput()
    print "Press a key or wait for a bit..."
    for i in range(20,0,-1):
        sys.stdout.write('#' * i)
        sys.stdout.flush()
        c = timedInput.ReadKey(0.100)
        if c:
            print "\npressed:",c
            break
        timedInput.ClearLine()
