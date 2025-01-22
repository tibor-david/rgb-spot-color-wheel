import sys
import threading
import serial
import time
from serial.tools import list_ports
from PyQt6.QtWidgets import QApplication, QMessageBox

from .interface import ColorWheelWindow


class App:
    def __init__(self):
        # Create the board & search for it
        self.serial = serial.Serial(baudrate=9600)
        self.thread: threading.Thread = threading.Thread(
            target=self.connect_board, daemon=True
        )
        self.thread.start()

        # Initialize the interface
        self.app = QApplication([])
        self.window = ColorWheelWindow()

        # Connect the button to the function
        self.window.send_button.clicked.connect(self.send_message)

    def search_board(self):
        # Arduino UNO VID/PID
        VID_PID = [
            (0x2341, 0x0001),
            (0x2341, 0x0043),
            (0x2341, 0x0243),
            (0x2A03, 0x0043),
            (0x1A86, 0x7523),
        ]

        # Search for the board
        while self.thread.is_alive():
            for device in list_ports.comports():
                if (device.vid, device.pid) in VID_PID:
                    return device.device
            time.sleep(0.5)

    def connect_board(self):
        port = self.search_board()
        self.serial.close()
        self.serial.port = port
        self.serial.open()

    def forge_message(self):
        # Get the RGB values
        r = self.window.red_spinbox.value()
        g = self.window.green_spinbox.value()
        b = self.window.blue_spinbox.value()

        # Get the luminosity or blink value
        if self.window.blink_slider.value() == 0:
            e = self.window.luminosity_slider.value()
        else:
            e = 189 + self.window.blink_slider.value()

        # Create the message
        message = f"r{r}g{g}b{b}e{e}\n"

        return message

    def send_message(self):
        message = self.forge_message()

        try:
            self.serial.write(message.encode())
        except serial.SerialException:
            # Show error message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText("No board connected.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

            # Start board search
            if not self.thread.is_alive():
                self.thread = threading.Thread(target=self.connect_board, daemon=True)
                self.thread.start()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())
