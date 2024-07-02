import aiosqlite
from datetime import datetime
from bs4 import BeautifulSoup


async def database_connect(db_name: str):
    """
    Connection for sqlite3 database

    :param db_name: Write database name
    :return: sqlite connect and sqlite cursor
    """
    connection = await aiosqlite.connect(db_name)
    cursor = await connection.cursor()
    return connection, cursor


async def commit_and_close(connection: aiosqlite.Connection):
    """
    Commit and close database

    :param connection: connect for database_connect
    :return: Noting
    """
    await connection.commit()
    await connection.close()


async def create_tables(db_name: str):
    """
    Create a tables for database

    :param db_name: Write database name
    :return: Nothing
    """
    conn, cursor = await database_connect(db_name)
    sql = '''
        DROP TABLE IF EXISTS tg_users;
        CREATE TABLE IF NOT EXISTS tg_users(
            user_id INTEGER UNIQUE PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            registration_date TEXT
        );
        
        DROP TABLE IF EXISTS emaktab;
        CREATE TABLE IF NOT EXISTS emaktab(
            user_id INTEGER PRIMARY KEY REFERENCES tg_users(user_id),
            
            login TEXT UNIQUE,
            password TEXT
        );
    '''

    await cursor.executescript(sql)
    await commit_and_close(conn)


async def check_user_tg(db_name: str, user_id: int):
    """
    Checking if there is a user_id in the database

    :param db_name: Write database name
    :param user_id: Write the telegram user id
    """
    conn, cursor = await database_connect(db_name)
    await cursor.execute('SELECT * FROM tg_users WHERE user_id = ?;', (user_id,))
    user = await cursor.fetchone()
    return True if user else False


async def check_user_emaktab(db_name: str, login: str):
    """
    Checking if there is a login in the database

    :param db_name: Write database name
    :param user_id: Write the telegram user id
    """
    conn, cursor = await database_connect(db_name)
    await cursor.execute('SELECT * FROM emaktab WHERE login = ?;', (login,))
    account = await cursor.fetchone()
    return True if account else False


async def add_tg_user(db_name: str, user_id: int, username: str, full_name: str):
    """
    Adding a user's telegram to the database

    :param db_name: Write database name
    :param user_id: Write telegram user id
    :param username: Write telegram username (@)
    :param full_name: Write telegram full name

    :return: Nothing
    """
    conn, cursor = await database_connect(db_name)
    registration_date = datetime.now().strftime("%m.%d.%Y %H:%M:%S")
    await cursor.execute('INSERT INTO tg_users(user_id, username, full_name, registration_date) VALUES (?, ?, ?, ?);',
                         (user_id, username, full_name, registration_date))
    await commit_and_close(conn)

    print(f"""
New user:
    id: {user_id}
    username: {username}
    full name: {full_name}
    registration_date: {registration_date}
""")


async def add_emaktab(db_name: str, user_id: int, login: str, password: str):
    """
    Adding a user's eMaktab to the database

    :param db_name: Write database name
    :param user_id: Write telegram user id
    :param login: Write eMaktab login
    :param password: Write eMaktab password

    :return: Nothing
    """
    conn, cursor = await database_connect(db_name)
    await cursor.execute('INSERT INTO emaktab(user_id, login, password) VALUES (?, ?, ?);', (user_id, login, password))
    await commit_and_close(conn)


async def delete_tg_user(db_name: str, user_id: int):
    """
    Delete telegram user for database

    :param db_name: Write database name
    :param user_id: Write telegram user id

    :return: Noting
    """
    conn, cursor = await database_connect(db_name)
    await cursor.execute('DELETE FROM tg_users WHERE user_id = ?;', (user_id,))
    await commit_and_close(conn)


async def delete_emaktab_login(db_name: str, user_id: int):
    """
    Delete eMaktab user for database

    :param db_name: Write database name
    :param user_id: Write telegram user id

    :return: Noting
    """
    conn, cursor = await database_connect(db_name)
    await cursor.execute('DELETE FROM emaktab WHERE user_id = ?;', (user_id,))
    await commit_and_close(conn)


async def get_user_to_user_id(db_name: str, user_id: int):
    conn, cursor = await database_connect(db_name)
    await cursor.execute('SELECT * FROM emaktab WHERE user_id = ?;', (user_id,))
    user = await cursor.fetchone()
    return user
