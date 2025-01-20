from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from .network import ESP32Client

class AnalogPlotter(QMainWindow):
    def __init__(self, server_host):
        super().__init__()
        self.server_host = server_host
        self.client = ESP32Client(server_host)
        # Set the GUI window icon
        self.setWindowIcon(QIcon("images/SleeveIcon.png"))

        # Initialize PyQtGraph layout
        self.setWindowTitle("ESP32 Sensor Data")
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QHBoxLayout(self.main_widget)

        # Left column: Line plots
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setTitle("ESP32 Analog Data")
        self.graph_widget.setLabel("left", "Analog Value")
        self.graph_widget.setLabel("bottom", "Time", units="s")
        self.graph_widget.setToolTip("Continuous-time sensor data streams")
        self.graph_widget.addLegend()
        layout.addWidget(self.graph_widget)

        # Right column: Heatmaps
        self.heatmap_layout = QVBoxLayout()

        # Top heatmap
        self.view_top = pg.GraphicsLayoutWidget()
        self.view_top_box = self.view_top.addViewBox()
        self.heatmap_top = pg.ImageItem()
        self.heatmap_top.setToolTip("Intensity Heatmap for 2x3 distal sensor array")
        self.view_top_box.addItem(self.heatmap_top)
        self.heatmap_layout.addWidget(self.view_top)

        # Bottom heatmap
        self.view_bottom = pg.GraphicsLayoutWidget()
        self.view_bottom_box = self.view_bottom.addViewBox()
        self.heatmap_bottom = pg.ImageItem()
        self.heatmap_bottom.setToolTip("Intensity Heatmap for 3x3 proximal sensor array")
        self.view_bottom_box.addItem(self.heatmap_bottom)
        self.heatmap_layout.addWidget(self.view_bottom)
        layout.addLayout(self.heatmap_layout)

        # Initialize data storage
        self.max_points = 100
        self.data = None
        self.time = [0] * self.max_points
        self.curves = []
        self.index = 0  # Circular buffer index

        # Connect to the ESP32 server
        self.client.connect()

        # Timer to fetch data periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)  # Fetch data every 20 ms

    def update_plot(self):
        try:
            # Fetch data from ESP32
            packet = self.client.fetch_data()
            if packet is None:
                return  # No complete data yet

            n_channels = packet["n_channels"]
            new_data = packet["data"]

            # Initialize plots and data storage if needed
            if self.data is None:
                self.data = [[0] * self.max_points for _ in range(n_channels)]
                colors_top = [(255, 0, 0, 200 - i * 30) for i in range(6)]  # Red gradients
                colors_bottom = [(0, 0, 255, 200 - i * 15) for i in range(9)]  # Blue gradients
                colors = colors_top + colors_bottom

                for i in range(n_channels):
                    pen = pg.mkPen(colors[i], width=2)
                    curve = self.graph_widget.plot([], [], pen=pen, name=f"Channel {i+1}")
                    self.curves.append(curve)

            # Add new samples to the circular buffer
            for i in range(len(new_data)):
                self.time[self.index % self.max_points] = self.index / n_channels  # Simulated time axis
                for ch in range(n_channels):
                    self.data[ch][self.index % self.max_points] = new_data[i][ch]
                self.index += 1

            # Update line plots
            for ch, curve in enumerate(self.curves):
                start = self.index % self.max_points
                x = self.time[start:] + self.time[:start]
                y = self.data[ch][start:] + self.data[ch][:start]
                curve.setData(x, y)

            # Update heatmaps
            cluster_1_data = [self.data[ch][self.index % self.max_points] for ch in range(6)]
            cluster_2_data = [self.data[ch][self.index % self.max_points] for ch in range(6, n_channels)]

            self.update_heatmap(self.heatmap_top, cluster_1_data, (2, 3), "red")
            self.update_heatmap(self.heatmap_bottom, cluster_2_data, (3, 3), "blue")

        except Exception as e:
            print(f"Error updating plot: {e}")

    def update_heatmap(self, heatmap_item, data, shape, color):
        """Update a heatmap with new data."""
        matrix = np.zeros(shape)
        for i, value in enumerate(data):
            row, col = divmod(i, shape[1])
            matrix[row, col] = value

        if color == "red":
            cmap = pg.ColorMap([0, 0.5, 1], [(0, 0, 0), (128, 0, 0), (255, 0, 0)])
        elif color == "blue":
            cmap = pg.ColorMap([0, 0.5, 1], [(0, 0, 0), (0, 0, 128), (0, 0, 255)])
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        heatmap_item.setImage(matrix.T, levels=(0, 4095))
        heatmap_item.setLookupTable(lut)
