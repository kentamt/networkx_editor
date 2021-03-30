from enum import Enum, auto

import tkinter as tk  # python 3
import networkx as nx
import matplotlib.pyplot as plt


class Action(Enum):
    ADD_NODE = auto(),
    ADD_EDGE = auto(),
    DEL_EDGE = auto(),


class Editor(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.G = None # nx.DiGraph()  # 有向グラフ (Directed Graph)
        self.counts = 0
        self.parent = parent
        favicon_data ='''R0lGODlhJgAmAHAAACH5BAEAAPwALAAAAAAmACYAhwAAAAAAMwAAZgAAmQAAzAAA/wArAAArMwArZgArmQArzAAr/wBVAABVMwBVZgBVmQBVzABV/wCAAACAMwCAZgCAmQCAzACA/wCqAACqMwCqZgCqmQCqzACq/wDVAADVMwDVZgDVmQDVzADV/wD/AAD/MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMrADMrMzMrZjMrmTMrzDMr/zNVADNVMzNVZjNVmTNVzDNV/zOAADOAMzOAZjOAmTOAzDOA/zOqADOqMzOqZjOqmTOqzDOq/zPVADPVMzPVZjPVmTPVzDPV/zP/ADP/MzP/ZjP/mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YrAGYrM2YrZmYrmWYrzGYr/2ZVAGZVM2ZVZmZVmWZVzGZV/2aAAGaAM2aAZmaAmWaAzGaA/2aqAGaqM2aqZmaqmWaqzGaq/2bVAGbVM2bVZmbVmWbVzGbV/2b/AGb/M2b/Zmb/mWb/zGb//5kAAJkAM5kAZpkAmZkAzJkA/5krAJkrM5krZpkrmZkrzJkr/5lVAJlVM5lVZplVmZlVzJlV/5mAAJmAM5mAZpmAmZmAzJmA/5mqAJmqM5mqZpmqmZmqzJmq/5nVAJnVM5nVZpnVmZnVzJnV/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwAM8wAZswAmcwAzMwA/8wrAMwrM8wrZswrmcwrzMwr/8xVAMxVM8xVZsxVmcxVzMxV/8yAAMyAM8yAZsyAmcyAzMyA/8yqAMyqM8yqZsyqmcyqzMyq/8zVAMzVM8zVZszVmczVzMzV/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8Amf8AzP8A//8rAP8rM/8rZv8rmf8rzP8r//9VAP9VM/9VZv9Vmf9VzP9V//+AAP+AM/+AZv+Amf+AzP+A//+qAP+qM/+qZv+qmf+qzP+q///VAP/VM//VZv/Vmf/VzP/V////AP//M///Zv//mf//zP///wAAAAAAAAAAAAAAAAj/APcJHEiQoKY0OWYkQJAgxxhNBSNKlKgpgQABAxAIYLjR4kaIE0MK1HRRwEKGKE9a9AhSZMEZHREgyGiRY82FGU26HLhsI0qaP2UuHIryojKXyjqaFLrxosacNWcWJRYyGkapODUiUKNpE7GDK5f+FHBUos+TOceIHLMxY0aOEmdovLkx2s59D8SGLUhs6VABOe4OZJtVY8t9PmkCFkwwzVm4I/VuZFwwwducIBUyzGlXoj53w+iFvEpUYFOZAwJHJJYKlWtUqcoWTCM1576+KclGHOY6le/WqHiZlclRk5raMiPSg/0qlatUzVu7i7iyJpkcRFNHfAXbOXTYz1FF/0xzE0GOHI8pRQTvO3p0VJ0HkrQpVKqAw/vo+Wnfmrt3VO3wFZNJcmWFHzHsoeKegqhQZZBbKOUwl0ZprPfcd975hopoBhE3FHpoqVVQdM+R6F1EY0AI2HEraRRRPahcyF5rsg2kEkNj4PbXMrsxB11rfgRYkFVY3YdYi4spx91rr3BYEGH2CYRebjXy5eRwKDEU2UJLCSBQlTvRN4CRpmVpkWqUTcmliwMlldWZaS6lGH5qzrURjy4tYydTCQwHFJc5gPklW28R5aVERNakonmUaJKJGmNohZZ9eErUk198NpXTZhNy6WBIeipF1JoJvMmRRpW6NGVQmIpVVJ+UaR4yZqf0zeQRmZSNpOiEJjWVAH65yodQgeelAexEAQEAOw=='''
        self.parent.tk.call('wm', 'iconphoto', self.parent._w, tk.PhotoImage(data=favicon_data))

        # create a canvas
        self.canvas = tk.Canvas(width=640, height=480, background="lightgray")
        self.canvas.pack(fill="both", expand=True)

        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_center_click)

        self.colors = ('blue', 'orange', 'gray', 'green')
        # loc_types = tk.StringVar(value=self.location_types)
        # self.listbox = tk.Listbox(listvariable=loc_types, height=5, selectmode=tk.SINGLE)
        # self.listbox.pack()
        # self.listbox.select_set(0)  # This only sets focus on the first item.
        # self.listbox.event_generate("<<ListboxSelect>>")

        self.menu_bar = tk.Menu(self)
        parent.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=file_menu)

        # add a submenu
        sub_menu = tk.Menu(file_menu, tearoff=0)
        sub_menu.add_command(label='Graph', command=self.init_graph)
        sub_menu.add_command(label='Di graph', command=self.init_di_graph)
        file_menu.add_cascade(
            label="New",
            menu=sub_menu
        )
        file_menu.add_command(label='Open')
        file_menu.add_command(label='Save as...')

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label='Add node', command=self.add_node_mode)
        self.edit_menu.add_command(label='Add edge', command=self.add_edge_mode)
        self.edit_menu.add_command(label='Delete node', command=self.del_edge_mode)
        self.edit_menu.entryconfig(0, state=tk.DISABLED)
        self.edit_menu.entryconfig(1, state=tk.DISABLED)
        self.edit_menu.entryconfig(2, state=tk.DISABLED)
        self.menu_bar.add_cascade(label='Edit', menu=self.edit_menu)



        # 右クリックでノードのattr編集
        self.attribute_dict = {i: "" for i in range(5)}
        self.new_window = None

        # 内部変数
        self.selected_nodes = []
        self.delete_candidate = None
        self.node_config_dict = {}

        self.entry_key_list = []
        self.entry_item_list = []

        self.is_di_graph = False

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

    def create_new_window(self, event):

        def set_attribute():
            tmp_dict = {}
            for ek, ei in zip(self.entry_key_list, self.entry_item_list):
                key = ek.get()
                item = ei.get()
                tmp_dict[key] = item
            self.attribute_dict = tmp_dict

            # item_idx_list = self.listbox.curselection()[0]
            color = self.colors[0]
            # name = str(self.counts)
            name =self.node_name_entry.get()
            self.create_node(event.x, event.y, color, name)
            self.new_window.destroy()

        self.new_window = tk.Toplevel(self.parent)
        root_x = self.parent.winfo_rootx()
        root_y = self.parent.winfo_rooty()
        win_x = root_x + event.x
        win_y = root_y + event.y
        self.new_window.geometry(f'250x200+{win_x}+{win_y}')
        print(self.attribute_dict)

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
        for key in self.attribute_dict.keys():
            entry_key = tk.Entry(self.new_window)
            entry_item = tk.Entry(self.new_window)
            self.entry_key_list.append(entry_key)
            self.entry_item_list.append(entry_item)

            entry_key.insert(0, key)
            entry_item.insert(0, self.attribute_dict[key])
            entry_key.grid(row=r, column=0)
            entry_item.grid(row=r, column=1)

            r += 1

        # color

        set_button = tk.Button(self.new_window, text="New node", command=set_attribute)
        set_button.grid(row=r, column=1)

    def add_node_mode(self):
        self.action = Action.ADD_NODE
        self.selected_nodes = []
        self.delete_candidate = None
        self.reset_node_color()

        print(self.action)

    def add_edge_mode(self):
        self.action = Action.ADD_EDGE
        self.selected_nodes = []
        self.delete_candidate = None

        self.reset_node_color()

        print(self.action)

    def del_edge_mode(self):
        self.action = Action.DEL_EDGE
        self.selected_nodes = []
        self.delete_candidate = None

        self.reset_node_color()

        print(self.action)

    def on_right_click(self, event):

        if self.action == Action.ADD_NODE:
            self.create_new_window(event)

            # item_idx_list = self.listbox.curselection()[0]
            # color = self.location_colors[item_idx_list]
            # name = str(self.counts)
            # self.create_node(event.x, event.y, color, name)

        elif self.action == Action.ADD_EDGE:

            # 2点選ぶ。3点目が選ばれたとき、最初の1点を削除する
            tag = 'token'
            obj_type = 'oval'
            oid = self.get_id_from(event, obj_type, tag)
            if oid is None:
                return

            tags = self.canvas.gettags(oid)
            if tags[0] != 'token':
                return
            node_name = tags[1]

            if node_name not in self.selected_nodes:
                self.selected_nodes.append(node_name)

            if len(self.selected_nodes) == 3:
                del self.selected_nodes[0]

            print(self.selected_nodes)

            # 選ばれた2点だけ色をつける
            self.reset_node_color()

            for n in self.selected_nodes:
                self.canvas.itemconfig(n, fill='red')

        elif self.action == Action.DEL_EDGE:
            try:
                tag = 'token'
                obj_type = 'oval'
                oid = self.get_id_from(event, obj_type, tag)
                tags = self.canvas.gettags(oid)

                if tags[0] != 'token':
                    return
                node_name = tags[1]
                self.delete_candidate = node_name
                self.canvas.itemconfig(node_name, fill='red')

            except:
                pass

    def reset_node_color(self):
        for n in self.node_config_dict.keys():
            fill = self.node_config_dict[n]['fill']
            self.canvas.itemconfig(n, fill=fill)

    def on_center_click(self, event):
        print('on center click')
        if self.action == Action.ADD_NODE:
            pass
        elif self.action == Action.ADD_EDGE:
            self.add_edge()
        elif self.action == Action.DEL_EDGE:
            self.delete_node()

    def delete_node(self):

        if self.delete_candidate is not None:

            # node for tk
            self.canvas.delete(self.delete_candidate)

            # edge for tk
            if self.is_di_graph:
                for edge in self.G.in_edges(self.delete_candidate):
                    edge_name = 'edge_' + edge[0] + '_' + edge[1]
                    self.canvas.delete(edge_name)
                    edge_name = 'edge_' + edge[1] + '_' + edge[0]
                    self.canvas.delete(edge_name)

                for edge in self.G.out_edges(self.delete_candidate):
                    edge_name = 'edge_' + edge[0] + '_' + edge[1]
                    self.canvas.delete(edge_name)
                    edge_name = 'edge_' + edge[1] + '_' + edge[0]
                    self.canvas.delete(edge_name)
            else:
                for edge in self.G.edges(self.delete_candidate):
                    edge_name = 'edge_' + edge[0] + '_' + edge[1]
                    self.canvas.delete(edge_name)
                    edge_name = 'edge_' + edge[1] + '_' + edge[0]
                    self.canvas.delete(edge_name)


            # node and dedge for nx
            self.G.remove_node(self.delete_candidate)
            self.delete_candidate = None

    def add_edge(self):

        if len(self.selected_nodes) == 2:
            node_and_pos = nx.get_node_attributes(self.G, 'pos')
            node_from = self.selected_nodes[1]
            node_to = self.selected_nodes[0]
            pos_from = node_and_pos[node_from]
            pos_to = node_and_pos[node_to]
            coord = (pos_from[0], pos_from[1], pos_to[0], pos_to[1])
            edge_name = f'edge_{node_from}_{node_to}'

            if (node_from, node_to) not in self.G.edges:
                if self.is_di_graph:
                    self.canvas.create_line(coord, arrow=tk.FIRST, fill='black', tags=("edge", edge_name))
                else:
                    self.canvas.create_line(coord, arrow=tk.BOTH, fill='black', tags=("edge", edge_name))

                self.G.add_edge(node_from, node_to)
                print(self.G.edges)
                print(edge_name)
        else:
            pass

    def create_node(self, x, y, color, node_name):
        """Create a token at the given coordinate in the given color"""

        if node_name in self.G.nodes:
            print(f'{node_name} exists.')
            return

        obj = self.canvas.create_oval(
            x - 5,
            y - 5,
            x + 5,
            y + 5,
            outline=color,
            fill=color,
            tags=("token", node_name),
        )

        config = {opt: self.canvas.itemcget(obj, opt) for opt in self.canvas.itemconfig(obj)}
        self.node_config_dict[node_name] = config

        self.G.add_node(node_name, pos=(x, y))
        for attr, value in self.attribute_dict.items():
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

        # pos = {}
        # for n in self.G.nodes:
        #     pos[n] = self.G.nodes[n]['pos']
        # nx.draw_networkx(self.G, pos)
        # plt.show()

    def drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        # move the object the appropriate amount
        self.canvas.move(self._drag_data["node_name"], delta_x, delta_y)

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
                d0 = (p0[0] - event.x)**2 + (p0[1] - event.y)**2
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

            # node_from = e[1]
            # node_to = e[0]
            # pos_from = node_and_pos[node_from]
            # pos_to = node_and_pos[node_to]
            # coord = (pos_from[0], pos_from[1], pos_to[0], pos_to[1])
            # edge_name = f'edge_{node_from}_{node_to}'
            # self.canvas.coords(edge_name, coord)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        node_name = self.canvas.gettags(self._drag_data['item'])[1]
        self.G.nodes[node_name]['pos'] = (event.x, event.y)


if __name__ == "__main__":
    root = tk.Tk()
    Editor(root).pack(fill="both", expand=True)
    root.mainloop()
