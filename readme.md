# Homecontrol backend

You can see the other parts of the project in following links

[Frontend](https://github.com/Bialri/Homecontrol_front)

[Hardware](https://github.com/Bialri/Homecontrol_hardware)

# Setup

### .env file

```dotenv
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_ROOT_PASSWORD=
DB_URL=mysql+aiomysql://${MYSQL_USER}:${MYSQL_PASSWORD}@localhost:3306/${MYSQL_DATABASE}
SECRET_AUTH= # secret for the jwt encryption
DOCS_URL=/docs
TITLE=Home control App
SCRIPTS_ADD_SECRET= # secret for administrator to add to db new devices and types of actions for script execution
TZ=Europe/Moscow
```

# Daemon work explanation

daemon is necessary to execute actions on schedule.
Non schedule scripts is also executed by the daemon.
The main idea was to make adding the new execution instructions easier as possible.

Daemon execute actions every 5 seconds.
It requests for activities to be carried out at the current time.
The activities are then handed over for execution, depending on the device the activities are handed over to the appropriate executor.
Execution instructions can simply be added and changed.

## How to add instructions
Create an executor function in the instructions package and add it to the init file.
``` python
from .button import execute_button_action
```
Import executor to <b>main.py</b>.
``` python
from instructions import execute_button_action
```
Add new option to match case statement.
``` python
match device_type:
        case 1:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, execute_button_action, action_id, device_id, session_maker)
```

## Non schedule scripts

Non schedule scripts executed as ordinary
but every time daemon delete already executed scripts that marked as singe_execution 
