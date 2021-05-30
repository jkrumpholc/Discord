import System
import Git_update as Git

file = "Workout.txt"


def file_read():
    data = []
    with open(file, "r+") as _file:
        for i in _file:
            option, value = i.strip().split(":")
            data.append({'option': option, 'value': int(value)})
    return data


def file_write(data):
    with open(file, "w") as _file:
        for i in data:
            _file.write(f"{i['option']}:{i['value']}\n")
    Git.new_commit(file)


def daily_check():
    today = System.today().timetuple().tm_yday
    data = file_read()
    date = System.datework().timetuple().tm_yday
    for i in data:
        option = i['option']
        if option == 'push':
            i['value'] += (today - int(date)) * 20
        elif option == 'run':
            i['value'] += (today - int(date)) * 250
    file_write(data)
    System.datewrite("w", System.today())


def substract(option, num):
    data = file_read()
    ret = ""
    for i in data:
        if i['option'] == option:
            i['value'] -= int(num)
            ret = i['value']
            break
    file_write(data)
    return ret


def status():
    remain = file_read()
    return remain
