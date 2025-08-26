import sys
import os
from src import create_app

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
