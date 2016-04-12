from tkinter import *
from PIL import Image, ImageTk


class MapFrame(Frame):
    """
    Uses Tkinter and PIL to display a map image to the user.
    Source: http://hci574.blogspot.com/2010/04/using-google-maps-static-images.html
    Source: http://www.daniweb.com/forums/thread65288.html
    """
    def __init__(self, master, im, title):
        Frame.__init__(self, master)
        self.caption = Label(self, text=title)
        self.caption.grid()
        self.image = ImageTk.PhotoImage(im) # <--- results of PhotoImage() must be stored
        self.image_label = Label(self, image=self.image, bd=0) # <--- will not work if 'image = ImageTk.PhotoImage(im)'
        self.image_label.grid()
        self.grid()
