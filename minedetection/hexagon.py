class Hexagon():
    def __init__(self, label: str, terrain: str, ai_confidence: float, human_confidence: float, mine_present: int):
        """
        Creates a Hexagon object

        Parameters:
            label (str): The hexagon's label
            terrain (str): Terrain type associated with the hex
            ai_confidence (float): The AI confidence a mine is present
            human_confidence (float): The human confidence a mine is present
            mine_present (int): 1 if a mine is present within this hex, 0 otherwise
        """
        self.label = label
        self.terrain = terrain
        self.ai_confidence = ai_confidence
        self.human_confidence = human_confidence
        if mine_present == 1:
            self.landmine_present = True
        else:
            self.landmine_present = False
        self.landmine_found = False
        self.landmine_cleared = False
        self.ai_queried = False
        self.human_queried = False
        self.uav_scanned = False

    def __eq__(self, other) -> bool:
        """
        Checks if two hexagons are equal

        Params:
            other - The object to compare to this Hexagon

        Returns:
            bool - True if this and the other objects are equal
        """

        if isinstance(other, Hexagon):
            return self.label == other.label and self.terrain == other.terrain and self.ai_confidence == other.ai_confidence and self.human_confidence == other.human_confidence and self.landmine_present == other.landmine_present
        else:
            return False

    def __hash__(self) -> int:
        """
        Hash function for NetworkEdge

        Returns:
            int - The hash code for the NetworkEdge
        """

        return hash((self.label, self.terrain, self.ai_confidence, self.human_confidence, self.landmine_present))