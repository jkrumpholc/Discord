from builtins import tuple
from datetime import *
import System
import Database
import Mal_Api


def watched(name: str | tuple, add: int) -> str:
    if isinstance(name, tuple):
        name = " ".join(name)
    ret = Database.db.get_anime(name)
    if len(ret) == 0:
        return f"Anime \"{name}\" not found."
    elif len(ret) == 1:
        return f"Anime \"{name}\" is already finished."
    else:
        full_name, ep = ret[0]
        ep += + int(add)
        if typ == "ongoing":
            sql = f'''UPDATE anime_ongoing SET current_ep = {ep} WHERE mal_id = {mal_id} '''
        elif typ == "finished":
            sql = f'''UPDATE anime_watching SET current_ep = {ep} WHERE mal_id = {mal_id} '''
        else:
            return "Database Error."
        Database.db.command(sql)
        Mal_Api.update_anime(mal_id, f"num_watched_episodes={ep}")
        return f"Anime \"{full_name}\" updated."


def new_anime_going(url: str, mal_id: int, ep: int, last: int, update_time: datetime, name: str | tuple = None) -> str:
    if name is None:
        name = System.parse_url(url)
    elif isinstance(name, tuple):
        name = " ".join(name)
    find = Database.db.command(f'''SELECT * FROM anime_list where mal_id = {mal_id} ''')
    if len(find) != 0:
        return f"Anime \"{name}\" already on list."
    else:
        if Database.db.add_ongoing_anime(url, name, ep, last, update_time, mal_id):
            return f"Anime \"{name}\" successfully added."
        return "Database error."


def new_anime(url: str, mal_id: int, ep: int, max_ep: int, name: str = None):
    if name is None:
        name = System.parse_url(url)
    elif isinstance(name, tuple):
        name = " ".join(name)
    find = Database.db.command(f'''SELECT * FROM anime_list where mal_id = {mal_id} ''')
    if len(find) != 0:
        return "Anime already on list."
    else:
        if Database.db.add_watching_anime(name, ep, max_ep, url, mal_id):
            return f"Anime \"{name}\" successfully added."
        return "Database error."


def new_anime_url(url: str) -> str:
    name, anime_type, episode, remain, mal_id = System.parse_page(url)
    air_time = System.add_time(System.now(), remain)
    if air_time.minute >= 30:
        air_time = air_time.replace(second=0, microsecond=0, minute=0, hour=air_time.hour + 1)
    else:
        air_time = air_time.replace(second=0, microsecond=0, minute=0)
    if anime_type == "Ongoing":
        ret = new_anime_going(url, mal_id, 0, episode, air_time + timedelta(hours=1), name=name)
    else:
        ret = new_anime(url, mal_id, 0, episode, name=name)
    return ret


def finished(name: str | tuple) -> str:
    if isinstance(name, tuple):
        name = " ".join(name)
    typ, mal_id = Database.db.get_anime_type(name)
    if len(typ) == 0:
        return "Anime not found."
    data = Database.db.command(f'''SELECT * FROM anime_list where mal_id = {mal_id} ''')
    if len(data) > 0:
        data = data[0][0]
    if typ == "ongoing":
        sql = f'''DELETE FROM anime_ongoing where mal_id = {mal_id} '''
    elif typ == "finished":
        sql = f'''DELETE FROM anime_watching where mal_id = {mal_id} '''
    else:
        return f"Database Error: type: {typ}"
    Database.db.command(sql)
    Database.db.command(f'''DELETE FROM anime_list where mal_id = {mal_id} ''')
    return f"Anime \"{data}\" was removed from watchlist."


def transfer(name: str | tuple) -> str:
    if isinstance(name, tuple):
        name = " ".join(name)
    data = Database.db.command(f'''SELECT * FROM anime_ongoing where name LIKE "%{name}%" ''')
    if len(data) > 0:
        data = data[0]
        finished(name)
        Database.db.add_watching_anime(data[0], data[1], data[2], data[4], data[5])
        return f"Anime \"{data[0]}\" transferred from ongoing to finished."
    else:
        return f"Anime \"{name}\" not found."


def status() -> str:
    ret = ""
    data_list = Database.db.command(f'''SELECT * FROM anime_watching ''')
    for i in data_list:
        ret += f"Name: {i[0]}, Episode: {i[1]} out of {i[2]} \n"
    data_list = Database.db.command(f'''SELECT * FROM anime_ongoing ORDER BY update_time''')
    for i in data_list:
        ret += f"Name: {i[0]}, Episode: {i[1]}, Last episode: {i[2]}, Airing in {i[3].strftime('%A')} at {i[3].strftime('%H')}:00\n<{i[4]}>\n"
    return ret


def waiting() -> str:
    data_list = Database.db.command(
        f'''SELECT name, current_ep, latest_ep  FROM anime_ongoing WHERE latest_ep > current_ep''')
    ret = ""
    for i in data_list:
        diff = i[2] - i[1]
        append = "s" if diff > 1 else ""
        ret += f"Anime \"{i[0]}\" have {diff} unwatched episode{append}.\n"
    return ret


def change_time(name: str | tuple, hour: time) -> str:
    if isinstance(name, tuple):
        name = " ".join(name)
    Database.db.command(f'''UPDATE anime_ongoing SET update_time = {hour} WHERE name LIKE "%{name}%" ''')
    return f"Anime \"{name}\" update time set to {hour}:00"


def update() -> str:
    now = System.now()
    ret = ""
    day = (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    data_list = Database.db.command(f'''SELECT * FROM anime_ongoing WHERE update_time <= '{day}' ORDER BY update_time''')
    for i in data_list:
        name, ep, latest, update_time, url, mal_id = i
        delta = (update_time - now).total_seconds()
        if update_time >= now:
            diff = round(delta / 3600)
            if 24 > diff > 0:
                append = "s" if diff > 1 else ""
                ret += f"Anime \"{name}\" will have new episode in {diff} hour{append}.\n"
                continue
            elif diff == 0:
                if not int(System.parse_page(url)[2]) > latest:
                    ret += f"Anime \"{name}\" will have new episode within hour.\n"
                    continue
                else:
                    update_time = now
        if update_time <= now:
            released = int(System.parse_page(url)[2])
            old = latest
            while update_time <= now:
                if released > latest:
                    latest += 1
                update_time += timedelta(days=7)
            diff = latest - old
            if diff == 0:
                ret += f"Anime \"{name}\" don't have any new episode.\n"
            else:
                append = "s" if diff > 1 else ""
                ret += f"Anime \"{name}\" have {diff} new episode{append}.\n"
            Database.db.command(f'''UPDATE anime_ongoing SET latest_ep = {latest} WHERE mal_id = {mal_id}''')
    return ret
