"""Contains utilities for calculation and conversion."""

def convert_centimeters_to_inches(centimeters):
    """Convert centimeters to inches"""
    return centimeters / 2.54

def convert_inches_to_centimeters(inches):
    """Convert inches to centimeters"""
    return inches * 2.54

def calculate_volume(width, height, depth):
    """Calculate the volume of a rectangular prism"""
    return width * height * depth

def check_if_part_will_fit(part, container):
    """Check if a part will fit in a container"""
    return max(part.width, part.height, part.depth) < max(container.width, container.height, container.depth)