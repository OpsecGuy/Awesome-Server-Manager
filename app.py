"""Awesome Server Manager v1 - Python 3.11.0"""
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
