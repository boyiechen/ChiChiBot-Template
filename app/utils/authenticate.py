# Add helper functions to check authorization
import os
import sys
import sqlite3
from icecream import ic
# Add project folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import AUTHORIZED_USERS, AUTHORIZED_GROUPS, SQLITE_DB_PATH

# check if user is authorized
def is_user_authorized(user_id):
    ic(user_id)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM authorized_users WHERE user_id = ?", (user_id,))
    authorized = c.fetchone()
    ic(authorized)
    conn.close()
    return authorized is not None

# check if group is authorized
def is_group_authorized(group_id):
    ic(group_id)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM authorized_groups WHERE group_id = ?", (group_id,))
    authorized = c.fetchone()
    ic(authorized)
    conn.close()
    return authorized is not None


# edit the database to add authorized groups
def add_authorized_group(group_id):
    """Manually add a group to the authorized groups list."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO authorized_groups (group_id) VALUES (?)", (group_id,))
    conn.commit()
    conn.close()

# edit the database to add authorized users 
def add_authorized_user(user_id, relationship):
    """Manually add a user to the authorized users list."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO authorized_users (user_id, relationship) VALUES (?, ?)", (user_id, relationship))
    conn.commit()
    conn.close()

# edit the database to remove authorized users when the user leaves the group
def remove_authorized_user(user_id):
    """Manually remove a user from the authorized users list."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM authorized_users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    
    for user in AUTHORIZED_USERS:
        add_authorized_user(user['user_id'], user['relationship'])
    for group in AUTHORIZED_GROUPS:
        add_authorized_group(group)
