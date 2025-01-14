import os

def parse_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            print(parts)

def main():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'Parts.txt')
    parse_file(file_path)

if __name__ == "__main__":
    main()