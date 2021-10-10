import Database
from datetime import datetime
import System


def add_note(name, input_date, input_time, text):
    timestamp = datetime.strptime(f'{input_date} {input_time}', '%d.%m.%Y %H:%M')
    now = System.now()
    if timestamp < now:
        return f"Unable to create notification for past event."
    else:
        delta = timestamp - now
        sec = (delta.days * 86400) + delta.seconds
    note = Database.command(f'''SELECT * FROM notes WHERE name='{name}' ''')
    if len(note) != 0:
        return f'Note {name} already exists.'
    else:
        input_date = datetime.strptime(input_date, '%d.%m.%Y').strftime('%Y-%m-%d')
        Database.add_note(name, input_date, input_time, text, repeat='FALSE')
        return f'Note {name} added\nNotification for note {name} has been set...\nRemaining time: ' \
               f'{System.time_to_human(sec)}', sec


def show_note():
    notes = Database.command('''SELECT * FROM notes''')
    if len(notes) == 0:
        return "No notes in database."
    else:
        today = System.today()
        now = System.now()
        ret = ""
        for i in notes:
            delta_time = i[1] - now
            delta_date = i[2] - today
            delta = (delta_date * 86400) + delta_time
            ret += f"Name: {i[0]}, Remaining time: {System.time_to_human(delta)}\n"
        return ret


def delete_note(name):
    Database.command(f'''DELETE FROM notes where name='{name}' ''')
    return f"Note {name} successfully deleted"


def clear_due():
    notes = Database.command('''SELECT * FROM notes''')
    for i in notes:
        if i[1] < datetime.time(System.now()) and i[2] == System.today() or i[2] < System.today():
            Database.command(f'''DELETE FROM notes where name='{i[0]}' ''')
