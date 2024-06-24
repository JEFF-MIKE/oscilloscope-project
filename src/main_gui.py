import os
import json
import pprint
from pdf_command_builder import CommandDetails

from kivy.app import App
from kivy.properties import ColorProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleViewBehavior
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior

Builder.load_file(os.path.join(os.path.dirname(__file__), 'main_gui.kv'))

Config.set('graphics', 'minimum_width', '640')
Config.set('graphics', 'minimum_height', '480')
Config.set('graphics', 'resizable', False)

class MyApp(App):
    def build(self):
        # Read the contents of the file
        json_contents = None
        with open(os.path.join(os.path.dirname(__file__), '..', 'output.json'), 'r', encoding='utf8') as f:
            json_contents = json.load(f)
        print(json_contents["DSO5012A"]["Scope Queries"].keys())
        label = Label(text='Placeholder')
        # Create a layout and add the label to it
        self.root = ColumnedBoxLayout(orientation='horizontal')
        rv = RV(column_index=0)
        self.root.add_widget(rv)
        self.root.enable_columns[0] = rv
        top_box = BoxLayout(orientation='vertical')
        top_box.add_widget(label)
        top_box.add_widget(self.root)
        return top_box

class RV(RecycleView):
    def __init__(self, column_index, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.selected_button_index: int | None = None
        self.data = [{'text': str(x), 'viewclass': 'LabelledButton', 'column_index': column_index, 'button_index': x, 'is_selected': False, 'parent_recycleview': self} for x in range(100)]

    def swap_selected_button_states(self, new_button_index):
        # Try doing this with copying the indexes, re-assigning them and then deleting instead to attempt to force the refresh
        new_selected_button = self.data[new_button_index].copy()
        old_selected_button = self.data[self.selected_button_index].copy() if self.selected_button_index is not None else None
        if self.selected_button_index == new_button_index:
            # enter toggle functionality
            new_selected_button['is_selected'] = not new_selected_button['is_selected']
            self.data[new_button_index] = new_selected_button
            return
        if old_selected_button is not None:
            old_selected_button['is_selected'] = False
            old_selected_button['background_color'] = (1, 1, 1, 1)
            self.data[self.selected_button_index] = old_selected_button
        new_selected_button['is_selected'] = True
        new_selected_button['background_color'] = (1, 0, 0, 1)
        # assign the indexes here.
        self.selected_button_index = new_button_index
        self.data[new_button_index] = new_selected_button

class ColumnedBoxLayout(BoxLayout):
    enable_columns = ListProperty([None, None,None,None])
    focused_index = NumericProperty(0)

class LabelledButton(Button, RecycleDataViewBehavior):
    def on_release(self):
        # Adding some custom state here for desired behavior
        print(f'RELEASED button of {self.text}, button index {self.button_index} at column index {self.column_index}')
        # We'll always swap the button states. A new column will only be added if there are enough indexes.
        self.parent_recycleview.swap_selected_button_states(self.button_index) # NOTE: This may need to be added to the refresh state instead!
        # Check if it's the top-level column, or a bottom level column that's being changed.
        if self.get_columned_box_layout().focused_index == self.column_index:
            if self.column_index >= len(self.get_columned_box_layout().enable_columns):
                return
            self.add_column()
        else:
            self.remove_existing_columns()
            self.add_column()

    def add_column(self):
        # make sure that we don't go above the column limit
        # print(f"Focused index is: {self.get_columned_box_layout().focused_index}, current index is: {self.column_index}")
        next_index = self.column_index + 1
        if next_index >= len(self.get_columned_box_layout().enable_columns):
            return
        next_rv = RV(column_index=next_index)
        self.get_columned_box_layout().enable_columns[next_index] = next_rv
        self.get_columned_box_layout().add_widget(next_rv)
        self.get_columned_box_layout().focused_index = next_index
        # for item in ToggleButtonBehavior.get_widgets(str(self.column_index)):
        #     pprint.pprint(dir(item))
    
    def remove_existing_columns(self):
        focused_index = self.get_columned_box_layout().focused_index
        for i in range(focused_index, self.column_index, -1):
            # go backwards and remove the columns
            targeted_rv = self.get_columned_box_layout().enable_columns[i]
            self.get_columned_box_layout().enable_columns[i] = None
            self.get_columned_box_layout().remove_widget(targeted_rv)
            del targeted_rv
        # mark the current focused_index as the current column index
        self.get_columned_box_layout().focused_index = self.column_index
            

    def get_columned_box_layout(self):
        # Traverse up the widget tree to find the ColumnedBoxLayout
        current_widget = self.parent
        while current_widget is not None:
            if isinstance(current_widget, ColumnedBoxLayout):
                return current_widget
            current_widget = current_widget.parent
        return None
    
    def refresh_view_attrs(self, rv, index, data):
        # For easier debugging, only print column index 0
        if data['column_index'] == 0:
            print(f'TRIGGERED REFRESH VIEW ATTRS FOR ITEM INDEX {index}, DATA IS {data}')
            print('RecycleView that caused this data to update was:', rv)
            pprint.pprint(data)
        if data['is_selected'] is True:
            # data['background_color'] = (1, 0, 0, 1)
            self.background_color = (1, 0, 0, 1)
        elif data['is_selected'] is False:
            self.background_color = (1, 1, 1, 1)
            # data['background_color'] = (1, 1, 1, 1)
        super(LabelledButton, self).refresh_view_attrs(rv, index, data)

if __name__ == '__main__':
    MyApp().run()