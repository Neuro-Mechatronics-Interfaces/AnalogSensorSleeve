import sys
from PyQt5.QtWidgets import QApplication
from sleeve.plotter import AnalogPlotter 

# Main application entry
if __name__ == "__main__":
    app = QApplication(sys.argv)
    server_url = "192.168.16.1"  # Replace with ESP32's actual IP address
    main_window = AnalogPlotter(server_url)
    main_window.show()
    sys.exit(app.exec_())