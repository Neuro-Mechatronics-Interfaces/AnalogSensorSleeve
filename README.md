# NML Sensor Sleeve Project

This repository contains the firmware and Python visualization software for the NML Sensor Sleeve project. The project uses an ESP32 microcontroller to collect analog data from 15 sensors and a Python GUI application to visualize the data in real-time.

## Repository Structure

```
.
├── firmware/          # Arduino firmware for the ESP32
│   └── ESP32S_Analog_Sensors.ino
├── sleeve/            # Python package for networking and plotting
│   ├── __init__.py
│   ├── network.py     # Handles communication with the ESP32
│   └── plotter.py     # Implements the visualization GUI
├── images/            # Icons and other visual assets
│   └── SleeveIcon.png
├── app.py             # Entry point for the GUI application
└── __init__.py        # Root-level Python package initializer
```

## Requirements

### Hardware
- ESP32 microcontroller
- 15 analog sensors
- Computer with Python installed

### Software
- Arduino IDE with ESP32 board support
- Python 3.8+
- Required Python libraries (see below)

## Installation

### 1. Firmware Setup
1. Navigate to the `firmware/` directory.
2. Open the `ESP32S_Analog_Sensors.ino` file in the Arduino IDE.
  + _Note: you may need to create an Arduino Cloud Sketch, then replace the contents of the Cloud Sketch folder with contents from `firmware/` to get it to correctly import to your version of the Arduino 2 IDE._
3. Ensure the following settings in the Arduino IDE:
   - **Board**: ESP32 Dev Module
   - **Upload Speed**: 115200
   - **Partition Scheme**: Default 4MB with spiffs
4. Configure your Wi-Fi credentials in the firmware:
   ```cpp
   const char* ssid = "Your_SSID";
   const char* password = "Your_Password";
   ```
5. Upload the firmware to the ESP32.
6. Connect to the WiFi network created by the ESP32 board. It will only support a single client connection at a time. To maintain your normal WiFi (e.g. to keep internet access), it's recommended to just get a WiFi USB dongle (they are cheap) and connect to it using that.

### 2. Python Environment
1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Icon Configuration (Optional)
- The GUI uses an icon located at `images/SleeveIcon.png`.
- Ensure the path is correct or update the `AnalogPlotter` class to point to a custom icon.

## Usage

1. Start the Python application:
   ```bash
   python -m app
   ```
2. Connect the ESP32 to power and ensure it is broadcasting its Wi-Fi network.
3. The GUI will display:
   - **Left Column**: Line plots for 15 channels with gradients corresponding to heatmap regions.
   - **Top-Right**: A 2x3 heatmap for the first 6 sensors.
   - **Bottom-Right**: A 3x3 heatmap for the remaining 9 sensors.

## Configuration

### Firmware
- **Sampling Rate**: `250 Hz`
- **Number of Channels**: `15`
- Modify these settings in the `firmware/ESP32S_Analog_Sensors.ino` file if needed:
  ```cpp
  #define SAMPLE_RATE 250
  #define N_CHANNELS 15
  ```

### Python
- Update the `server_host` in `app.py` to match your ESP32's IP address if not using the default (`192.168.16.1`).

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push to your branch:
   ```bash
   git commit -m "Add new feature"
   git push origin feature-name
   ```
4. Create a pull request.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

