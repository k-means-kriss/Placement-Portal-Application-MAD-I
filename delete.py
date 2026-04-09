import os

def delete_db():
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("database.db deleted!")
    else:
        print("No database file found.")

if __name__ == "__main__":
    delete_db()