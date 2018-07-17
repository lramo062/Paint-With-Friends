from _thread import *
from multiprocessing import Process, Lock
from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk

class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self, client):
        self.username = None
        self.client = client
        self.popupmsg("Please enter your username")
        
        self.root = Tk()
    
        # Window Title
        self.root.wm_title("Paint with Friends")

        # Brush Button
        brush_image = ImageTk.PhotoImage(file="brush.png")
        self.brush_button = Button(self.root, image=brush_image, command=self.use_brush)
        self.brush_button.grid(row=100, column=1)

        # Circle Button
        self.circle_button = Button(self.root, text="Circle", command=self.use_circle)
        self.circle_button.grid(row=100, column=6)

        # Rectangle Button
        # rectangle_image = ImageTk.PhotoImage(file="rectangle.png")
        self.rectangle_button = Button(self.root, text="Rectangle", command=self.use_rectangle)
        self.rectangle_button.grid(row=100, column=7)
   
        # Color Button
        # color_image = ImageTk.PhotoImage(file="color.png")
        # self.color_button = Button(self.root, image=color_image, command=self.choose_color, )
        # self.color_button.grid(row=100, column=2)

        # Eraser Button
        eraser_image = ImageTk.PhotoImage(file="eraser.png")
        self.eraser_button = Button(self.root, image=eraser_image, command=self.use_eraser)
        self.eraser_button.grid(row=100, column=3)

        # Size Button
        self.choose_size_button = Scale(self.root, from_=1, to=10, orient=HORIZONTAL)
        self.choose_size_button.grid(row=100, column=4)
        
        # Wipe Canvas Button
        self.wipe_canvas_button = Button(self.root, text="New Canvas", command=self.wipe_canvas)
        self.wipe_canvas_button.grid(row=100, column=5)
        
        # Canvas
        self.c = Canvas(self.root, bg='white', width=600, height=600)
        self.c.grid(row=0, columnspan=10)

        # Text Dialog Box, will display users' messages
        self.text_box = Text(self.root, height=40, width=30)
        self.text_box.grid(row=0, column=11)

        # Scroll Bar for Text Box
        self.scroll = Scrollbar(self.root, command=self.text_box.yview)
        self.scroll.grid(row=0, column=12)

        self.setup()
        
        # START NEW THREAD THAT IS CONSTANTLY LISTENING FOR DATA!!!!
        start_new_thread(self.receive_data, ())
        self.root.mainloop()

    def setup(self):
        # destroy window if not connected to server
        if not self.username:
            self.root.destroy()
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        # self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = None

    def popupmsg(self, message):

        self.popup = Tk()
        self.popup.wm_title("Welcome to Paint-With-Friends!")
        self.popup.geometry("500x75")
        
        label = ttk.Label(self.popup, text=message)
        label.place(x=25, y=25, anchor="center")
        label.pack()

        text_box = Entry(self.popup)
        text_box.place(x=25, y=50, anchor="center")
        text_box.pack()

        enter_button = ttk.Button(self.popup, text="Enter", command=lambda: self.get_username(text_box))
        enter_button.pack()
        
        self.popup.mainloop()

    def get_username(self, text_box):
        # send username to server
        username = text_box.get()
        data = [username, 0, 0, 0, "username", 0, 0]
        self.client.send_data(data)

        # check if username is valid and assign color
        while True:
            color_data = self.client.receive_data()
            print(color_data)
            if color_data[0] == "ERROR":
                self.popup.destroy()
                self.popupmsg("That username is already taken, please enter a new username")
                break
                
            elif color_data[4] == "color":
                self.color = color_data[0]
                self.username = color_data[1]
                self.popup.destroy()
                break
        
    def start_canvas(self):
        print('starting canvas')
        self.root.mainloop()

    def use_brush(self):
        self.activate_button(self.brush_button)
        self.c.bind("<ButtonPress-1>", self.on_button_press)
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
   
    def use_circle(self):
        self.activate_button(self.circle_button)
        self.c.bind("<ButtonPress-1>", self.on_button_press)
        self.c.unbind('<B1-Motion>')
        self.c.bind("<ButtonRelease-1>", self.draw_circle)

    def use_rectangle(self):
        self.activate_button(self.rectangle_button)
        self.c.bind("<ButtonPress-1>", self.on_button_press)
        self.c.unbind('<B1-Motion>')
        self.c.bind("<ButtonRelease-1>", self.draw_rectangle)
        
    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)
        self.c.bind("<ButtonPress-1>", self.on_button_press)
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        
    def on_button_press(self, event):
        self.x = event.x
        self.y = event.y
        
    # def choose_color(self):
    #     self.eraser_on = False
    #     # ask color is a built-in color picker tool in tkinter
    #     self.color = askcolor(color=self.color)[1]

    def wipe_canvas(self):
        self.client.send_data([0,0,0,0,"wipe_canvas",0,0])
        self.c = Canvas(self.root, bg='white', width=600, height=600)
        self.c.grid(row=0, columnspan=10)
        self.setup()
        
    def activate_button(self, some_button, eraser_mode=False):
        # if there's an active button raise it
        if self.active_button:
            self.active_button.config(relief=RAISED)
            self.active_button = None
            some_button.config(relief=SUNKEN)
            self.active_button = some_button
            self.eraser_on = eraser_mode

        # if there's no active button the sink the new button
        else:
            some_button.config(relief=SUNKEN)
            self.active_button = some_button
            self.eraser_on = eraser_mode

    def paint(self, event):
        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color
        if self.x and self.y:
            # send data to server
            data = [self.x, self.y, event.x, event.y,
                    "paint", paint_color, self.line_width]
            self.client.send_data(data)

            # paint on canvas
            self.c.create_line(data[0], data[1], data[2], data[3],
                               width=self.line_width, fill=paint_color,
                            capstyle=ROUND, smooth=TRUE, splinesteps=36)
            self.x = event.x
            self.y = event.y
            
    def draw_circle(self, event):
        self.activate_button(self.circle_button)
        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color

        # set dimensions for circle
        self.old_x, self.old_y = (self.x, self.y)
        self.x, self.y = (event.x, event.y)

        # send data to server
        data = [self.old_x, self.old_y, self.x, self.y,
                "draw_circle", paint_color, self.line_width]
        self.client.send_data(data)

        # paint on canvas
        if self.old_x and self.old_y:
            self.c.create_oval(self.old_x, self.old_y, self.x, self.y, outline=paint_color,
                               width=self.line_width)
        self.old_x = None
        self.old_y = None


    def draw_rectangle(self, event):
        self.activate_button(self.rectangle_button)
        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color
        
        # set dimensions for circle
        self.old_x, self.old_y = (self.x, self.y)
        self.x, self.y = (event.x, event.y)

        # send data to server
        data = [self.old_x, self.old_y, self.x, self.y,
                "draw_rectangle", paint_color, self.line_width]
        self.client.send_data(data)

        if self.old_x and self.old_y:
            self.c.create_rectangle(self.old_x, self.old_y, self.x, self.y, outline=paint_color,
                               width=self.line_width)
        self.old_x = None
        self.old_y = None
            
    def reset(self, event):
        self.old_x, self.old_y = None, None

    def print_user_connected(self, text):
        self.text_box.insert(END, text)
        
    def receive_data(self):
        while True:
            paint_color = 'white' if self.eraser_on else self.color
            cordinates = self.client.receive_data()
            if cordinates[4] == 'paint':
                self.c.create_line(cordinates[0], cordinates[1], cordinates[2], cordinates[3],
                                   width=cordinates[6], fill=cordinates[5],
                                   capstyle=ROUND, smooth=TRUE, splinesteps=36)
            elif cordinates[4] == 'draw_rectangle':
                self.c.create_rectangle(cordinates[0], cordinates[1], cordinates[2],
                                        cordinates[3], outline=cordinates[5],
                                        width=cordinates[6])
            elif cordinates[4] == 'draw_circle':
                self.c.create_oval(cordinates[0], cordinates[1], cordinates[2],
                                   cordinates[3], outline=cordinates[5],
                                   width=cordinates[6])
            elif cordinates[4] == 'wipe_canvas':
                self.c = Canvas(self.root, bg='white', width=600, height=600)
                self.c.grid(row=0, columnspan=10)
                self.setup()

# if __name__ == '__main__':
#     Paint()
    
