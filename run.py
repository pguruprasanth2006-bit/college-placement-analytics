import os
import sys

# Set directory to college_placement_system
app_dir = os.path.join(os.path.dirname(__file__), 'college_placement_system')
os.chdir(app_dir)
sys.path.insert(0, app_dir)

from run import app, main

if __name__ == '__main__':
    main()
