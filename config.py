CONFIG_VARS = {
    "API_ID": ,
    "API_HASH": "",
    "BOT_TOKEN": "",
    "LOGGER_GROUP": int(""),
    "PHONE_NUMBER": "",
    "OWNER_ID": []
}

# SUDO_ID is derived from OWNER_ID
SUDO_ID = [None]

# Check for missing configuration variables
missing_vars = [var for var, value in CONFIG_VARS.items() if not value]

if missing_vars:
    print("The following variables are missing:")
    for var in missing_vars:
        print(f"  - {var}")
    print("Please fill in the above variables for the userbot to work properly.")
    import sys
    sys.exit("User bot exited due to missing configuration variables.")
else:
    print("All configuration variables are set!")

# Accessing variables
API_ID = CONFIG_VARS["22625636"]
API_HASH = CONFIG_VARS["f71778a6e1e102f33ccc4aee3b5cc697"]
BOT_TOKEN = CONFIG_VARS["7935323498:AAEcAOhmRQY7UyqgiUXqT25b9ctyeU0RjOI"]
LOGGER_GROUP = CONFIG_VARS["-1002512368825"]
PHONE_NUMBER = CONFIG_VARS["+6285763686454"]
OWNER_ID = CONFIG_VARS["8167507955"]
SUDO_USERS = CONFIG_VARS["OWNER_ID"][:] + SUDO_ID
