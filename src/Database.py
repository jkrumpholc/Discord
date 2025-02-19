from datetime import *
from mysql.connector import *
import System


class Database:
    def __init__(self):
        self.host = System.credentials("SQL_HOST")
        self.password = System.credentials("SQL_PASSWORD")
        self.database = System.credentials("SQL_DATABASE")
        self.user = System.credentials("SQL_USER")
        self.conn = connect(host=self.host, password=self.password, database=self.database, user=self.user)
        self.cur = self.conn.cursor()
        self.sql = ""

    def __del__(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()

    def execute(self, fetch=False):
        try:
            self.cur.execute(self.sql)
            self.sql = ""
            if fetch:
                ret = self.cur.fetchall()
                return ret
        except (Exception, DatabaseError) as error:
            print(error)
            return False

    def add_watching_anime(self, name: str, curr_ep: int, ep: int, mal_id: int) -> bool:
        self.sql += f'''INSERT INTO anime_finished (id, num_episodes, watched_episodes) VALUES
        ({mal_id}, {curr_ep}, {ep});'''
        self.add_anime_list(name, mal_id, status="finished")
        return True

    def add_ongoing_anime(self, name: str, curr_ep: int, last_ep: int, update: datetime, mal_id: int) -> bool:
        self.sql += f'''INSERT INTO anime_ongoing (id, num_episodes, watched_episodes, airing) VALUES
        ({mal_id}, {last_ep}, {curr_ep}, '{update.strftime("%Y-%m-%d %H:%M:SS")}');'''
        self.add_anime_list(name, mal_id, status="ongoing")
        return True

    def add_completed_anime(self, name: str, mal_id: int, date_time: date = System.today()) -> bool:
        self.sql += f'''INSERT INTO anime_completed (id, finished) VALUES({mal_id}, '{date_time.strftime("%Y-%m-%d")}');'''
        self.add_anime_list(name, mal_id, status="completed")
        return True

    def add_anime_list(self, name: str, mal_id: int, status: str) -> bool:
        self.sql += f'''INSERT INTO anime_list(id, name, status) VALUES({mal_id}, "{name}", {status});'''
        self.execute()
        return True

    def get_anime_type_name(self, name: str) -> tuple[int, str, str]:
        self.sql += f'''SELECT id, name, status FROM anime_list where name LIKE "%{name}%"; '''
        return self.execute(True)

    def get_anime(self, name: str) -> list:
        mal_id, name, status = self.get_anime_type_name(name)
        if status == "ongoing":
            self.sql += f'''SELECT num_episodes, watched_episodes, airing FROM anime_ongoing where id = {mal_id}; '''
        elif status == "finished":
            self.sql += f'''SELECT num_episodes, watched_episodes FROM anime_finished where id = {mal_id}; '''
        elif status == "completed":
            self.sql += f'''SELECT finished FROM anime_completed where id = {mal_id}; '''
        else:
            return []
        return self.execute(True)

    """def command(self, sql: str) -> list:
        try:
            self.cur.execute(sql)
            try:
                ret = self.cur.fetchall()
            except ProgrammingError:
                ret = ""
            return ret
        except ProgrammingError:
            exit(f"Wrong SQL request: {sql}")
        except OperationalError:
            exit("Cannot connect to database.")"""

    """def add_note(self, name: str, note_date: str, note_time: str, text: str, repeat: str) -> None:
        sql = f'''INSERT INTO notes(name, date, time, repeat, text) VALUES('{name}', '{note_date}', '{note_time}', {repeat}, '{text}')'''
        self.cur.execute(sql)

    def add_repeat_note(self, name: str, note_time: datetime.time, text: str, interval: timedelta,
                        repeat: bool) -> None:
        sql = f'''INSERT INTO notes(name, time, repeat, every,text)VALUES('{name}','{note_time}',{repeat},{interval},'{text}')'''
        self.cur.execute(sql)
"""


db = Database()
