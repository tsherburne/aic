class NetworkEdge():
    def __init__(self, data):
        """
        Constructor for the NetworkEdge object

        Params:
            data - The JSON edge object
        """

        self.origin = data['from']
        self.destination = data['to']
        self.landmine_present = data['landmine_present']
        self.landmine_found = False
        self.landmine_cleared = False
        self.ai_estimate = data['ai_estimate']
        self.human_estimate = data['human_estimate']
        self.terrain_type = data['terrain_type']
        self.ai_queried = False
        self.human_queried = False
        self.uav_scanned = False

    def __eq__(self, other) -> bool:
        """
        Checks if two edges are equal

        Params:
            other - The object to compare to this NetworkEdge

        Returns:
            bool - True if this and the other objects are equal
        """

        if isinstance(other, NetworkEdge):
            return ((self.origin == other.origin and self.destination == other.destination) or
                    (self.origin == other.destination and self.destination == other.origin))
        else:
            return False

    def __hash__(self) -> int:
        """
        Hash function for NetworkEdge

        Returns:
            int - The hash code for the NetworkEdge
        """

        return hash((self.origin, self.destination, self.ai_estimate, self.human_estimate))
