import serial
import time


class SerialCom:
    """Class for serial communication"""
    def __init__(self, device, baudrate):
        self.device = device
        self.baudrate = baudrate
        self.s = serial.Serial(self.device, self.baudrate)

    def init_communication(self):
        # s.open()
        time.sleep(0.1)

    def write(self, text):
        self.s.write((text + "\r\n").encode('utf-8'))  # \r
        response = self.s.readline()
        # print all comments from Arduino
        while response.startswith(b'//'):
            print(response.decode("utf-8"))
            response = self.s.readline()

        return response.decode("utf-8").strip()

    def read(self):
        if not self.s.readable():
            return ""

        response = self.s.readline()
        # print all comments from Arduino
        while response.startswith(b'//'):
            print(response.decode("utf-8"))
            response = self.s.readline()

        return response.decode("utf-8")

    def read_all(self):
        return self.s.read_all().decode("utf-8")

    def read_until_received(self, *wf):
        start = time.time()
        try:
            found = False
            while not found:
                txt = self.s.readline().decode('utf-8').strip()
                print("received: ", txt)
                for s in list(wf):
                    # print(s, ".", txt)
                    if s == txt:
                        found = True
                        break
                if time.time() - start > 5:
                    return "timeout"

            return txt
            # while not any(txt in s for s in list(wf)):
            #     txt = self.s.readline()
        except TypeError as err:
            print("Type error: {0}".format(err))

        return txt

    def close(self):
        self.s.close()

