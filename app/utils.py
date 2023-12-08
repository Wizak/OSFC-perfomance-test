import webbrowser


def center_window(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - root.winfo_reqwidth()) // 2
    y = (screen_height - root.winfo_reqheight()) // 2

    root.geometry("+{}+{}".format(x, y))


def prepare_time_to_format(value):
    if isinstance(value, str):
        return value

    result = ""
    minutes = int(value // 60)
    if minutes != 0:
       result += f"{minutes} m"
    seconds = value % 60
    if int(seconds) != 0:
        if len(result) != 0:
            result += " "
        result += f"{int(seconds)} s"
    milliseconds = int((seconds % 1) * 1000)
    if milliseconds != 0:
        if len(result) != 0:
            result += " "
        result += f"{milliseconds} ms"

    return result


def open_data_example_link():
    url = 'https://drive.google.com/file/d/1_TdzCgSx2jEmX_T21n3aQohwJ7Gro40w/view?usp=sharing'
    webbrowser.open(url)