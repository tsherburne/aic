import pyqtgraph as pg
import math
from PyQt6.QtWidgets import QMainWindow, QApplication, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGraphicsPolygonItem, QGraphicsScene, QGraphicsView, QGraphicsTextItem
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPolygonF, QColor
from mission import Mission


class Renderer(QMainWindow):
    def __init__(self):
        """
        Creates the Renderer object
        """
        super().__init__()

        self.mission = Mission("example_scenario_two_scans.json")

        self.show_flag = 0
        win_width = 1400
        win_height = 1200
        self.resize(win_width, win_height)
        self.showMaximized()

        hexagon_labels = []
        for hex in self.mission.hexagons:
            hexagon_labels.append(hex.label)
        self.hex_map = Renderer.HexagonMap(self, hexagon_labels)

        self.setWindowTitle('Scenario')
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'w')
        self.background = "background-color: white; color: white;"
        self.setStyleSheet("QMainWindow {background: 'white';}")
        self.main_panel = QGridLayout()
        self.main_panel.addWidget(self.hex_map)
        self.initialize_ui_view()

        self.widget = QWidget()
        self.widget.setLayout(self.main_panel)
        self.setCentralWidget(self.widget)

    def render(self):
        """
        Render the window by calling show and processing all events
        """

        self.show()
        QApplication.processEvents()

    def initialize_ui_view(self):
        """
        Initialize the UI at the bottom of the window
        """
        self.ui_layout = QVBoxLayout()

        #  Mission Details
        self.add_custom_h_box_to_ui([
            [QLabel(), "Mission Details: Start Node - %s, End Node - %s, UAV 1 Traversal Time - %s, UAV 2 Traversal Time - %s, Cost of Human Estimate - %s, Cost of AI Estimate - %s, UGV Traversal Time - %s, UGV Clear Time - %s" % (self.mission.start_node, self.mission.end_node, self.mission.uav_1.uav_traversal_time, self.mission.uav_2.uav_traversal_time, self.mission.human_estimate_time, self.mission.ai_estimate_time, self.mission.ugv_traversal_time, self.mission.ugv_clear_time)]  # noqa: E501
        ])

        #  Mission Report (Error Reporting)
        self.mission_report = QLabel()
        self.add_custom_h_box_to_ui([
            [QLabel(), "Mission Status: "],
            [self.mission_report, ""]
        ])

        #  AI 1 Mine Estimate
        self.ai_1_query_value_label = QLabel()
        self.add_custom_h_box_to_ui([
            [QLabel(), "AI 1 Mine Estimate: "],
            [self.ai_1_query_value_label, "N/A"],
            [QPushButton(), "Get AI 1 Estimate", self.query_ai, 1]
        ])

        #  AI 2 Mine Estimate
        self.ai_2_query_value_label = QLabel()
        self.add_custom_h_box_to_ui([
            [QLabel(), "AI 2 Mine Estimate: "],
            [self.ai_2_query_value_label, "N/A"],
            [QPushButton(), "Get AI 2 Estimate", self.query_ai, 2]
        ])

        #  Human Mine Estimate
        self.human_query_value_label = QLabel()
        self.add_custom_h_box_to_ui([
            [QLabel(), "Human Mine Estimate: "],
            [self.human_query_value_label, "N/A"],
            [QPushButton(), "Get Human Estimate", self.query_human]
        ])

        #  Terrain Type
        self.terrain_value_label = QLabel()
        self.add_custom_h_box_to_ui([
            [QLabel(), "Terrain Type: "],
            [self.terrain_value_label, "N/A"]
        ])

        #  UAV 1 Location and Moving
        self.uav_1_value_label = QLabel(self.mission.uav_1.uav_location.label)
        self.move_uav_1_box = QLineEdit()
        self.add_custom_h_box_to_ui([
            [QLabel(), "UAV 1 Location: "],
            [self.uav_1_value_label, self.mission.uav_1.uav_location.label],
            [QLabel(), "Move UAV 1 To: "],
            [self.move_uav_1_box],
            [QPushButton(), "Move", self.move_uav, 1]
        ])

        #  UAV 2 Location and Moving
        self.uav_2_value_label = QLabel(self.mission.uav_2.uav_location.label)
        self.move_uav_2_box = QLineEdit()
        self.add_custom_h_box_to_ui([
            [QLabel(), "UAV 2 Location: "],
            [self.uav_2_value_label, self.mission.uav_2.uav_location.label],
            [QLabel(), "Move UAV 2 To: "],
            [self.move_uav_2_box],
            [QPushButton(), "Move", self.move_uav, 2]
        ])

        #  UGV Location and Moving
        self.ugv_value_label = QLabel(self.mission.ugv_location.label)
        self.move_ugv_box = QLineEdit()
        self.add_custom_h_box_to_ui([
            [QLabel(), "UGV Location: "],
            [self.ugv_value_label, self.mission.ugv_location.label],
            [QLabel(), "Move UGV To: "],
            [self.move_ugv_box],
            [QPushButton(), "Move", self.move_ugv]
        ])

        #  Total Cost
        self.total_value_label = QLabel()
        self.add_custom_h_box_to_ui([
            [QLabel(), "Total: "],
            [self.total_value_label, "0"]
        ])

        #  Adding UI to Main Window
        ui_widget = QWidget()
        ui_widget.setLayout(self.ui_layout)
        self.main_panel.addWidget(ui_widget, 1, 0, 1, 1)
        self.ui_layout.addStretch(1)
        self.ui_layout.setSpacing(0)

    def add_custom_h_box_to_ui(self, widget_list):
        """
        Add an horizontal box to the UI with associated widget lists

        Params:
            widget_list - A list of lists containing the widgets including
                [QLabel(), label_string],
                [QLineEdit()], OR
                [QPushButtom(), button_string, button_function]
        """

        horizontal_layout = QHBoxLayout()
        for list in widget_list:
            new_widget = list[0]
            if type(new_widget) is QLabel:
                new_widget.setText(list[1])
                new_widget.setStyleSheet("QLabel { color: black; alignment: center}")
            elif type(new_widget) is QLineEdit:
                pass
            elif type(new_widget) is QPushButton:
                new_widget.setText(list[1])
                if len(list) == 4:
                    new_widget.clicked.connect(lambda: list[2](list[3]))
                else:
                    new_widget.clicked.connect(list[2])
            else:
                continue
            horizontal_layout.addWidget(new_widget)

        horizontal_widget = QWidget()
        horizontal_widget.setLayout(horizontal_layout)
        self.ui_layout.addWidget(horizontal_widget)
        horizontal_layout.addStretch(1)
        horizontal_layout.setSpacing(1)

    def get_chosen_hex(self, hex_label: str):
        """
        Gets a valid chosen hex and update the UI with its information

        Parameters:
            hex_label (str): The label for the hex to find
        """

        if len(hex_label) == 2 and hex_label.isalpha:
            chosen_hex = self.mission.get_chosen_hex(hex_label)
            if chosen_hex is not None:
                if chosen_hex.ai_1_queried:
                    self.ai_1_query_value_label.setText(str(chosen_hex.ai_1_confidence))
                else:
                    self.ai_1_query_value_label.setText("Hex %s not yet estimated by AI 1" % (hex_label))
                if chosen_hex.ai_2_queried:
                    self.ai_2_query_value_label.setText(str(chosen_hex.ai_2_confidence))
                else:
                    self.ai_2_query_value_label.setText("Hex %s not yet estimated by AI 2" % (hex_label))
                if chosen_hex.human_queried:
                    self.human_query_value_label.setText(str(chosen_hex.human_confidence))
                else:
                    self.human_query_value_label.setText("Hex %s not yet estimated by humans" % (hex_label))
                self.terrain_value_label.setText(chosen_hex.terrain)
        self.mission_report.setText(self.mission.current_log)

    def query_ai(self, num_uav: int):
        """
        Provide the AI cost and increase the total

        Parameters:
            num_uav (int): The number of the uav to move
        """

        self.mission_report.setText("")
        if self.mission.query_ai(num_uav):
            if num_uav == 1:
                self.ai_1_query_value_label.setText(str(self.mission.selected_hexagon.ai_1_confidence))
            elif num_uav == 2:
                self.ai_2_query_value_label.setText(str(self.mission.selected_hexagon.ai_2_confidence))
            self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

    def query_human(self):
        """
        Provide the human cost and increase the total
        """

        self.mission_report.setText("")
        if self.mission.query_human():
            self.human_query_value_label.setText(str(self.mission.selected_hexagon.human_confidence))
            self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

    def move_uav(self, num_uav: int):
        """
        Move the UAV to a valid adjacent location and increase the cost

        Parameters:
            num_uav (int): The number of the uav to move
        """

        uav_box_text = ""
        label = None
        uav = None
        if num_uav == 1:
            uav_box_text = self.move_uav_1_box.text().upper()
            label = self.uav_1_value_label
            uav = self.mission.uav_1
        elif num_uav == 2:
            uav_box_text = self.move_uav_2_box.text().upper()
            label = self.uav_2_value_label
            uav = self.mission.uav_2
        self.mission_report.setText("")
        old_uav_location = uav.uav_location.label
        hex = self.mission.move_uav(uav, uav_box_text)
        if hex is not None:
            self.set_hex_color(old_uav_location, uav_box_text, f'uav{uav.uav_number}')
            label.setText(uav_box_text)
            self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

    def move_ugv(self):
        """
        Move the UGV to a valid adjacent location and increase the cost
        """

        self.mission_report.setText("")
        ugv_box_text = self.move_ugv_box.text().upper()
        old_ugv_location = self.mission.ugv_location.label
        status = self.mission.move_ugv(ugv_box_text)
        if status != -1 and status != 0:
            self.set_hex_color(old_ugv_location, ugv_box_text, "ugv")
        if status == 2:
            self.ugv_value_label.setText(ugv_box_text)
        self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

    def set_hex_color(self,  from_hex: str, to_hex: str, moving_vehicle: str):
        hexes = self.hex_map.scene.items()
        for hex in hexes:
            if type(hex).__name__ == "HexagonItem":
                if hex.label == to_hex:
                    if moving_vehicle == "ugv":
                        hex.ugv_present = True
                        hex.setBrush(QColor("red"))
                    else:
                        if moving_vehicle == "uav1":
                            hex.uav_1_present = True
                        else:
                            hex.uav_2_present = True
                        hex.setBrush(QColor("green"))
                elif hex.label == from_hex:
                    if moving_vehicle == "ugv":
                        hex.ugv_present = False
                        if hex.uav_1_present or hex.uav_2_present:
                            hex.setBrush(QColor("green"))
                        else:
                            hex.setBrush(QColor(0, 0, 0, 127))
                    else:
                        if moving_vehicle == "uav1":
                            hex.uav_1_present = False
                        else:
                            hex.uav_2_present = False
                        if hex.ugv_present:
                            hex.setBrush(QColor("red"))
                        elif hex.uav_1_present or hex.uav_2_present:
                            hex.setBrush(QColor("green"))
                        else:
                            hex.setBrush(QColor(0, 0, 0, 127))


    class HexagonItem(QGraphicsPolygonItem):
        def __init__(self, center: QPointF, radius: int, label: str, renderer, parent=None):
            """
            Creates the HexagonItem object

            Parameters:
                center (QPointF): The central point of the hex
                radius (int): The radius of the hex
                label (str): The label to be put in the middle of the hex
                renderer (Renderer): A local reference to the Renderer object
            """
            super().__init__(parent)
            self.label = label
            self.renderer = renderer
            self.uav_1_present = False
            self.uav_2_present = False
            self.ugv_present = False

            points = []
            for i in range(6):
                angle = 2 * 3.14159 * i / 6
                x = center.x() + radius * math.cos(angle)
                y = center.y() + radius * math.sin(angle)
                points.append(QPointF(x, y))
            polygon = QPolygonF(points)
            self.setPolygon(polygon)

            self.textItem = QGraphicsTextItem(self)
            self.textItem.setHtml('<center>%s</center>' % self.label)
            self.textItem.setTextWidth(self.boundingRect().width())
            rect = self.textItem.boundingRect()
            rect.moveCenter(self.boundingRect().center())
            self.textItem.setPos(rect.topLeft())

            self.setBrush(QColor(0, 0, 0, 127))
            self.setPen(QColor(255, 255, 255, 127))

            if label == renderer.mission.uav_1.uav_location.label:
                self.uav_1_present = True
                self.uav_2_present = True
                self.ugv_present = True
                self.setBrush(QColor("red"))

        def mousePressEvent(self, event):
            """
            The function called if the hex is clicked with the LMB

            Parameters:
                event (QGraphicsSceneMouseEvent): A mouse event that calls this function
            """
            if event.button() == Qt.MouseButton.LeftButton:
                Renderer.get_chosen_hex(self.renderer, hex_label=self.label)

    class HexagonMap(QGraphicsView):
        def __init__(self, renderer, labels: list[str]):
            """
            Creates the HexagonMap object

            Parameters:
                renderer (Renderer): A local reference to the Renderer object
                labels (list[str]): A list of labels to be put in the middle of the hexes
            """
            super().__init__()

            self.scene = QGraphicsScene(self)
            self.setScene(self.scene)
            self.renderer = renderer

            self.radius = 30
            self.rows = 10
            self.cols = 10
            self.labels = labels
            self.create_hexagons()

        def create_hexagons(self):
            """
            Creates and adds each of the HexagonItems to the scene
            """
            count = 0
            for row in range(self.rows):
                for col in range(self.cols):
                    x = col * self.radius * 1.5
                    y = row * self.radius * 1.732
                    if col % 2 == 1:
                        y += self.radius * 0.866

                    center = QPointF(x, y)
                    hexagon = Renderer.HexagonItem(center, self.radius, self.labels[count], self.renderer)
                    self.scene.addItem(hexagon)
                    count += 1

if __name__ == "__main__":
    pyqt_app = QApplication([])
    renderer = Renderer()
    renderer.render()
    pyqt_app.exec()
