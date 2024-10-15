import matplotlib.pyplot as plt
import networkx as nx
import pyqtgraph as pg

from PyQt6.QtWidgets import QMainWindow, QApplication, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mission import Mission


class Renderer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mission = Mission("example_scenario.json")

        self.show_flag = 0
        self.win_width = 1400
        self.win_height = 900

        self.setWindowTitle('Scenario')
        self.setFixedWidth(self.win_width)
        self.setFixedHeight(self.win_height)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'w')
        self.background = "background-color: white; color: white;"
        self.setStyleSheet("QMainWindow {background: 'white';}")
        self.main_panel = QGridLayout()
        self.initialize_graph_view()
        self.main_panel.addWidget(self.canvas, 0, 0, 1, 1)
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

    def initialize_graph_view(self):
        """
        Initializes the graph at the top of the window using networkx
        """

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        G = nx.Graph()
        edges = [(edge.origin, edge.destination) for edge in self.mission.network_edges]
        G.add_edges_from(edges)
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=700)
        nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
        nx.draw_networkx_edges(G, pos, edgelist=edges, width=6)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    def initialize_ui_view(self):
        """
        Initialize the UI at the bottom of the window
        """
        self.ui_layout = QVBoxLayout()

        #  Mission Details
        self.add_custom_h_box_to_ui([
            [QLabel(), "Mission Details: Start Node - %s, End Node - %s, UAV Traversal Time - %s, Cost of Human Estimate - %s, Cost of AI Estimate - %s, UGV Traversal Time - %s, UGV Clear Time - %s" % (self.mission.start_node, self.mission.end_node, self.mission.uav_traversal_time, self.mission.human_estimate_time, self.mission.ai_estimate_time, self.mission.ugv_traversal_time, self.mission.ugv_clear_time)]  # noqa: E501
        ])

        #  Mission Report (Error Reporting)
        self.mission_report = QLabel()
        self.add_custom_h_box_to_ui([
            [self.mission_report, ""]
        ])

        #  Edge Selection
        self.edge_selection_box = QLineEdit()
        self.add_custom_h_box_to_ui([
            [QLabel(), "Enter edge name (i.e. A,B): "],
            [self.edge_selection_box],
            [QPushButton(), "Select Edge", self.get_chosen_edge]
        ])

        #  AI Mine Estimate
        self.ai_query_value_label = QLabel()
        self.add_custom_h_box_to_ui([
            [QLabel(), "AI Mine Estimate: "],
            [self.ai_query_value_label, "N/A"],
            [QPushButton(), "Get AI Estimate", self.query_ai]
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

        #  UAV Location and Moving
        self.uav_value_label = QLabel(self.mission.uav_location)
        self.move_uav_box = QLineEdit()
        self.add_custom_h_box_to_ui([
            [QLabel(), "UAV Location: "],
            [self.uav_value_label, self.mission.uav_location],
            [QLabel(), "Move UAV To: "],
            [self.move_uav_box],
            [QPushButton(), "Move", self.move_uav]
        ])

        #  UGV Location and Moving
        self.ugv_value_label = QLabel(self.mission.ugv_location)
        self.move_ugv_box = QLineEdit()
        self.add_custom_h_box_to_ui([
            [QLabel(), "UGV Location: "],
            [self.ugv_value_label, self.mission.ugv_location],
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
                new_widget.clicked.connect(list[2])
            else:
                print("Not a valid widget type")
                continue
            horizontal_layout.addWidget(new_widget)

        horizontal_widget = QWidget()
        horizontal_widget.setLayout(horizontal_layout)
        self.ui_layout.addWidget(horizontal_widget)
        horizontal_layout.addStretch(1)
        horizontal_layout.setSpacing(1)

    def get_chosen_edge(self):
        """
        Gets a valid chosen edge and update the UI with its information
        """

        self.mission_report.setText("")
        edge = self.edge_selection_box.text().replace(' ', '')
        split_edge = edge.split(',')
        if len(split_edge) == 2 and len(split_edge[0]) == 1 and len(split_edge[1]) == 1 and split_edge[0].isalpha and split_edge[1].isalpha:
            edge_1 = split_edge[0].upper()
            edge_2 = split_edge[1].upper()
            chosen_edge = self.mission.get_chosen_edge(edge_1, edge_2)
            if chosen_edge is not None:
                if chosen_edge.ai_queried:
                    self.ai_query_value_label.setText(str(chosen_edge.ai_estimate))
                else:
                    self.ai_query_value_label.setText("Edge %s, %s not yet estimated by AI" % (edge_1, edge_2))
                if chosen_edge.human_queried:
                    self.human_query_value_label.setText(str(chosen_edge.human_estimate))
                else:
                    self.human_query_value_label.setText("Edge %s, %s not yet estimated by humans" % (edge_1, edge_2))
                self.terrain_value_label.setText(chosen_edge.terrain_type)
        self.mission_report.setText(self.mission.current_log)

    def query_ai(self):
        """
        Provide the AI cost and increase the total
        """

        self.mission_report.setText("")
        if self.mission.query_ai():
            self.ai_query_value_label.setText(str(self.mission.selected_edge.ai_estimate))
            self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

    def query_human(self):
        """
        Provide the human cost and increase the total
        """

        self.mission_report.setText("")
        if self.mission.query_human():
            self.human_query_value_label.setText(str(self.mission.selected_edge.human_estimate))
            self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

    def move_uav(self):
        """
        Move the UAV to a valid adjacent location and increase the cost
        """

        self.mission_report.setText("")
        uav_box_text = self.move_uav_box.text().upper()
        edge = self.mission.move_uav(uav_box_text)
        if edge is not None:
            self.uav_value_label.setText(uav_box_text)
            self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

    def move_ugv(self):
        """
        Move the UGV to a valid adjacent location and increase the cost
        """

        self.mission_report.setText("")
        ugv_box_text = self.move_ugv_box.text().upper()
        status = self.mission.move_ugv(ugv_box_text)
        if status == 2:
            self.ugv_value_label.setText(ugv_box_text)
        self.total_value_label.setText(str(self.mission.total))
        self.mission_report.setText(self.mission.current_log)

if __name__ == "__main__":
    pyqt_app = QApplication([])
    renderer = Renderer()
    renderer.render()
    pyqt_app.exec()
