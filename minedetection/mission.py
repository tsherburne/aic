import json
import logging
import datetime
import os
from network_edge import NetworkEdge
from typing import Set


class Mission():
    def __init__(self, config_filename: str):
        """
        Constructor for the Mission object

        Params:
            data - The JSON mission object
        """

        log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
        filename=f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        log_filename = os.path.join(log_dir, filename)
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s %(message)s'
        )
        self.__current_log = ""
        with open('../config/' + config_filename) as json_data:
            data = json.load(json_data)
            self.__network_edges = set()
            self.__selected_edge = None
            for edge in data['edges']:
                self.__network_edges.add(NetworkEdge(edge))
            data = data['mission']
            self.__start_node = data['start']
            self.__end_node = data["end"]
            self.__human_estimate_time = data["human estimate time"]
            self.__ai_estimate_time = data["AI estimate time"]
            self.__ugv_traversal_time = data["UGV traversal time"]
            self.__ugv_clear_time = data["UGV clear time"]
            self.__uav_traversal_time = data["UAV traversal time"]
            self.__ugv_location = self.start_node.upper()
            self.__uav_location = self.start_node.upper()
        self.__total = 0

    @property
    def network_edges(self) -> Set[NetworkEdge]:
        """
        Gets the network_edges field

        Returns:
            Set[NetworkEdge] - The network edges
        """
        return self.__network_edges

    @property
    def selected_edge(self) -> NetworkEdge:
        """
        Gets the selected_edge field

        Returns:
            NetworkEdge - The selected edge
        """
        return self.__selected_edge

    @selected_edge.setter
    def selected_edge(self, edge):
        """
        Sets the selected_edge field

        Parameters:
            NetworkEdge - The edge to make current
        """
        self.__selected_edge = edge

    @property
    def start_node(self) -> str:
        """
        Gets the start_node field

        Returns:
            str - The start node
        """
        return self.__start_node

    @property
    def end_node(self) -> str:
        """
        Gets the end_node field

        Returns:
            str - The end node
        """
        return self.__end_node

    @property
    def human_estimate_time(self) -> int:
        """
        Gets the human_estimate_time field

        Returns:
            int - The human estimate time
        """
        return self.__human_estimate_time

    @property
    def ai_estimate_time(self) -> int:
        """
        Gets the ai_estimate_time field

        Returns:
            int - The ai estimate time
        """
        return self.__ai_estimate_time

    @property
    def ugv_traversal_time(self) -> int:
        """
        Gets the ugv_traversal_time field

        Returns:
            int - The ugv traversal time
        """
        return self.__ugv_traversal_time

    @property
    def ugv_clear_time(self) -> int:
        """
        Gets the ugv_clear_time field

        Returns:
            int - The ugv clear time
        """
        return self.__ugv_clear_time

    @property
    def uav_traversal_time(self) -> int:
        """
        Gets the ugv_traversal_time field

        Returns:
            int - The uav traversal time
        """
        return self.__uav_traversal_time

    @property
    def ugv_location(self) -> str:
        """
        Gets the ugv_location field

        Returns:
            str - The ugv location
        """
        return self.__ugv_location

    @property
    def uav_location(self) -> str:
        """
        Gets the uav_location field

        Returns:
            str - The uav location
        """
        return self.__uav_location

    @property
    def total(self) -> int:
        """
        Gets the total field

        Returns:
            int - The current mission total
        """
        return self.__total

    @property
    def current_log(self) -> str:
        """
        Gets the current log message

        Returns:
            str - The current log message
        """
        return self.__current_log

    def __increment_total(self, value):
        """
        Increase total by value

        Params:
            int - The value to increase total by
        """
        self.__total += value

    def query_ai(self):
        """
        Check if there is a selected edge scanned by the UAV, and query the AI if so

        Returns:
            True if the AI was queried
        """

        if self.selected_edge is not None and self.selected_edge.uav_scanned and not self.selected_edge.ai_queried:
            self.selected_edge.ai_queried = True
            self.__increment_total(self.ai_estimate_time)
            self.__log_message("AI queried for edge %s, %s. The estimate was %s." % (self.selected_edge.origin, self.selected_edge.destination, self.selected_edge.ai_estimate))
            return True
        else:
            self.__log_message("AI could not be queried for edge %s, %s. This occurs if an edge is not selected, the AI has already been queried, or the UAV has not scanned the current edge." % (self.selected_edge.origin, self.selected_edge.destination))
            return False

    def query_human(self):
        """
        Check if there is a selected edge scanned by the UAV, and query the AI if so

        Returns:
            True if the AI was queried
        """

        if self.selected_edge is not None and self.selected_edge.uav_scanned and not self.selected_edge.human_queried:
            self.selected_edge.human_queried = True
            self.__increment_total(self.human_estimate_time)
            self.__log_message("Human queried for edge %s, %s. The estimate was %s." % (self.selected_edge.origin, self.selected_edge.destination, self.selected_edge.human_estimate))
            return True
        else:
            self.__log_message("Human could not be queried for edge %s, %s. This occurs if an edge is not selected, the human has already been queried, or the UAV has not scanned the current edge." % (self.selected_edge.origin, self.selected_edge.destination))
            return False

    def move_ugv(self, destination_node: str):
        """
        Move the UGV to a valid adjacent location and increase the cost

        Params:
            destination_node : str - The destination node for the UGV to move to

        Returns:
            int - 0 if a landmine was found, 1 if a landmine was cleared, and -1 if the UGV could not be moved
        """

        for edge in self.__network_edges:
            if (
                (self.ugv_location != destination_node) and
                (self.ugv_location == edge.origin or self.ugv_location == edge.destination) and
                (destination_node == edge.origin or destination_node == edge.destination)
            ):
                if edge.landmine_present and not edge.landmine_found:
                    self.__increment_total(self.ugv_traversal_time)
                    edge.landmine_found = True
                    self.__log_message("Landmine detected along edge %s, %s. UGV returned to orginal passageway. Move UGV again to clear landmine and complete traversal." % (self.ugv_location, destination_node))
                    return 0
                elif edge.landmine_present and edge.landmine_found:
                    self.__increment_total(self.ugv_clear_time)
                    edge.landmine_cleared = True
                    edge.landmine_present = False
                    self.__ugv_location = destination_node
                    self.__log_message("Landmine cleared. UGV moved to passage %s." % destination_node)
                    if destination_node == self.end_node:
                        self.__log_message("MISSION SUCCESS")
                    return 1
                else:
                    self.__increment_total(self.ugv_traversal_time)
                    self.__ugv_location = destination_node
                    self.__log_message("UGV moved to passage %s." % destination_node)
                    if destination_node == self.end_node:
                        self.__log_message("MISSION SUCCESS")
                    return 2
        self.__log_message("UGV could not be moved to passage %s. Please check the destination exists and is adjacent to the UGV's current location" % destination_node)
        return -1

    def move_uav(self, destination_node: str):
        """
        Move the UAV to a valid adjacent location and increase the cost

        Params:
            destination_node : str - The destination node for the UAV to move to

        Returns:
            edge : NetworkEdge - the edge scanned by the UAV or None otherwise
        """

        for edge in self.network_edges:
            if (
                (self.uav_location != destination_node) and
                (self.uav_location == edge.origin or self.uav_location == edge.destination) and
                (destination_node == edge.origin or destination_node == edge.destination)
            ):
                self.__increment_total(self.uav_traversal_time)
                self.__uav_location = destination_node
                edge.uav_scanned = True
                self.__log_message("UAV moved to passage %s. Estimates can now be obtained for edge %s, %s." % (destination_node, edge.origin, edge.destination))
                return edge
        self.__log_message("UAV could not be moved to passage %s. Please check the destination exists and is adjacent to the UAV's current location" % destination_node)
        return None

    def get_chosen_edge(self, point_a: str, point_b: str):
        """
        Gets a valid chosen edge and update the UI with its information

        Params:
            point_a : str - The start point for the edge to be gotten
            point_b : str - The end point for the edge to be gotten

        Returns:
            edge : NetworkEdge - the edge that was chosen or None otherwise
        """

        for edge in self.network_edges:
            if (
                (point_a == edge.origin or point_a == edge.destination) and
                (point_b == edge.origin or point_b == edge.destination)
            ):
                self.__selected_edge = edge
                self.__log_message("Selected edge %s, %s" % (point_a, point_b))
                return edge
        self.__log_message("Edge %s, %s could not be found" % (point_a, point_b))
        return None

    def __log_message(self, msg: str):
        """
        Logs a message to the log file
        
        Params:
            msg : str - The message to be logged
        """

        self.__current_log = msg
        logging.log(level=logging.INFO, msg=msg)
