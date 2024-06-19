import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.lang import Builder

Builder.load_file(os.path.join(os.path.dirname(__file__), 'main_gui.kv'))

class MyApp(App):
    def build(self):
        # Read the contents of the file
        contents = None
        # Create a RecycleView to display the contents
        rv = RV()
        # Create a label to display the contents
        label = Label(text='fISH')
        # Create a layout and add the label to it
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(label)
        layout.add_widget(RV())

        return layout
    
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(100)]

if __name__ == '__main__':
    MyApp().run()