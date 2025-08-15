import sqlite3

#connect to SQLite
conn = sqlite3.connect('systemUsers.db')
cursor = conn.cursor()


#create users table with id and azure blob url
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        uuid TEXT PRIMARY KEY,
        azure_blob_url TEXT NOT NULL
    )
''')

#commit changes and close 
conn.commit()
conn.close()

def checkUser(userUUID):
    try:
            conn = sqlite3.connect('systemUsers.db')
            cursor = conn.cursor()

            # Check if the UUID already exists
            cursor.execute('''
                SELECT COUNT(*) FROM users WHERE uuid = ?
            ''', (userUUID,))
            if cursor.fetchone()[0] > 0:
                print(f"User with UUID {userUUID} already exists.")
                return True
            else:
                return False
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")

    finally:
        conn.close()
        
def insertUser(userUUID, azure_blob_url):
    try:
        conn = sqlite3.connect('systemUsers.db')
        cursor = conn.cursor()

        # Insert the new user
        cursor.execute('''
            INSERT INTO users (uuid, azure_blob_url)
            VALUES (?, ?)
        ''', (userUUID, azure_blob_url))

        conn.commit()
        print(f"User inserted successfully with ID {userUUID}.")

    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")

    finally:
        conn.close()

      
def updateUserContainerUrl(userUUID, container_url):
    try:
        conn = sqlite3.connect('systemUsers.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET azure_blob_url = ?
            WHERE uuid = ?
        ''', (container_url, userUUID))

        conn.commit()

        print(f"Updated container URL for UUID {userUUID}.")

    except sqlite3.Error as e:
        print(f"Error updating container URL: {e}")

    finally:
        conn.close()
        
def viewUsers():
    try:
        conn = sqlite3.connect('systemUsers.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        if rows:
            print("Users in the database:")
            for row in rows:
                print(row)
        else:
            print("No users found in the database.")
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
    finally:
        conn.close()

viewUsers()
