from enum import Enum, auto
from copy import deepcopy
import tkinter as tk  # python 3
import networkx as nx
import matplotlib.pyplot as plt


class Action(Enum):
    ADD_NODE = auto(),
    ADD_EDGE = auto(),
    DEL_EDGE = auto(),
    EDIT_NODE = auto(),
    EDIT_EDGE = auto()

class Editor(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        favicon_data = '''iVBORw0KGgoAAAANSUhEUgAAAEMAAABACAIAAADOPF2KAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAI3SURBVGhD7ZbbccMgEEVxakgZ8U+6SwXpLj9KGenBuWaZDeINK6ONhzMeR0KKxOEu4Mu2beYpeHF//z/LRB/LRB/LRB/LRB/LRB+n/e66Xt/ckTHb9u2OBJxjAo3Prx93YszH+yu+hT4nmAQaDHwkMrPnSU4DoN0vuV7W2jVEIRBCEsvKRB9TTbA00YKbQ7J8rUxGKcTyz/YTkJQRagAVv7uAUAOckMnVgkGkj3W42BYRkzLJdZTeTleFPZldXb4Sv5obJZ2ZWl3VEqreUGCeCXqJIedRlwx/khkmcCANd17UwJ3uqJOHz5PAIUnc+4FeHZyJ3yccg8Y+0W34Jqixi45M/L0suZGRBh7IB7a5g3bzmFYTaNzuG5njYm749n2o98RwbyQmTdUVaACc4sMpHaIhpG4SazC+DAMrwp3Pol5dBRNgy2x3VZgJhmDsCZVMyhrAXqU546D2+VQyqZqAOBZmQIwz6Q3ngXv8WD74r/sk659mFROss7Tg5sDV5N4ylgbhzjs5JpOg3zyuwDU1MJYh07Qz5mZLHAh13X8my7S9iM3/CiGZeczgHg9ydYXeJJ8ZSxJBuz29+e+i8q76tJoAyLgjS+NQBfCo77t+h1ra8w/oMDkWFtizSyOgLPPAVbgMRpBw52JOMyH2yZQCAbgaVLjPadUVk5shPoUCOzmTA1FkgsGmBTeH0hl/OLpMCrGUAwHqMknKVDWAxuoiGf9T1QCKVmEha8brY5noY5no41lMjPkFvCZR5OLJj/IAAAAASUVORK5CYII='''
        self.parent.tk.call('wm', 'iconphoto', self.parent._w, tk.PhotoImage(data=favicon_data))

        # create a canvas
        self.canvas = tk.Canvas(width=640, height=480, background="lightgray")
        self.canvas.pack(fill="both", expand=True)

        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_center_click)

        # Menu bar
        self.menu_bar = tk.Menu(self)
        parent.config(menu=self.menu_bar)
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=file_menu)
        # File > New > Graph | Directed graph
        sub_menu = tk.Menu(file_menu, tearoff=0)
        sub_menu.add_command(label='Graph', command=self.init_graph)
        sub_menu.add_command(label='Directed graph', command=self.init_di_graph)
        file_menu.add_cascade(label="New", menu=sub_menu)
        # File > Open
        file_menu.add_command(label='Open')
        # File > Save as...
        file_menu.add_command(label='Save as...')

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        # Edit > Add node
        self.edit_menu.add_command(label='Add node', command=self.add_node_mode)
        # Edit > Add edge
        self.edit_menu.add_command(label='Add edge', command=self.add_edge_mode)
        # Edit > Delete node
        self.edit_menu.add_command(label='Delete node', command=self.del_edge_mode)
        # Edit > Edit node
        self.edit_menu.add_command(label='Edit node', command=self.edit_node_mode)
        # Edit > Edit node
        self.edit_menu.add_command(label='Edit edge', command=self.edit_edge_mode)

        # All actions are disabled at the beginning
        self.edit_menu.entryconfig(0, state=tk.DISABLED)
        self.edit_menu.entryconfig(1, state=tk.DISABLED)
        self.edit_menu.entryconfig(2, state=tk.DISABLED)
        self.menu_bar.add_cascade(label='Edit', menu=self.edit_menu)

        # New window
        self.new_window = None

        # Attributes for new node and edge
        self.node_attr_dict = {i: "" for i in range(5)}
        self.edge_attr_dict = {i: "" for i in range(5)}
        self.edit_node_attr_dict = {}

        # params
        self.G = None
        self.selected_nodes = []
        self.selected_node = None
        self.node_config_dict = {}
        self.counts = 0
        self.entry_key_list = []
        self.entry_item_list = []
        self.is_di_graph = False
        self.colors = ('skyblue', 'orange', 'gray', 'green')
        self.node_name_entry = None

        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # State
        self.action = Action.ADD_NODE

    def init_graph(self):
        self.is_di_graph = False
        self.G = nx.Graph()
        self.canvas.delete(tk.ALL)

        self.edit_menu.entryconfig(0, state=tk.NORMAL)
        self.edit_menu.entryconfig(1, state=tk.NORMAL)
        self.edit_menu.entryconfig(2, state=tk.NORMAL)

    def init_di_graph(self):
        self.is_di_graph = True
        self.G = nx.DiGraph()
        self.canvas.delete(tk.ALL)

        self.edit_menu.entryconfig(0, state=tk.NORMAL)
        self.edit_menu.entryconfig(1, state=tk.NORMAL)
        self.edit_menu.entryconfig(2, state=tk.NORMAL)

    def create_new_window_for_node(self, event):

        def set_attribute():
            tmp_dict = {}
            for ek, ei in zip(self.entry_key_list, self.entry_item_list):
                key = ek.get()
                item = ei.get()
                tmp_dict[key] = item
            self.node_attr_dict = tmp_dict

            # item_idx_list = self.listbox.curselection()[0]
            color = self.colors[0]
            # name = str(self.counts)
            name = self.node_name_entry.get()
            self.create_node(event.x, event.y, color, name)
            self.new_window.destroy()
            self.new_window = None

        self.new_window = tk.Toplevel(self.parent)
        root_x = self.parent.winfo_rootx()
        root_y = self.parent.winfo_rooty()
        win_x = root_x + event.x
        win_y = root_y + event.y
        self.new_window.geometry(f'250x200+{win_x}+{win_y}')
        print(self.node_attr_dict)

        r = 0
        self.entry_item_list = []
        self.entry_key_list = []

        r += 1
        label = tk.Label(self.new_window, text='Node name')
        label.grid(row=r, column=0)
        self.node_name_entry = tk.Entry(self.new_window)
        self.node_name_entry.insert(0, f'node_name_{self.counts}')
        self.node_name_entry.grid(row=r, column=1)

        r += 1
        label = tk.Label(self.new_window, text='Key')
        label.grid(row=r, column=0)
        label = tk.Label(self.new_window, text='Item')
        label.grid(row=r, column=1)
        r += 1
        for key in self.node_attr_dict.keys():
            entry_key = tk.Entry(self.new_window)
            entry_item = tk.Entry(self.new_window)
            self.entry_key_list.append(entry_key)
            self.entry_item_list.append(entry_item)

            entry_key.insert(0, key)
            entry_item.insert(0, self.node_attr_dict[key])
            entry_key.grid(row=r, column=0)
            entry_item.grid(row=r, column=1)

            r += 1

        set_button = tk.Button(self.new_window, text="New node", command=set_attribute)
        set_button.grid(row=r, column=1)

    def create_new_window_for_edge(self, event):

        def set_attribute():
            tmp_dict = {}
            for ek, ei in zip(self.entry_key_list, self.entry_item_list):
                key = ek.get()
                item = ei.get()
                tmp_dict[key] = item
            self.edge_attr_dict = tmp_dict

            self.add_edge()
            self.new_window.destroy()
            self.new_window = None

        self.new_window = tk.Toplevel(self.parent)
        root_x = self.parent.winfo_rootx()
        root_y = self.parent.winfo_rooty()
        win_x = root_x + event.x
        win_y = root_y + event.y
        self.new_window.geometry(f'250x200+{win_x}+{win_y}')
        print(self.edge_attr_dict)

        r = 0
        self.entry_item_list = []
        self.entry_key_list = []

        label = tk.Label(self.new_window, text='Key')
        label.grid(row=r, column=0)
        label = tk.Label(self.new_window, text='Item')
        label.grid(row=r, column=1)
        r += 1
        for key in self.edge_attr_dict.keys():
            entry_key = tk.Entry(self.new_window)
            entry_item = tk.Entry(self.new_window)
            self.entry_key_list.append(entry_key)
            self.entry_item_list.append(entry_item)

            entry_key.insert(0, key)
            entry_item.insert(0, self.edge_attr_dict[key])
            entry_key.grid(row=r, column=0)
            entry_item.grid(row=r, column=1)

            r += 1

        set_button = tk.Button(self.new_window, text="New edge", command=set_attribute)
        set_button.grid(row=r, column=1)


    def create_new_window_for_edit_node(self, event):

        def set_attribute():
            tmp_dict = {}
            for ek, ei in zip(self.entry_key_list, self.entry_item_list):
                key = ek.get()
                item = ei.get()
                tmp_dict[key] = item
            self.edit_node_attr_dict = tmp_dict

            # item_idx_list = self.listbox.curselection()[0]
            color = self.colors[0]
            # name = str(self.counts)
            name = self.node_name_entry.get()
            # self.create_node(event.x, event.y, color, name)
            self.edit_node(name)

            self.selected_node = None
            self.selected_nodes = []
            self.reset_node_color()

            self.new_window.destroy()
            self.new_window = None

        self.new_window = tk.Toplevel(self.parent)
        root_x = self.parent.winfo_rootx()
        root_y = self.parent.winfo_rooty()
        win_x = root_x + event.x
        win_y = root_y + event.y
        self.new_window.geometry(f'250x200+{win_x}+{win_y}')
        print(self.node_attr_dict)

        r = 0
        self.entry_item_list = []
        self.entry_key_list = []

        r += 1
        label = tk.Label(self.new_window, text='Node name')
        label.grid(row=r, column=0)
        self.node_name_entry = tk.Entry(self.new_window)
        self.node_name_entry.insert(0, self.selected_node)
        self.node_name_entry.grid(row=r, column=1)

        r += 1
        label = tk.Label(self.new_window, text='Key')
        label.grid(row=r, column=0)
        label = tk.Label(self.new_window, text='Item')
        label.grid(row=r, column=1)
        r += 1

        self.edit_node_attr_dict = self.G.nodes.data()[self.selected_node]
        for key in self.edit_node_attr_dict.keys():
            if key == 'pos':
                continue
            entry_key = tk.Entry(self.new_window)
            entry_item = tk.Entry(self.new_window)
            self.entry_key_list.append(entry_key)
            self.entry_item_list.append(entry_item)

            entry_key.insert(0, key)
            entry_item.insert(0, self.edit_node_attr_dict[key])
            entry_key.grid(row=r, column=0)
            entry_item.grid(row=r, column=1)

            r += 1

        set_button = tk.Button(self.new_window, text="Edit node", command=set_attribute)
        set_button.grid(row=r, column=1)


    def add_node_mode(self):
        self.action = Action.ADD_NODE
        self.selected_nodes = []
        self.selected_node = None
        self.reset_node_color()
        print(self.action)

    def add_edge_mode(self):
        self.action = Action.ADD_EDGE
        self.selected_nodes = []
        self.selected_node = None
        self.reset_node_color()
        print(self.action)

    def del_edge_mode(self):
        self.action = Action.DEL_EDGE
        self.selected_nodes = []
        self.selected_node = None
        self.reset_node_color()
        print(self.action)

    def edit_node_mode(self):
        print(self.G.nodes.data())
        self.action = Action.EDIT_NODE
        self.selected_nodes = []
        self.selected_node = None
        self.reset_node_color()
        print(self.action)

    def edit_edge_mode(self):
        self.action = Action.EDIT_EDGE
        self.selected_nodes = []
        self.selected_node = None
        self.reset_node_color()
        print(self.action)

    def on_right_click(self, event):

        if self.action == Action.ADD_NODE:
            if self.G is not None and self.new_window is None:
                self.create_new_window_for_node(event)

        elif self.action == Action.ADD_EDGE:

            tag = 'token'
            obj_type = 'oval'
            oid = self.get_id_from(event, obj_type, tag)
            if oid is None:
                return

            tags = self.canvas.gettags(oid)
            if tags[0] != 'token':
                return
            node_name = tags[1]

            # if node_name not in self.selected_nodes:
            self.selected_nodes.append(node_name)

            if len(self.selected_nodes) == 3:
                del self.selected_nodes[0]

            self.reset_node_color()

            for n in self.selected_nodes:
                self.canvas.itemconfig(n, fill='red')

        elif self.action == Action.DEL_EDGE:

            tag = 'token'
            obj_type = 'oval'
            oid = self.get_id_from(event, obj_type, tag)
            if oid is None:
                return
            tags = self.canvas.gettags(oid)

            if tags[0] != 'token':
                return
            node_name = tags[1]
            self.selected_node = node_name
            self.reset_node_color()
            self.canvas.itemconfig(node_name, fill='red')

        elif self.action == Action.EDIT_NODE:
            tag = 'token'
            obj_type = 'oval'
            oid = self.get_id_from(event, obj_type, tag)
            if oid is None:
                return
            tags = self.canvas.gettags(oid)
            if tags[0] != 'token':
                return

            node_name = tags[1]
            self.selected_node = node_name
            self.reset_node_color()
            self.canvas.itemconfig(node_name, fill='red')


    def on_center_click(self, event):
        print('on center click')
        if self.action == Action.ADD_NODE:
            pass
        elif self.action == Action.ADD_EDGE:
            self.create_new_window_for_edge(event)
        elif self.action == Action.DEL_EDGE:
            self.delete_node()
        elif self.action == Action.EDIT_NODE:
            self.create_new_window_for_edit_node(event)

    def reset_node_color(self):
        for n in self.node_config_dict.keys():
            fill = self.node_config_dict[n]['fill']
            self.canvas.itemconfig(n, fill=fill)

    def delete_node(self):

        if self.selected_node is not None:

            # node for tk
            self.canvas.delete(self.selected_node)

            # edge for tk
            if self.is_di_graph:
                for edge in self.G.in_edges(self.selected_node):
                    edge_name = 'edge_' + edge[0] + '_' + edge[1]
                    self.canvas.delete(edge_name)
                    edge_name = 'edge_' + edge[1] + '_' + edge[0]
                    self.canvas.delete(edge_name)

                for edge in self.G.out_edges(self.selected_node):
                    edge_name = 'edge_' + edge[0] + '_' + edge[1]
                    self.canvas.delete(edge_name)
                    edge_name = 'edge_' + edge[1] + '_' + edge[0]
                    self.canvas.delete(edge_name)
            else:
                for edge in self.G.edges(self.selected_node):
                    edge_name = 'edge_' + edge[0] + '_' + edge[1]
                    self.canvas.delete(edge_name)
                    edge_name = 'edge_' + edge[1] + '_' + edge[0]
                    self.canvas.delete(edge_name)

            # node and dedge for nx
            self.G.remove_node(self.selected_node)
            self.selected_node = None

    def edit_node(self, node_name):
        if node_name != self.selected_node and node_name in self.G.nodes:
            print(f'{node_name} exists.')
            return

        for attr, value in self.edit_node_attr_dict.items():
            if value != "":
                self.G.nodes[self.selected_node][attr] = value

        if node_name != self.selected_node:
            # Change nx graph name
            mapping = {self.selected_node : node_name}
            self.G = nx.relabel_nodes(self.G, mapping)
            print(self.G)

            # Change tk node name
            for obj in self.canvas.find_withtag('token'):
                config = {opt: self.canvas.itemcget(obj, opt) for opt in self.canvas.itemconfig(obj)}
                config['tags'] = config['tags'].split(' ')
                if config["tags"][0] == 'token' and config['tags'][1] == self.selected_node:
                    config['tags'][1] = node_name
                    self.canvas.create_oval(*self.canvas.coords(obj), **config)
                    self.canvas.delete(self.selected_node)

                    # 色をリセットする関数で読んでいるconfigのリストをここで更新すること

            # Change tk edge name
            for obj in self.canvas.find_withtag('edge'):
                config = {opt: self.canvas.itemcget(obj, opt) for opt in self.canvas.itemconfig(obj)}
                config['tags'] = config['tags'].split(' ')
                if config["tags"][0] == 'edge' and self.selected_node in config['tags'][1]:

                    # case: edge_XXXX_selected_node
                    edge_name = config['tags'][1]
                    config['tags'][1] = edge_name.replace(self.selected_node, node_name)

                    self.canvas.create_line(*self.canvas.coords(obj), **config)
                    self.canvas.delete(edge_name)
                    self.canvas.tag_lower(config['tags'][1])

        # DEBUG
        for k, v in self.G.nodes(data=True):
            print(k, v)

    def add_edge(self):

        if self.selected_nodes[0] == self.selected_nodes[1]:
            return

        if len(self.selected_nodes) == 2:
            node_and_pos = nx.get_node_attributes(self.G, 'pos')
            node_from = self.selected_nodes[1]
            node_to = self.selected_nodes[0]
            edge_name = f'edge_{node_from}_{node_to}'

            if (node_from, node_to) not in self.G.edges:
                self.G.add_edge(node_from, node_to)
                for attr, value in self.node_attr_dict.items():
                    if value != "":
                        self.G.edges[node_from, node_to][attr] = value

                pos_from = node_and_pos[node_from]
                pos_to = node_and_pos[node_to]
                coord = (pos_from[0], pos_from[1], pos_to[0], pos_to[1])

                if self.is_di_graph:
                    self.canvas.create_line(coord, arrow=tk.FIRST, fill='black', tags=("edge", edge_name))
                else:
                    self.canvas.create_line(coord, arrow=tk.BOTH, fill='black', tags=("edge", edge_name))

                self.canvas.tag_lower(edge_name)

        else:
            pass

    def create_node(self, x, y, color, node_name):
        """Create a token at the given coordinate in the given color"""

        if node_name in self.G.nodes:
            print(f'{node_name} exists.')
            return
        radius = 6
        obj = self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            outline='blue',
            fill=color,
            tags=("token", node_name),
        )

        config = {opt: self.canvas.itemcget(obj, opt) for opt in self.canvas.itemconfig(obj)}
        self.node_config_dict[node_name] = config

        self.G.add_node(node_name, pos=(x, y))
        for attr, value in self.node_attr_dict.items():
            if value != "":
                self.G.nodes[node_name][attr] = value

        self.counts += 1  # TODO: 作るときに手入力できめる

        for k, v in self.G.nodes(data=True):
            print(k, v)

    def drag_start(self, event):
        """Begining drag of an object"""

        tag = 'token'
        obj_type = 'oval'
        item = self.get_id_from(event, obj_type, tag)

        # record the item and its location
        self._drag_data["item"] = item
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data['node_name'] = self.canvas.gettags(item)[1]  # self._drag_data['item'])[1]
        print(self._drag_data['node_name'])

    def get_id_from(self, event, obj_type, tag):
        draft = tk.Canvas(self.canvas)
        draft.delete(tk.ALL)
        concerned = self.canvas.find_withtag(tag)  # what you want
        for obj in concerned:  # copy on draft
            # first, get the method to use
            if self.canvas.type(obj) == obj_type:
                create = draft.create_line
            # use "elif ..." to copy more types of objects
            else:
                continue

            # copy the element with its attributes
            config = {opt: self.canvas.itemcget(obj, opt) for opt in self.canvas.itemconfig(obj)}
            config["tags"] = str(obj)  # I can retrieve the ID in "w" later with this trick
            draft.create_oval(*self.canvas.coords(obj), **config)
        # use coordinates relative to the canvas
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = draft.find_closest(x, y)  # ID in draft (as a tuple of len 1)
        if item:
            item = int(draft.gettags(*item)[0])  # ID in self.canvas
        else:
            item = None  # closest not found
        return item

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data['node_name'] = None


    def drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        # move the object the appropriate amount
        self.canvas.move(self._drag_data["node_name"], delta_x, delta_y)
        node_name = self.canvas.gettags(self._drag_data['item'])[1]
        self.G.nodes[node_name]['pos'] = (event.x, event.y)

        # move edges connected by target node
        node_and_pos = nx.get_node_attributes(self.G, 'pos')

        for e in self.G.edges:

            if self.is_di_graph:
                node_from = e[0]
                node_to = e[1]
                pos_from = node_and_pos[node_from]
                pos_to = node_and_pos[node_to]
                coord = (pos_from[0], pos_from[1], pos_to[0], pos_to[1])

                edge_name = f'edge_{node_from}_{node_to}'
                self.canvas.coords(edge_name, coord)
            else:
                p0 = node_and_pos[e[0]]
                p1 = node_and_pos[e[1]]
                d0 = (p0[0] - event.x) ** 2 + (p0[1] - event.y) ** 2
                d1 = (p1[0] - event.x) ** 2 + (p1[1] - event.y) ** 2
                if d0 < d1:
                    node_from = e[0]
                    node_to = e[1]
                else:
                    node_from = e[1]
                    node_to = e[0]

                pos_from = node_and_pos[node_from]
                pos_to = node_and_pos[node_to]
                coord = (pos_from[0], pos_from[1], pos_to[0], pos_to[1])

                for edge_name in [f'edge_{node_from}_{node_to}', f'edge_{node_to}_{node_from}']:
                    self.canvas.coords(edge_name, coord)


        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


if __name__ == "__main__":
    root = tk.Tk()
    Editor(root).pack(fill="both", expand=True)
    root.mainloop()

