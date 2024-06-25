import os
import json
import pprint
from pdf_command_builder import CommandDetails

from kivy.app import App
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.lang import Builder

from dataclasses import dataclass

@dataclass(frozen=True)
class ColumnDetails:
    categories: list[str]
    commands: list[dict]
    queries: list[dict]
    command_type_picker: list[str]


Builder.load_file(os.path.join(os.path.dirname(__file__), 'main_gui.kv'))

Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '400')
Config.set('graphics', 'resizable', True)

class MyApp(App):
    def build(self):
        # Read the contents of the file
        json_contents = None
        with open(os.path.join(os.path.dirname(__file__), '..', 'output.json'), 'r', encoding='utf8') as f:
            json_contents = json.load(f)
        # TODO: Maybe just add this data inside the json file itself?
        scope_categories = json_contents['DSO5012A']['Scope Queries'].keys() # column 1
        command_data = json_contents['DSO5012A']['Scope Queries']
        query_data = json_contents['DSO5012A']['Scope Commands']
        # 2nd Column is Query Or Command
        second_column_data = ['Query', 'Command']
        label = Label(text='Placeholder')
        column_details = ColumnDetails(categories=scope_categories, commands=command_data, queries=query_data, command_type_picker=second_column_data)
        self.root = ColumnedBoxLayout(orientation='horizontal',column_text_data=column_details)
        rv = RV(column_index=0, column_data=column_details.command_type_picker)
        self.root.add_widget(rv)
        self.root.enable_columns[0] = rv
        top_box = BoxLayout(orientation='vertical')
        top_box.add_widget(label)
        top_box.add_widget(self.root)
        return top_box

class RV(RecycleView):
    def __init__(self, column_index, column_data, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.selected_button_index: int | None = None
        self.data = [{'text': str(item), 'viewclass': 'LabelledButton', 'column_index': column_index, 'button_index': index, 'is_selected': False, 'parent_recycleview': self} for index, item in enumerate(column_data)]

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
    enable_columns = ListProperty([None, None,None])
    focused_index = NumericProperty(0)
    column_text_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        # Ensure column_text_data is provided and not None
        self._send_mode = ''
        if 'column_text_data' not in kwargs or kwargs['column_text_data'] is None:
            raise ValueError("column_text_data cannot be None")
        super().__init__(**kwargs)
    
    def add_column(self, invoked_column, button_text):
        next_index = invoked_column + 1
        if next_index >= len(self.enable_columns):
            return
        # Here, we need to decide what data to pass into the columns
        data_to_pass_in = None
        if self.focused_index == 0:
            data_to_pass_in = self.column_text_data.categories
            self._send_mode = button_text
        if self.focused_index == 1:
            if self._send_mode == 'Query':
                data_to_pass_in = self.column_text_data.queries[button_text]
            elif self._send_mode == 'Command':
                data_to_pass_in = self.column_text_data.commands[button_text]
        next_recycleview = RV(column_index=next_index,column_data=data_to_pass_in)
        self.enable_columns[next_index] = next_recycleview
        self.add_widget(next_recycleview)
        self.focused_index = next_index

    def remove_existing_columns(self, invoked_column):
        for column_index in range(self.focused_index, invoked_column, -1):
            # go backwards and remove the columns
            targeted_recycleview = self.enable_columns[column_index]
            self.enable_columns[column_index] = None
            self.remove_widget(targeted_recycleview)
            del targeted_recycleview
        # mark the current focused_index as the current column index
        self.focused_index = invoked_column


class LabelledButton(Button, RecycleDataViewBehavior):
    def on_release(self):
        # Adding some custom state here for desired behavior
        print(f'RELEASED button of {self.text}, button index {self.button_index} at column index {self.column_index}')
        # We'll always swap the button states. A new column will only be added if there are enough indexes.
        self.parent_recycleview.swap_selected_button_states(self.button_index) # NOTE: This may need to be added to the refresh state instead!
        # Check if it's the top-level column, or a bottom level column that's being changed.
        column_box_parent = self.get_columned_box_layout()
        if column_box_parent.focused_index == self.column_index:
            if self.column_index >= len(column_box_parent.enable_columns):
                return
            column_box_parent.add_column(self.column_index, self.text)
        else:
            column_box_parent.remove_existing_columns(self.column_index)
            column_box_parent.add_column(self.column_index, self.text)            

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