from importlib.resources import files
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QSpinBox,
    QPushButton,
    QSlider,
    QGridLayout,
    QWidget,
    QGraphicsEllipseItem,
    QGraphicsView,
    QGraphicsScene,
)

from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF


class DraggablePoint(QGraphicsEllipseItem):
    def __init__(self, rect, wheel_center, wheel_radius, color_update_callback):
        super().__init__(rect)
        self.wheel_center = wheel_center
        self.wheel_radius = wheel_radius
        self.color_update_callback = color_update_callback

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionChange:
            new_x, new_y = value.x(), value.y()
            center_x, center_y = self.wheel_center

            # Compute the distance between the center and the new position
            dx = new_x - center_x
            dy = new_y - center_y
            distance = (dx**2 + dy**2) ** 0.5

            # If the distance is greater than the radius, scale the position
            if distance > self.wheel_radius:
                scale = self.wheel_radius / distance
                new_x = center_x + dx * scale
                new_y = center_y + dy * scale
                value = QPointF(new_x, new_y)

            # Call the color update callback
            self.color_update_callback(value)
        return super().itemChange(change, value)


class ColorWheelWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the window
        self.setWindowTitle("Color Wheel")
        self.setFixedWidth(475)
        self.setFixedHeight(315)

        central_widget = QWidget()
        self.window_layout = QGridLayout()
        self.setCentralWidget(central_widget)

        # Chromatic wheel label
        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.chromatic_wheel_pixmap = QPixmap(
            str(files("rgb_spot_color_wheel.resources").joinpath("color_wheel.png"))
        )

        # Compute the center and radius of the wheel
        self.wheel_center = (
            self.chromatic_wheel_pixmap.width() // 2,
            self.chromatic_wheel_pixmap.height() // 2,
        )
        self.wheel_radius = self.chromatic_wheel_pixmap.width() // 2

        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.graphics_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.graphics_view.setSceneRect(
            0,
            0,
            self.chromatic_wheel_pixmap.width(),
            self.chromatic_wheel_pixmap.height(),
        )
        self.graphics_scene.addPixmap(self.chromatic_wheel_pixmap)

        # Draggable point
        self.draggable_point = DraggablePoint(
            QRectF(-5, -5, 10, 10),
            self.wheel_center,
            self.wheel_radius,
            self.update_preview_color,
        )
        self.draggable_point.setBrush(QColor("black"))
        self.draggable_point.setFlag(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable
        )
        self.draggable_point.setFlag(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsScenePositionChanges
        )
        self.graphics_scene.addItem(self.draggable_point)

        # Preview label
        self.preview_label = QLabel(self)
        self.preview_label.setStyleSheet(f"border: 1px solid black;")
        self.preview_label.setFixedSize(50, 50)

        # RGB spinboxes & its labels
        self.red_spinbox = QSpinBox(self)
        self.green_spinbox = QSpinBox(self)
        self.blue_spinbox = QSpinBox(self)

        self.red_spinbox.setRange(0, 255)
        self.green_spinbox.setRange(0, 255)
        self.blue_spinbox.setRange(0, 255)

        self.red_label = QLabel(self)
        self.green_label = QLabel(self)
        self.blue_label = QLabel(self)

        self.red_label.setText("R:")
        self.green_label.setText("G:")
        self.blue_label.setText("B:")

        # Luminosity and blink sliders
        self.luminosity_slider = QSlider(Qt.Orientation.Vertical, self)
        self.blink_slider = QSlider(Qt.Orientation.Vertical, self)

        self.luminosity_slider.setRange(0, 189)
        self.blink_slider.setRange(0, 61)

        self.luminosity_label = QLabel(self)
        self.blink_label = QLabel(self)

        self.luminosity_label.setText("Luminosity")
        self.blink_label.setText("Blink")

        # Send button
        self.send_button = QPushButton("Send", self)

        # RGB layout
        self.rgb_layout = QGridLayout()
        self.rgb_layout.addWidget(self.red_label, 0, 0)
        self.rgb_layout.addWidget(self.red_spinbox, 0, 1)
        self.rgb_layout.addWidget(self.green_label, 1, 0)
        self.rgb_layout.addWidget(self.green_spinbox, 1, 1)
        self.rgb_layout.addWidget(self.blue_label, 2, 0)
        self.rgb_layout.addWidget(self.blue_spinbox, 2, 1)

        # Luminosity and blink layout
        self.sliders_layout = QGridLayout()
        self.sliders_layout.addWidget(self.luminosity_label, 0, 0)
        self.sliders_layout.addWidget(self.luminosity_slider, 1, 0)
        self.sliders_layout.addWidget(self.blink_label, 0, 1)
        self.sliders_layout.addWidget(self.blink_slider, 1, 1)

        # Add widgets to the window layout
        self.window_layout.addWidget(self.graphics_view, 0, 0, 5, 5)
        self.window_layout.addWidget(self.preview_label, 0, 5)
        self.window_layout.addLayout(self.rgb_layout, 1, 5, 4, 1)
        self.window_layout.addLayout(self.sliders_layout, 0, 6, 5, 1)
        self.window_layout.addWidget(self.send_button, 5, 0, 1, 7)

        # Set default color
        self.draggable_point.setPos(*self.wheel_center)
        self.red_spinbox.setValue(255)
        self.green_spinbox.setValue(255)
        self.blue_spinbox.setValue(255)

        # Set the layout
        central_widget.setLayout(self.window_layout)

    def update_preview_color(self, position):
        # Check if the position is inside the wheel
        if (
            0 <= position.x() < self.chromatic_wheel_pixmap.width()
            and 0 <= position.y() < self.chromatic_wheel_pixmap.height()
        ):
            image = self.chromatic_wheel_pixmap.toImage()
            color = image.pixelColor(int(position.x()), int(position.y()))

            # Update the preview label
            self.preview_label.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid black;"
            )
            self.red_spinbox.setValue(color.red())
            self.green_spinbox.setValue(color.green())
            self.blue_spinbox.setValue(color.blue())
