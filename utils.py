import curses


def menu_loop(stdscr, menu_title, menu_items):
    # Set cursor visibility to 0 (invisible)
    curses.curs_set(0)
    # Initialize color pair
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row = 0
    draw_menu(stdscr, current_row, menu_title, menu_items)

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return current_row

        draw_menu(stdscr, current_row, menu_title, menu_items)


def draw_menu(stdscr, selected_row_idx, menu_title, menu_items):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    stdscr.addstr(0, 0, menu_title)
    stdscr.addstr(1, 0, "=" * len(menu_title))

    for idx, item in enumerate(menu_items):
        x = w // 2 - len(item) // 2
        y = h // 2 - len(menu_items) // 2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, item)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, item)

    stdscr.refresh()


def get_string_input(stdscr, prompt, allow_empty=False):
    curses.echo()
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h // 2, 0, prompt)
    stdscr.refresh()
    input_str = stdscr.getstr(h // 2, len(prompt)).decode('utf-8').strip()
    curses.noecho()
    if not allow_empty and not input_str:
        show_message(stdscr, "Input cannot be empty. Please try again.")
        return get_string_input(stdscr, prompt, allow_empty)
    return input_str


def get_int_input(stdscr, prompt):
    while True:
        input_str = get_string_input(stdscr, prompt)
        try:
            return int(input_str)
        except ValueError:
            show_message(stdscr, "Invalid input. Please enter a valid number.")


def show_message(stdscr, message):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h // 2, w // 2 - len(message) // 2, message)
    stdscr.refresh()
    stdscr.getch()
