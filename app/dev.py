# Set the path
import sys
from flask.ext.migrate import MigrateCommand

import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'statuspage')))

from flask.ext.script import Manager, Server
from statuspage import app

manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host='0.0.0.0')
)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
