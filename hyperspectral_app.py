import sys
import csv
import numpy as np
import spectral
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel,
    QFileDialog, QAction, QComboBox, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


# ===================== Hyperspectral Data =====================
class HyperSpectralData:
    def __init__(self, hdr_path):
        self.img = spectral.open_image(hdr_path)
        cube = np.squeeze(self.img.load())

        self.cube = cube
        self.wavelengths = np.array(self.img.bands.centers)
        self.saved_spectra = []

    def get_pixel_spectrum(self, x, y):
        return self.cube[y, x, :]


# ===================== Plot Widget =====================
class SpectralPlot(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.clear_plot()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_title("Spectral Signatures")
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Reflectance")
        self.draw()

    def update_plot(self, wavelengths, hover_spectrum, saved_spectra):
        self.ax.clear()

        for s in saved_spectra:
            # self.ax.plot(wavelengths, s["spectrum"],
            #              label=f"({s['x']},{s['y']})")  modify it
            self.ax.plot(wavelengths, s["spectrum"])

        if hover_spectrum is not None:
            self.ax.plot(wavelengths, hover_spectrum,
                         "--", color="black", label="Hover")

        if saved_spectra or hover_spectrum is not None:
            self.ax.legend()

        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Reflectance")
        self.ax.set_title("Spectral Signatures")
        self.fig.tight_layout()
        self.draw()


# ===================== Image Viewer =====================
class ImageViewer(QLabel):
    def __init__(self, plot_widget, status_label):
        super().__init__()
        self.hs_data = None
        self.plot_widget = plot_widget
        self.status_label = status_label

        self.band_index = 0
        self.max_spectra = 5  # >>> CHANGE (default)

        self.setAlignment(Qt.AlignCenter)
        self.setText("Load a hyperspectral image")
        self.setMouseTracking(True)

    def set_data(self, hs_data):
        self.hs_data = hs_data
        self.hs_data.saved_spectra.clear()
        self.status_label.setText("")
        self.display_band()

    def set_max_spectra(self, value):
        self.max_spectra = value  

    def display_band(self):
        if self.hs_data is None:
            return

        band = self.hs_data.cube[:, :, self.band_index].astype(np.float32)
        band = (band - band.min()) / (band.max() - band.min() + 1e-6)
        band_uint8 = (band * 255).astype(np.uint8)

        h, w = band_uint8.shape
        qimg = QImage(
            band_uint8.data, w, h,
            band_uint8.strides[0],
            QImage.Format_Grayscale8
        )
        self.setPixmap(QPixmap.fromImage(qimg))

    def mouseMoveEvent(self, event):
        if (
            self.hs_data is None or
            self.pixmap() is None or
            len(self.hs_data.saved_spectra) >= self.max_spectra
        ):
            return  

        x, y = int(event.x()), int(event.y())

        if 0 <= x < self.hs_data.cube.shape[1] and 0 <= y < self.hs_data.cube.shape[0]:
            spectrum = self.hs_data.get_pixel_spectrum(x, y)
            self.plot_widget.update_plot(
                self.hs_data.wavelengths,
                spectrum,
                self.hs_data.saved_spectra
            )

    def mousePressEvent(self, event):
        if self.hs_data is None:
            return

        if len(self.hs_data.saved_spectra) >= self.max_spectra:
            self.status_label.setText(
                f"Maximum {self.max_spectra} spectra selected"
            )  
            return

        x, y = int(event.x()), int(event.y())

        if 0 <= x < self.hs_data.cube.shape[1] and 0 <= y < self.hs_data.cube.shape[0]:
            spectrum = self.hs_data.get_pixel_spectrum(x, y)

            self.hs_data.saved_spectra.append({
                "x": x,
                "y": y,
                "spectrum": spectrum
            })

            self.plot_widget.update_plot(
                self.hs_data.wavelengths,
                None,
                self.hs_data.saved_spectra
            )


# ===================== Main Window =====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hyperspectral Explorer")

        self.hs_data = None

        self.plot_widget = SpectralPlot()
        self.status_label = QLabel("")
        self.image_viewer = ImageViewer(self.plot_widget, self.status_label)

        
        self.max_combo = QComboBox()
        self.max_combo.addItems([str(v) for v in range(5, 55, 5)])
        self.max_combo.currentTextChanged.connect(
            lambda v: self.image_viewer.set_max_spectra(int(v))
        )

        
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)

        controls = QVBoxLayout()
        controls.addWidget(QLabel("Max Spectra"))
        controls.addWidget(self.max_combo)
        controls.addWidget(export_btn)
        controls.addWidget(self.status_label)
        controls.addStretch()

        central = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.image_viewer)
        layout.addWidget(self.plot_widget)
        layout.addLayout(controls)

        central.setLayout(layout)
        self.setCentralWidget(central)

        self.create_menu()

    def create_menu(self):
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.load_image)

        menu = self.menuBar().addMenu("File")
        menu.addAction(open_action)

    def load_image(self):
        hdr_path, _ = QFileDialog.getOpenFileName(
            self, "Open Hyperspectral Image", "", "ENVI Header (*.hdr)"
        )

        if not hdr_path:
            return

        self.hs_data = HyperSpectralData(hdr_path)
        self.image_viewer.set_data(self.hs_data)
        self.plot_widget.clear_plot()

    
    def export_csv(self):
        if self.hs_data is None or not self.hs_data.saved_spectra:
            self.status_label.setText("No spectra to export")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["x", "y"] + list(self.hs_data.wavelengths)
            writer.writerow(header)

            for s in self.hs_data.saved_spectra:
                writer.writerow([s["x"], s["y"]] + list(s["spectrum"]))

        self.status_label.setText("CSV exported successfully")


# ===================== Run App =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
