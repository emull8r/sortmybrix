import json
import pathlib
import csv

class Parts:
    """Represents a group of LEGO parts in the user's inventory"""
    def __init__(self, Part, Color, Quantity):
        self.Part = Part
        self.Color = Color
        self.Quantity = Quantity
    
    def __repr__(self):
        return f"Parts(Part={self.Part}, Color={self.Color}, Quantity={self.Quantity})"

class Containers:
    """Represents a group of storage containers for LEGO parts"""
    def __init__(self, name, length, width, height, quantity):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.quantity = quantity
    
    def __repr__(self):
        return f"Containers(name={self.name}, length={self.length}, width={self.width}, height={self.height}, quantity={self.quantity})"

class Container:
    """Represents an individual storage container for LEGO parts"""
    def __init__(self, name, length, width, height, parts=None):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.parts = parts if parts is not None else set()
    
    def __repr__(self):
        return f"Container(name={self.name}, length={self.length}, width={self.width}, height={self.height}, parts={self.parts})"
    
    def calculate_remaining_space(self, parts_dict):
        """Calculate remaining space in the container
        Arguments:
        parts_dict: Dictionary of parts with their dimensions
        Returns:
        remaining_space: Available volume in the container (in cubic centimeters)
        """
        container_volume = self.length * self.width * self.height
        used_volume = 0
        
        for part in self.parts:
            part_id = part.Part
            if part_id not in parts_dict:
                continue
            quantity = part.Quantity
            part_volume = parts_dict[part_id]['width'] * parts_dict[part_id]['height'] * parts_dict[part_id]['depth']
            part_volume = part_volume * 0.8**3  # Convert studs to centimeters
            used_volume += part_volume * quantity
        
        remaining_space = container_volume - used_volume
        return max(remaining_space, 0)  # Return 0 if container is overfilled
    
    def calculate_similarity_score(self, parts_dict, new_part):
        """Calculate similarity score for a new part compared to existing parts in container
        Arguments:
        parts_dict: Dictionary of parts with their dimensions and category
        new_part: Parts object to evaluate
        Returns:
        score: Similarity score (higher is more similar). Scored by size, color, then category.
        """
        if not self.parts or new_part.Part not in parts_dict:
            return 0
        
        new_part_info = parts_dict[new_part.Part]
        new_volume = new_part_info['width'] * new_part_info['height'] * new_part_info['depth']
        new_category = new_part_info['category_id']
        
        total_score = 0
        max_possible_score = 0
        
        for existing_part in self.parts:
            if existing_part.Part not in parts_dict:
                continue
            
            max_possible_score += 100
            part_score = 0
            
            # Size similarity (0-50 points): Based on volume difference
            existing_part_info = parts_dict[existing_part.Part]
            existing_volume = existing_part_info['width'] * existing_part_info['height'] * existing_part_info['depth']
            
            if max(new_volume, existing_volume) == 0:
                # Both volumes are 0, perfect match in size
                size_score = 50
            else:
                volume_ratio = min(new_volume, existing_volume) / max(new_volume, existing_volume)
                size_score = volume_ratio * 50
            part_score += size_score
            
            # Color similarity (0-30 points): Exact match or no match
            if new_part.Color == existing_part.Color:
                color_score = 30
            else:
                color_score = 0
            part_score += color_score
            
            # Category similarity (0-20 points): Exact match or no match
            existing_category = existing_part_info['category_id']
            if new_category == existing_category:
                category_score = 20
            else:
                category_score = 0
            part_score += category_score
            
            total_score += part_score
        
        # Return average score across all existing parts
        if max_possible_score == 0:
            return 0
        return total_score / max_possible_score
    
    def add_parts(self, parts_dict, new_part):
        """Add a Parts object to the container, fitting as many as possible
        
        Arguments:
        parts_dict: Dictionary of parts with their dimensions
        new_part: Parts object to add
        
        Returns:
        remainder: A new Parts object with the quantity that couldn't fit, or None if all fit
        """
        if new_part.Part not in parts_dict:
            return new_part
        
        part_volume = parts_dict[new_part.Part]['width'] * parts_dict[new_part.Part]['height'] * parts_dict[new_part.Part]['depth']
        part_volume = part_volume * 0.8**3  # Convert studs to centimeters
        
        quantity_added = 0
        
        # Try to add each individual part
        for i in range(new_part.Quantity):
            remaining_space = self.calculate_remaining_space(parts_dict)
            if remaining_space >= part_volume:
                # Create a temporary part with quantity 1 to add to the set
                temp_part = Parts(Part=new_part.Part, Color=new_part.Color, Quantity=1)
                self.parts.add(temp_part)
                quantity_added += 1
            else:
                # No more space, break out
                break
        
        # Return remainder or None
        if quantity_added < new_part.Quantity:
            remainder_quantity = new_part.Quantity - quantity_added
            return Parts(Part=new_part.Part, Color=new_part.Color, Quantity=remainder_quantity)
        
        return None


def parse_master_parts_file(master_parts_file, config):
    """ Parse the master parts file and return a dictionary of parts
    Arguments:
    master_parts_file: TXT file downloaded from bricklink, 
    contains the IDs of parts and their physical dimensions and other properties
    Returns:
    parts: Dictionary of parts, where the key is the part ID and the value is a dictionary of the part's properties
    """
    parts_dict = {}
    with open(master_parts_file, 'r', encoding='utf-8') as f:
        line_count = 0
        for line in f:
            if line_count > 2:
                line = line.strip().split('\t')
                category_id = line[0]
                category_name = line[1]
                number = line[2]
                #name = line[3]
                alternate_item_number = line[4]
                dimensions = line[5]
                default_dimension = config['default_dimension']
                width = default_dimension
                height = default_dimension
                depth = default_dimension
                if dimensions != '? x ? x ?':
                    dimensions = dimensions.split('x')
                    # dimensions are in centimeters
                    width = float(dimensions[0].strip())
                    height = float(dimensions[1].strip())
                    depth = float(dimensions[2].strip())
                parts_dict[number] = {"category_id": category_id,
                                      "category_name": category_name,
                                    "alternate_item_number": alternate_item_number,
                                    "width": width,
                                    "height": height,
                                    "depth": depth}
            line_count += 1
    return parts_dict

def parse_user_parts_file(user_parts_file):
    """Parse the user parts CSV file"""
    parts_list = []
    with open(user_parts_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            part = Parts(Part=row['Part'], Color=int(row['Color']), Quantity=int(row['Quantity']))
            parts_list.append(part)
    return parts_list

def parse_containers_csv(containers_file):
    """Parse the containers CSV file
    Arguments:
    containers_file: CSV file with columns: Name, Quantity, Length, Width, Height (in inches)
    Returns:
    container_list: List of Container namedtuples with dimensions converted to centimeters
    """
    container_list = []
    with open(containers_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['Name']
            quantity = int(row['Quantity'])
            # Convert inches to centimeters
            length = float(row['Depth']) * 2.54
            width = float(row['Width']) * 2.54
            height = float(row['Height']) * 2.54
            container_list.append(Containers(name=name, length=length, width=width, height=height, quantity=quantity))
    return container_list

def expand_containers(containers_list):
    """Convert a list of Containers objects into individual Container objects
    Arguments:
    containers_list: List of Containers objects with quantities
    Returns:
    expanded_containers: List of individual Container objects (one per quantity)
    """
    expanded_containers = []
    for containers in containers_list:
        for i in range(containers.quantity):
            container = Container(
                name=f"{containers.name} {i+1}",
                length=containers.length,
                width=containers.width,
                height=containers.height
            )
            expanded_containers.append(container)
    return expanded_containers

def sort(parts_list, parts_dict, containers):
    """Sort parts into containers based on similarity and remaining space
    
    Arguments:
    parts_list: List of Parts objects to sort
    parts_dict: Dictionary of part information
    containers: List of Container objects
    
    Returns:
    sorted_containers: List of Container objects with sorted parts
    unsorted_parts: List of Parts objects that could not be sorted into any container
    """
    # step 1: sort containers from smallest to largest
    containers.sort(key=lambda c: c.length * c.width * c.height)
    # step 2: sort parts from smallest to largest (skip parts not in dict)
    parts_list.sort(key=lambda p: parts_dict[p.Part]['width'] * parts_dict[p.Part]['height'] * parts_dict[p.Part]['depth'] if p.Part in parts_dict else float('inf'))
    
    unsorted_parts = []
    
    # step 3: try to fit each part into the best container
    for part in parts_list:
        if part.Part not in parts_dict:
            unsorted_parts.append(part)
            continue
            
        best_container = None
        best_score = -1
        for container in containers:
            if container.calculate_remaining_space(parts_dict) <= 0:
                continue
            score = container.calculate_similarity_score(parts_dict, part)
            if score > best_score:
                best_score = score
                best_container = container
        if best_container is not None:
            remainder = best_container.add_parts(parts_dict, part)
            if remainder is not None:
                parts_list.insert(0, remainder)
        else:
            unsorted_parts.append(part)
    
    return containers, unsorted_parts

def calculate_total_volume_of_parts(parts_list, parts_dict):
    """Calculate the total volume of parts in the user's inventory"""
    total_volume = 0
    for part in parts_list:
        part_id = part.Part
        if part_id not in parts_dict:
            continue
        quantity = part.Quantity
        part_volume_in_studs = parts_dict[part_id]['width'] * parts_dict[part_id]['height'] * parts_dict[part_id]['depth']
        part_volume = part_volume_in_studs * 0.8**3
        total_volume += part_volume * quantity
    return total_volume

def load_config(config_file="config.json"):
    """Load configuration from a JSON config file
    Arguments:
    config_file: Path to JSON config file with file paths
    Returns:
    config: Dictionary with configuration values
    """
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def main():
    """Load configuration from config.json and process LEGO parts inventory"""
    config = load_config()
    
    master_parts_file = pathlib.Path(config['master_parts_file'])
    user_parts_file = pathlib.Path(config['user_parts_file'])
    containers_file = pathlib.Path(config['containers_file'])
    
    parts_dict = parse_master_parts_file(master_parts_file, config)
    user_parts = parse_user_parts_file(user_parts_file)
    containers = expand_containers(parse_containers_csv(containers_file))
    
    sorted_containers, unsorted_parts = sort(user_parts, parts_dict, containers)

    print("Sorted Containers:")
    for container in sorted_containers:
        print(container)
    print("\nUnsorted Parts:")
    for part in unsorted_parts:
        print(part)

if __name__ == "__main__":
    main()