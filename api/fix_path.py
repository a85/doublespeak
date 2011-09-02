import os
import sys

def fix_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tornado'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

def main():
    return 

if __name__ == "__main__":
    fix_path()
