import json
import logging
import datetime
import os
from hexagon import Hexagon


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
            self.__hexagons = []
            self.__selected_hexagon = None
            for label in data.keys():
                if label != "mission":
                    content = data[label]
                    self.__hexagons.append(Hexagon(label, content['Terrain'], content['AI Confidence'], content['Human Confidence'], content['Mine']))
            data = data['mission']
            self.__start_node = data['start']
            self.__end_node = data['end']
            self.__human_estimate_time = data["human estimate time"]
            self.__ai_estimate_time = data["AI estimate time"]
            self.__ugv_traversal_time = data["UGV traversal time"]
            self.__ugv_clear_time = data["UGV clear time"]
            self.__uav_traversal_time = data["UAV traversal time"]
            self.__ugv_location = self.__hexagons[0]
            self.__uav_location = self.__hexagons[0]
            self.__hexagons[0].landmine_present = False
            self.__hexagons[0].uav_scanned = True
        self.__total = 0

    @property
    def hexagons(self) -> list[Hexagon]:
        """
        Gets the hexagons field

        Returns:
            Set[Hexagon] - The hexagons
        """
        return self.__hexagons

    @property
    def selected_hexagon(self) -> Hexagon:
        """
        Gets the selected_hexagon field

        Returns:
            Hexagon - The selected hexagon
        """
        return self.__selected_hexagon

    @selected_hexagon.setter
    def selected_hexagon(self, hex):
        """
        Sets the selected_hexagon field

        Parameters:
            hex - The hexagon to make current
        """
        self.__selected_hexagon = hex

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
    def ugv_location(self) -> Hexagon:
        """
        Gets the ugv_location field

        Returns:
            str - The ugv location
        """
        return self.__ugv_location

    @property
    def uav_location(self) -> Hexagon:
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

    def query_ai(self) -> bool:
        """
        Check if there is a selected hex scanned by the UAV, and query the AI if so

        Returns:
            True if the AI was queried
        """

        if self.selected_hexagon is not None and self.selected_hexagon.uav_scanned and not self.selected_hexagon.ai_queried:
            self.selected_hexagon.ai_queried = True
            self.__increment_total(self.ai_estimate_time)
            self.__log_message("AI queried for hex %s. The estimate was %s." % (self.selected_hexagon.label, self.selected_hexagon.ai_confidence))
            return True
        else:
            self.__log_message("AI could not be queried for hex %s. This occurs if a hex is not selected, the AI has already been queried, or the UAV has not scanned the current hex." % (self.selected_hexagon.label))
            return False

    def query_human(self) -> bool:
        """
        Check if there is a selected hex scanned by the UAV, and query the AI if so

        Returns:
            True if the AI was queried
        """

        if self.selected_hexagon is not None and self.selected_hexagon.uav_scanned and not self.selected_hexagon.human_queried:
            self.selected_hexagon.human_queried = True
            self.__increment_total(self.human_estimate_time)
            self.__log_message("Human queried for hex %s. The estimate was %s." % (self.selected_hexagon.label, self.selected_hexagon.human_confidence))
            return True
        else:
            self.__log_message("Human could not be queried for hex %s. This occurs if an hex is not selected, the human has already been queried, or the UAV has not scanned the current hex." % (self.selected_hexagon.label))
            return False

    def move_ugv(self, destination_node: str) -> int:
        """
        Move the UGV to a valid adjacent location and increase the cost

        Params:
            destination_node (str): The destination node for the UGV to move to

        Returns:
            0 if a landmine was found, 1 if a landmine was cleared, and -1 if the UGV could not be moved
        """

        for hex in self.hexagons:
            if hex.label == destination_node and self.__is_adjacent(self.ugv_location, hex):
                if hex.landmine_present and not hex.landmine_found:
                    self.__increment_total(self.ugv_traversal_time)
                    hex.landmine_found = True
                    self.__log_message("Landmine detected along hex %s. UGV returned to orginal passageway. Move UGV again to clear landmine and complete traversal." % destination_node)
                    return 0
                elif hex.landmine_present and hex.landmine_found:
                    self.__increment_total(self.ugv_clear_time)
                    hex.landmine_cleared = True
                    hex.landmine_present = False
                    self.__ugv_location = hex
                    self.__log_message("Landmine cleared. UGV moved to passage %s." % destination_node)
                    if destination_node == self.end_node:
                        self.__log_message("MISSION SUCCESS")
                    return 1
                else:
                    self.__increment_total(self.ugv_traversal_time)
                    self.__ugv_location = hex
                    self.__log_message("UGV moved to passage %s." % destination_node)
                    if destination_node == self.end_node:
                        self.__log_message("MISSION SUCCESS")
                    return 2
        self.__log_message("UGV could not be moved to passage %s. Please check the destination exists and is adjacent to the UGV's current location" % destination_node)
        return -1

    def move_uav(self, destination_node: str) -> Hexagon:
        """
        Move the UAV to a valid adjacent location and increase the cost

        Params:
            destination_node (str): The destination node for the UAV to move to

        Returns:
            The hex scanned by the UAV or None otherwise
        """

        for hex in self.hexagons:
            if hex.label == destination_node and self.__is_adjacent(self.uav_location, hex):
                self.__increment_total(self.uav_traversal_time)
                self.__uav_location = hex
                hex.uav_scanned = True
                self.__log_message("UAV moved to passage %s. Estimates can now be obtained for hex %s." % (destination_node, destination_node))
                return hex
        self.__log_message("UAV could not be moved to passage %s. Please check the destination exists and is adjacent to the UAV's current location" % destination_node)
        return None
    
    def __is_adjacent(self, current_hex: Hexagon, destination_hex: Hexagon) -> bool:
        """
        Checks whether or not two hexagons are adjacent to one another
        
        Parameters:
            current_hex (Hexagon): The current hexagon selected
            destination_hex (Hexagon): The hexagon to check adjacency to the current
        
        Returns:
            True if the current_hex and destination_hex are adjacent
        """
        if current_hex == destination_hex:
            return False
        letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3,'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9}
        current_code = (letter_map[current_hex.label[0]], letter_map[current_hex.label[1]])
        destination_code = (letter_map[destination_hex.label[0]], letter_map[destination_hex.label[1]])
        return (
            (current_code[0] == destination_code[0] and (current_code[1] + 1 - destination_code[1]) in [0, 1, 2]) or
            (current_code[1] == destination_code[1] and (current_code[0] + 1 - destination_code[0]) in [0, 1, 2]) or
            (current_code[1] % 2 == 0 and current_code[0] - 1 == destination_code[0] and (current_code[1] + 1 - destination_code[1]) in [0, 1, 2]) or
            (current_code[1] % 2 == 1 and current_code[0] + 1 == destination_code[0] and (current_code[1] + 1 - destination_code[1]) in [0, 1, 2])
        )

    def get_chosen_hex(self, label: str) -> Hexagon:
        """
        Gets a valid chosen hex and update the UI with its information

        Params:
            label : str - The label of the hex to be obtained

        Returns:
            The hex that was chosen or None otherwise
        """

        for hex in self.hexagons:
            if hex.label == label:
                self.__selected_hexagon = hex
                self.__log_message("Selected hex %s" % (hex.label))
                return hex
        self.__log_message("Hex %s could not be found" % (label))
        return None

    def __log_message(self, msg: str):
        """
        Logs a message to the log file
        
        Params:
            msg (str): The message to be logged
        """

        self.__current_log = msg
        logging.log(level=logging.INFO, msg=msg)
