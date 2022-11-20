"""Awesome Server Manager v1 - Python 3.9.12"""
import threading
import gui

def main():
    """
    Entry Point
    """
    wnd.create()
    threading.Thread(target=wnd.update, daemon=True).start()
    wnd.run()
    wnd.destroy()


if __name__ == '__main__':
    wnd = gui.Window()
    main()
