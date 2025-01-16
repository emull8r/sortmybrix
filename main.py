import argparse
import pathlib
import csv
from collections import namedtuple

Part = namedtuple('Part', ['Part', 'Color', 'Quantity'])

def parse_master_parts_file(master_parts_file):
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
                #category_name = line[1] no point in using this
                number = line[2]
                #name = line[3]
                alternate_item_number = line[4]
                dimensions = line[5]
                if dimensions != '? x ? x ?':
                    dimensions = dimensions.split('x')
                    # dimensions are in centimeters
                    width = float(dimensions[0].strip())
                    height = float(dimensions[1].strip())
                    depth = float(dimensions[2].strip())
                    parts_dict[number] = {"category_id": category_id,
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
            part = Part(Part=row['Part'], Color=int(row['Color']), Quantity=int(row['Quantity']))
            parts_list.append(part)
    return parts_list

def main():
    """ Parse command line arguments
     Arguments:
     Master parts file: TXT file downloaded from bricklink, 
     contains the IDs of parts and their physical dimensions and other properties
     User parts file: CSV downloaded from Rebrickable, contains all the LEGO parts owned by user
     Containers: List of containers and quantities in the format 'x,y,z,#', where x is the width,
     y is the height, and z is the depth of the container, and # is the quantity of that container
     """
    parser = argparse.ArgumentParser()
    parser.add_argument("master_parts_file", help="TXT file downloaded from Bricklink", type=pathlib.Path,
                        default="data/Parts.txt")
    parser.add_argument("user_parts_file", help="CSV file downloaded from Rebrickable", type=pathlib.Path)
    #parser.add_argument("containers", help="List of containers and quantities, where each item is in the format 'x,y,z,#'," 
    #                    +"where x, y, and z are floats of the dimensions, and # is the quantity of that container",
    #                    nargs='+', type=str)
    args = parser.parse_args()
    parts_dict = parse_master_parts_file(args.master_parts_file)
    print(parts_dict)
    user_parts = parse_user_parts_file(args.user_parts_file)
    print(user_parts)

if __name__ == "__main__":
    main()