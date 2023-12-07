def center_window(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - root.winfo_reqwidth()) // 2
    y = (screen_height - root.winfo_reqheight()) // 2

    root.geometry("+{}+{}".format(x, y))