import os
from core.app_factory import create_app

# Dynamically load the environment configuration (default to development)
config_name = os.getenv('FLASK_CONFIG', 'default')

# Instantiate the Flask application via the Factory
app = create_app(config_name)

if __name__ == '__main__':
    # Run the server. Debug mode is controlled via config/settings.py
    app.run(host='0.0.0.0', port=5000)