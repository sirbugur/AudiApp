import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QVBoxLayout, QWidget, QGridLayout, QStatusBar, QPushButton, QFileDialog

import sys
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.sc = super(PlotCanvas, self).__init__(fig)

    def plot(self, data, title="Plot"):
        self.axes.plot(data)
        self.axes.set_title(title)
        self.draw()
    
    def plot_waterfall(self, audio_data, sample_rate, window_size=1024):
        # Divide the audio data into chunks and plot them
        self.axes.specgram(audio_data, NFFT=window_size, Fs=sample_rate, noverlap=512)
        self.axes.set_title("Waterfall Plot")
        self.axes.set_xlabel('Time [s]')
        self.axes.set_ylabel('Frequency [Hz]')
        # self.axes.colorbar(label='Intensity [dB]')
        self.draw()

    def plot_fft(self, audio_data, sample_rate):
        N = len(audio_data)
        T = 1.0 / sample_rate
        yf = np.fft.fft(audio_data)
        xf = np.fft.fftfreq(N, T)[:N//2]
        
        self.axes.plot(xf, 2.0/N * np.abs(yf[:N//2]))
        self.axes.set_title("FFT Plot")
        self.draw() 

class PlotWidget(QWidget):
    def __init__(self):
        self.widget = super(PlotWidget, self).__init__()
        self.plot_canvas = PlotCanvas(self, width=5, height=4)
        # self.plot_canvas.plot(data, title)
        self.plot_canvas.plot([], "Time Series")
        self.vbox = QVBoxLayout()
        toolbar = NavigationToolbar2QT(self.plot_canvas, self)

        self.vbox.addWidget(toolbar)
        self.vbox.addWidget(self.plot_canvas)

        self.setLayout(self.vbox)

    def updateWavPlot(self, data, title):
        self.plot_canvas.plot(data, title)
    
    def updateWaterfallPlot(self, data, sample_rate, window_size=1024):
        self.plot_canvas.plot_waterfall(data, sample_rate, window_size)

    def updateFFTPlot(self, data, sample_rate):
        self.plot_canvas.plot_fft(data, sample_rate)

class AudioApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dj-Jay Jay Okocha App")
        self.setGeometry(100, 100, 1200, 800)

        # Create a menu bar with 3 actions
        self._create_nav_bar()

        # Create a central widget with 4 plots
        self._create_central_widget()

        # Create a status bar
        self._create_status_bar()

    def _create_nav_bar(self):
        nav_bar = self.menuBar()

        action1 = QAction("Open", self)
        action1.triggered.connect(lambda: self.play_audio())
        action2 = QAction("Record", self)
        action2.triggered.connect(lambda: self.update_status("Record clicked"))
        action3 = QAction("Stop", self)
        action3.triggered.connect(lambda: self.update_status("Stop clicked"))

        nav_bar.addAction(action1)
        nav_bar.addAction(action2)
        nav_bar.addAction(action3)
        
    def _create_plot_with_toolbar(self, data, title):
        """Create a plot with a navigation toolbar."""
        plot_widget = QWidget()
        vbox = QVBoxLayout()

        plot_canvas = PlotCanvas(self, width=5, height=4)
        plot_canvas.plot(data, title)

        toolbar = NavigationToolbar2QT(plot_canvas, self)

        vbox.addWidget(toolbar)
        vbox.addWidget(plot_canvas)

        plot_widget.setLayout(vbox)
        return plot_widget

    def _create_central_widget(self):
        central_widget = QWidget(self)
        layout = QGridLayout()

        # Create 4 plot canvases
        self.plot1 = PlotWidget()
        self.plot2 = PlotWidget()
        self.plot3 = PlotWidget()
        self.plot4 = self._create_plot_with_toolbar([1, 3, 2, 4, 3], "Plot 4")

        # Add plots to layout
        layout.addWidget(self.plot1, 0, 0)
        layout.addWidget(self.plot2, 0, 1)
        layout.addWidget(self.plot3, 1, 0)
        layout.addWidget(self.plot4, 1, 1)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        

    def _create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def update_status(self, message):
        self.statusBar.showMessage(message)

    def update_plots_after_file_opened(self, audio_data, sample_rate):
        self.plot1.updateWavPlot(audio_data, "Time Series")
        self.plot2.updateWaterfallPlot(audio_data, sample_rate)
        self.plot3.updateFFTPlot(audio_data, sample_rate)

    def play_audio(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Audio', '', 'WAV Files (*.wav)')
        if file_name:
            sample_rate, data = wav.read(file_name)
            self.update_plots_after_file_opened(data, sample_rate)
            self.update_status(f"Playing : {file_name}")
            sd.play(data, samplerate=sample_rate)
            # sd.wait()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioApp()
    # window = MainWindow()
    window.show()
    sys.exit(app.exec_())
