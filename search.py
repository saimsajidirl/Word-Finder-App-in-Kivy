import os
import threading
from functools import partial
import subprocess
import platform

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.text import LabelBase

from kivymd.app import MDApp
from kivymd.theming import ThemeManager

import PyPDF2
from docx import Document
import openpyxl



class GlowingLabel(Label):
    """A label that has a pulsing glow effect."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glow_anim = Animation(opacity=0.5, duration=1) + Animation(opacity=1, duration=1)
        self.glow_anim.repeat = True
        self.glow_anim.start(self)

class PulseButton(ButtonBehavior, Image):
    """A button that uses an image and scales up slightly when pressed."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'search_icon.png'  # Replace with your icon path
        self.size_hint = (None, None)
        self.size = (50, 50)
        self.pulse_anim = Animation(size=(60, 60), duration=0.5) + Animation(size=(50, 50), duration=0.5)
        self.pulse_anim.repeat = True

    def on_press(self):
        self.pulse_anim.start(self)



class AdvancedFileSearchApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stop_search_flag = threading.Event()
        self.search_thread = None
        self.search_cache = {}  # Cache dictionary for search results

    def build(self):
        # Theme setup
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.accent_palette = "Amber"

        # Root layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Background rectangle
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)

        # Search bar
        self.search_bar = BoxLayout(size_hint_y=None, height=50)
        self.search_input = TextInput(hint_text='Enter search word', multiline=False, font_size=18)
        self.search_button = PulseButton(on_press=self.start_search)
        self.stop_button = Button(text='Stop Search', size_hint=(None, None), size=(100, 50), disabled=True)
        self.stop_button.bind(on_press=self.stop_searching) 
        self.search_bar.add_widget(self.search_input)
        self.search_bar.add_widget(self.search_button)
        self.search_bar.add_widget(self.stop_button)

        # Progress indicators
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        self.status_label = GlowingLabel(text='Ready to search', size_hint_y=None, height=30)
        self.search_progress = ProgressBar(max=100, size_hint_y=None, height=20)
        self.results_count_label = Label(text='Results: 0', size_hint_y=None, height=30)

        # Results display
        self.result_tabs = TabbedPanel(do_default_tab=False)
        self.file_tab = TabbedPanelItem(text='Files')
        self.content_tab = TabbedPanelItem(text='Content Matches')
        self.file_results = BoxLayout(orientation='vertical', size_hint_y=None)
        self.file_results.bind(minimum_height=self.file_results.setter('height'))  # Use minimum_height
        self.content_results = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_results.bind(minimum_height=self.content_results.setter('height'))  # Use minimum_height

        file_scroll = ScrollView(size_hint=(1, None), size=(400, 300))
        file_scroll.add_widget(self.file_results)
        content_scroll = ScrollView(size_hint=(1, None), size=(400, 300))
        content_scroll.add_widget(self.content_results)

        self.file_tab.add_widget(file_scroll)
        self.content_tab.add_widget(content_scroll)
        self.result_tabs.add_widget(self.file_tab)
        self.result_tabs.add_widget(self.content_tab)

        # Add all elements to the main layout
        self.layout.add_widget(self.search_bar)
        self.layout.add_widget(self.progress_bar)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.search_progress)
        self.layout.add_widget(self.results_count_label)
        self.layout.add_widget(self.result_tabs)

        return self.layout



    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    @mainthread
    def update_results(self, file_results, content_results):
        self.file_results.clear_widgets()
        self.content_results.clear_widgets()


        if file_results:
            for filepath in file_results:
                btn = Button(text=os.path.basename(filepath), size_hint_y=None, height=40)
                btn.bind(on_press=partial(self.open_file, filepath))
                self.file_results.add_widget(btn)
        else:
            self.file_results.add_widget(Label(text='No file name matches found'))


        if content_results:
            for result in content_results:
                # Assuming content_results stores (filepath, description)
                filepath, description = result
                btn = Button(text=f'{description} - {os.path.basename(filepath)}', size_hint_y=None, height=40)
                btn.bind(on_press=partial(self.open_file, filepath))  # Open file on click
                self.content_results.add_widget(btn)
        else:
            self.content_results.add_widget(Label(text='No content matches found'))

        self.status_label.text = 'Search completed' if not self.stop_search_flag.is_set() else "Search stopped"
        self.search_progress.value = 100
        total_results = len(file_results) + len(content_results)
        self.results_count_label.text = f'Results: {total_results}'
        self.show_completion_popup()

    def show_completion_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message = Label(text='Search completed successfully!')
        dismiss_button = Button(text='OK', size_hint=(None, None), size=(100, 50))
        content.add_widget(message)
        content.add_widget(dismiss_button)

        popup = Popup(title='Search Complete', content=content, size_hint=(None, None), size=(300, 200))
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()

    @mainthread 
    def update_progress(self, progress, dt):
        self.progress_bar.value = progress
        self.status_label.text = f'Searching... {progress:.2f}% complete'

    @mainthread
    def update_search_progress(self, progress, dt):
        self.search_progress.value = progress
        self.status_label.text = f'Searching... {progress:.2f}% complete'

    @mainthread
    def update_results_count(self, count, dt):
        self.results_count_label.text = f'Results: {count}'


    def start_search(self, instance):
        search_word = self.search_input.text
        if not search_word:
            return

        if search_word in self.search_cache:  # Check cache first
            file_results, content_results = self.search_cache[search_word]
            self.update_results(file_results, content_results)
            return
        
        # Proceed with a new search if not cached
        self.status_label.text = 'Initializing search...'
        self.progress_bar.value = 0
        self.search_progress.value = 0
        self.results_count_label.text = 'Results: 0'
        self.file_results.clear_widgets()
        self.content_results.clear_widgets()
        self.stop_search_flag.clear()

        self.stop_button.disabled = False
        self.search_button.disabled = True

        self.search_thread = threading.Thread(target=self.search_files, args=(search_word,))
        self.search_thread.start()

    def stop_searching(self, instance):
        self.stop_search_flag.set()
        self.status_label.text = "Search stopped"
        self.stop_button.disabled = True
        self.search_button.disabled = False

    def search_files(self, search_word):
        file_results = []
        content_results = []
        total_files = 0
        processed_files = 0
        total_results = 0

        # Get total file count for progress calculation
        for root, _, files in os.walk('/'):
            total_files += len(files)

        for root, _, files in os.walk('/'):
            if self.stop_search_flag.is_set():
                break

            for filename in files:
                if self.stop_search_flag.is_set():
                    break

                filepath = os.path.join(root, filename)

                # File name matches
                if search_word.lower() in filename.lower():
                    file_results.append(filepath)
                    total_results += 1
                    Clock.schedule_once(partial(self.update_results_count, total_results), 0)

                # File content matches
                if self.search_file_content(filepath, search_word):
                    content_results.append((filepath, f"{os.path.basename(filepath)} (content match)"))  # Store filepath and description
                    total_results += 1
                    Clock.schedule_once(partial(self.update_results_count, total_results), 0)

                processed_files += 1
                progress = (processed_files / total_files) * 100
                Clock.schedule_once(partial(self.update_search_progress, progress), 0)

        self.search_cache[search_word] = (file_results, content_results)  # Cache the results
        self.update_results(file_results, content_results)
        self.stop_button.disabled = True
        self.search_button.disabled = False

    def search_file_content(self, filepath, search_word):
        try:
            if filepath.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if search_word.lower() in content.lower():
                        return True

            elif filepath.endswith('.pdf'):
                with open(filepath, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if search_word.lower() in text.lower():
                            return True

            elif filepath.endswith('.docx'):
                doc = Document(filepath)
                full_text = '\n'.join([para.text for para in doc.paragraphs])
                if search_word.lower() in full_text.lower():
                    return True

            elif filepath.endswith('.xlsx'):
                wb = openpyxl.load_workbook(filepath, read_only=True)
                for sheet in wb.worksheets:
                    for row in sheet.iter_rows():
                        for cell in row:
                            if cell.value and search_word.lower() in str(cell.value).lower():
                                return True

        except Exception as e:
            print(f"Error reading {filepath}: {e}")

        return False

    def open_file(self, filepath, instance):
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # Linux variants
            subprocess.call(('xdg-open', filepath))



if __name__ == '__main__':
    AdvancedFileSearchApp().run()
