import threading
from concurrent.futures import ThreadPoolExecutor
import serial

class control:
    def __init__(self, COM, baudrate):
        self.com = COM
        self.baundrate = baudrate
        self.Serial = serial.Serial(self.com, self.baundrate)
        self.data = None
        self.stop = False
        self.check = False
        self.user_input = ""

    def recv_data(self):
        while self.stop is False:
            try:
                if self.Serial.in_waiting > 0:
                    data = self.Serial.readline()
                    data = data.decode()
                    data1 = data.rstrip()
                    if data1 == "Y":
                        self.check = True
                        break
            except:
                continue

    def nothing(self):
        self.Serial.write(b'x')

    def quickRotate(self):
        self.Serial.write(b'Q')

    def slowRotate(self):
        self.Serial.write(b'W')

    def stopRotate(self):
        self.Serial.write(b'E')

    def onXylanh1(self):
        self.Serial.write(b'H')

    def onXylanh2(self):
        self.Serial.write(b'J')

    def onXylanh3(self):
        self.Serial.write(b'K')

    def move2A(self):
        self.Serial.write(b'A')

    def move2C(self):
        self.Serial.write(b'C')

    def move2B(self):
        self.Serial.write(b'B')

    def doJob(self, job=None):
        if job is None:
            self.nothing()
        if job == "quickrotate":
            self.quickRotate()
        if job == "slowrotate":
            self.slowRotate()
        if job == "stoprotate":
            self.stopRotate()
        if job == "onxylanh1":
            self.onXylanh1()
        if job == "onxylanh2":
            self.onXylanh2()
        if job == "onxylanh3":
            self.onXylanh3()
        if job == "move2A":
            self.move2A()
        if job == "move2B":
            self.move2B()


    def Test (self):
        while self.stop is False:
            if self.check is True:
                self.Serial.write(b'x')
            else:
                if self.user_input == "off":
                    self.Serial.write(b'x')
                if self.user_input == "on3":
                    self.onXylanh3()
                if self.user_input == "on2":
                    self.onXylanh2()
                if self.user_input == "on1":
                    self.onXylanh1()
                if self.user_input == "A":
                    self.move2A()
                if self.user_input == "B":
                    self.move2B()
                if self.user_input == "max":
                    self.quickRotate()
                if self.user_input == "medium":
                    self.slowRotate()
                if self.user_input == "stop":
                    self.stopRotate()


    def update_data(self):
        while self.stop is False:
            self.user_input = input("\n Type on1 / on2 / on3 / A / B / off / quit : ")

            if self.user_input == "quit":
                self.stop = True

    def thread_pool(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.Test)

    def run(self):
        thread = threading.Thread(target=self.thread_pool)
        thread.start()
        self.update_data()
        thread.join()


if __name__ == "__main__":
    Test = control('COM3', 115200)
    Test.run()




