from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
import math
from math import fabs
import requests
import json

# Global variables
url = 'http://185.18.54.154:8000/myapp/receive_tab_rec/'
player_name = "Alex"
g = float(1.62)
M = float(2250)
m_start_fuel = [float(1000)]
m = m_start_fuel
C = float(3660)
_s0 = 250000
q = float(0)
h = [float(0.0000001)]
h_min = float(0.00000001)
V_h = [float(0)]
x = [float(0)]
u = [float(0)]
a = float(0)
a_max = float(3 * 9.81)
al = float(0)
dm = float(0)
t = float(0)
i = int(0)
t_f = [float(0)]
file_background = '111.jpg'
file_background2 = '222.jpg'
#Submit_button_text = 'ok'
# Data storage for the tabs
data_history = []
input_history = []

def send_post_request():
    global V_h, x, u, i, m, _s0

    data = {
        'name': player_name,
        's': fabs(x[i-1]-_s0),
        'u': u[i-1],
        'v': V_h[i-1],
        'm': m[i-1]
    }

    json_data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json_data, headers=headers)

    # Check response
    if response.status_code == 200:
        table = response.json().get('table', [])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def q_a():
    global q, dm, t, C, M, m, a
    q = dm / t
    a = q * C / (M + m[i])

def correct_bl():
    global i, t_f, t, V_h, x, u, h, m
    main_bl()
    t_f.append(t_f[i] + t)
    i += 1
    main_bl()
    V_h[i - 1] = V_h[i]
    x[i - 1] = x[i]
    u[i - 1] = u[i]
    h[i - 1] = h[i]
    m[i - 1] = m[i]
    t_f[i - 1] = t_f[i]

    del V_h[i:]
    del m[i:]
    del h[i:]
    del x[i:]
    del u[i:]
    del t_f[i:]

def main_bl():
    global V_h, a, t, al, x, u, g, h, i, a_max, q, dm, m
    V_h.append(V_h[i] + a * t * math.sin(al))
    x.append(x[i] + (V_h[i] + V_h[i + 1]) / 2 * t)
    u.append(u[i] + (a * math.cos(al) - g) * t)
    h.append(h[i] + (u[i + 1] + u[i]) / 2 * t)
    m.append(m[i] - q * t)

    if a > a_max:
        t_f.append(t_f[i] + t)
        input_history.append({
            "dm": dm,
            "t": t,
            "al": al / math.pi * 180
        })

        i += 1
        dm = 0
        t = a - a_max
        data_history.append({
            "i": i,
            "h": h[i],
            "x": x[i],
            "u": u[i],
            "V_h": V_h[i],
            "t_f": t_f[i]
        })
        # Replace the print statement with a popup
        SimulationApp.get_running_app().show_a_max_popup(a, t)
        q_a()
        main_bl()

class BorderedLabel(Label):
    """Custom Label with a border."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Set border color
            Color(0, 0, 0, 1)  # Black border
            self.border = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, *args):
        """Update the border when the label's position or size changes."""
        self.border.pos = self.pos
        self.border.size = self.size
        self.font_size = 32

class TabbedTextInput(TextInput):
    def __init__(self, next_input=None, **kwargs):
        super().__init__(**kwargs)
        self.next_input = next_input
        self.multiline = False  # Ensure single-line input
        self.size_hint_y = None
        self.height = 50  # Set height to fit one line
        self.font_size = 32  # Adjust font size for better readability

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # Handle Tab key press
        if keycode[1] == 'tab':
            if self.next_input:
                self.next_input.focus = True
            return True  # Prevent default behavior
        return super().keyboard_on_key_down(window, keycode, text, modifiers)

class SimulationApp(App):
    def on_start(self):
        # Show name prompt when app starts
        self.show_name_prompt()

    def show_name_prompt(self):
        global player_name

        # Create a popup layout
        popup_layout = BoxLayout(orientation='vertical', padding=40, spacing=10)
        # Add a label and text input for the name
        popup_layout.add_widget(Label(text="Введите имя игрока:"))
        name_input = TextInput(text=player_name, multiline=False, size_hint=(1, None), height=60)
        popup_layout.add_widget(name_input)

        # Add a submit button
        submit_button = Button(text="OK", size_hint=(1, None), height=40)
        popup_layout.add_widget(submit_button)

        # Create the popup
        popup = Popup(title="",
                      content=popup_layout,
                      size_hint=(0.8, 0.4))

        def set_name(instance):
            global player_name
            name = name_input.text.strip()
            if name:  # Only set if name is not empty
                player_name = name
            popup.dismiss()

        submit_button.bind(on_press=set_name)
        popup.open()

    def build(self):
        global i
        self.tabs = TabbedPanel(do_default_tab=False, size_hint=(1, 1))

        # First Tab: Input and Results
        self.input_tab = TabbedPanelItem(text="Ввод", font_size=24)
        self.input_layout = RelativeLayout()  # Use RelativeLayout for overlaying widgets

        # Add background image (fills the entire screen)
        self.background = Image(source=file_background, allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
        self.input_layout.add_widget(self.background)
        # Input fields
        self.dm_input = TabbedTextInput(hint_text="Введите dm", multiline=False, size_hint=(0.2, None), height=30,
                                       pos_hint={'x': 0.1, 'top': 0.9})
        self.t_input = TabbedTextInput(hint_text="Введите t", multiline=False, size_hint=(0.2, None), height=30,
                                      pos_hint={'x': 0.4, 'top': 0.9})
        self.al_input = TabbedTextInput(hint_text="Введите al", multiline=False, size_hint=(0.2, None), height=30,
                                       pos_hint={'x': 0.7, 'top': 0.9})

        # Set up tab order
        self.dm_input.next_input = self.t_input
        self.t_input.next_input = self.al_input
        self.al_input.next_input = self.dm_input  # Loop back to the first input

        # Set default values for the first step
        self.dm_input.text = "100"
        self.t_input.text = "3.9"
        self.al_input.text = "42.7"

        # Submit button
        Submit_button_text = "Старт"
        self.submit_button = Button(text=Submit_button_text, size_hint=(0.2, 0.1), pos_hint={'x': 0.4, 'top': 0.8},
                                    font_size=32)
        self.submit_button.bind(on_press=self.process_input)

        # Result label
        self.result_label = Label(text="Тут будут результаты", size_hint=(0.8, 0.4),
                                 pos_hint={'x': 0.1, 'top': 0.7}, font_size=32)

        # Add widgets to input layout (on top of the background image)
        self.input_layout.add_widget(self.dm_input)
        self.input_layout.add_widget(self.t_input)
        self.input_layout.add_widget(self.al_input)
        self.input_layout.add_widget(self.submit_button)
        self.input_layout.add_widget(self.result_label)

        self.input_tab.add_widget(self.input_layout)

        # Second Tab: Input History
        self.input_history_tab = TabbedPanelItem(text="Ист. ввода", font_size=24)
        self.input_history_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Add column headers
        self.input_column_headers = GridLayout(cols=3, size_hint_y=None, height=40, spacing=20)
        headers = ["dm", "t", "al"]
        for header in headers:
            header_label = BorderedLabel(text=header, size_hint_x=None, width=150, bold=True)
            self.input_column_headers.add_widget(header_label)

        # Scrollable input history display
        self.input_history_scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)
        self.input_history_table = GridLayout(
            cols=3,
            size_hint_x=None,
            size_hint_y=None,
            spacing=20,
            row_default_height=50,  # Increase row height
            row_force_default=True,  # Force row height
        )
        self.input_history_table.bind(minimum_width=self.input_history_table.setter('width'))
        self.input_history_table.bind(minimum_height=self.input_history_table.setter('height'))
        self.input_history_scroll.add_widget(self.input_history_table)

        # Add widgets to input history layout
        self.input_history_layout.add_widget(self.input_column_headers)
        self.input_history_layout.add_widget(self.input_history_scroll)

        self.input_history_tab.add_widget(self.input_history_layout)

        # Third Tab: History
        self.history_tab = TabbedPanelItem(text="История", font_size=24)
        self.history_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Add column headers
        self.column_headers = GridLayout(cols=6, size_hint_y=None, height=40, spacing=20)
        headers = ["i", "h", "x", "u", "V_h", "t_f"]
        for header in headers:
            header_label = BorderedLabel(text=header, size_hint_x=None, width=150, bold=True)
            self.column_headers.add_widget(header_label)

        # Scrollable history display
        self.history_scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)
        self.history_table = GridLayout(
            cols=6,
            size_hint_x=None,
            size_hint_y=None,
            spacing=20,
            row_default_height=50,  # Increase row height
            row_force_default=True,  # Force row height
        )
        self.history_table.bind(minimum_width=self.history_table.setter('width'))
        self.history_table.bind(minimum_height=self.history_table.setter('height'))
        self.history_scroll.add_widget(self.history_table)

        # Add widgets to history layout
        self.history_layout.add_widget(self.column_headers)
        self.history_layout.add_widget(self.history_scroll)

        self.history_tab.add_widget(self.history_layout)

        # Fourth Tab: Highscore Table
        self.highscore_tab = TabbedPanelItem(text="Табл.рек.", font_size=24)
        self.highscore_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Add column headers
        self.highscore_column_headers = GridLayout(cols=5, size_hint_y=None, height=40, spacing=20)
        headers = ["Имя", "Отклон.", "Ск.верт.", "Ск.гориз","Ост.топл"]
        for header in headers:
            header_label = BorderedLabel(text=header, size_hint_x=None, width=150, bold=True)
            self.highscore_column_headers.add_widget(header_label)

        # Scrollable highscore display
        self.highscore_scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)
        self.highscore_table = GridLayout(
            cols=5,
            size_hint_x=None,
            size_hint_y=None,
            spacing=20,
            row_default_height=50,  # Increase row height
            row_force_default=True,  # Force row height
        )
        self.highscore_table.bind(minimum_width=self.highscore_table.setter('width'))
        self.highscore_table.bind(minimum_height=self.highscore_table.setter('height'))
        self.highscore_scroll.add_widget(self.highscore_table)

        # Add widgets to highscore layout
        self.highscore_layout.add_widget(self.highscore_column_headers)
        self.highscore_layout.add_widget(self.highscore_scroll)

        self.update_button = Button(text="Обновить", size_hint=(1, 0.1))
        self.update_button.bind(on_press=lambda instance: self.fetch_highscore_data())
        self.highscore_layout.add_widget(self.update_button)

        self.highscore_tab.add_widget(self.highscore_layout)

        # Fifth Tab: Text with Background
        self.text_tab = TabbedPanelItem(text="О программе", font_size=24)
        self.text_layout = RelativeLayout()

        # Add background image
        self.text_background = Image(source=file_background2, allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
        self.text_layout.add_widget(self.text_background)

        # Add 15 lines of text
        self.text_lines = BoxLayout(orientation='vertical', padding=10, spacing=10)


        line_label = Label(text=f"Для управления лунолетом введите кол-во топлива, \n"
                                f"время маневра, угол отклонения от вертикали в градусах.\n "
                                f"Ваша цель - пролететь 250 000м, используя 1000кг топлива \n"
                                f"Ограничения: \n"
                                f"1.Кол-во топлива не должно превышать 5% от общей \n"
                                f"массы (2250+1000 на момент старта)\n"
                                f"2.Допустимое ускорение - не более 3g, при превышении \n"
                                f"считается, что пилот потерял сознание, корабль выкл. \n"
                                f"двигатель на время пропорциональное превышению \n"
                                f"3.Для работы вкладки <<Таблица рекордов>> необходим \n"
                                f"доступ к интернет."
                                f"\n"
                                f"\n"
                                f"\n", size_hint_y=1, height=30, font_size=32)
        self.text_lines.add_widget(line_label)
        self.text_layout.add_widget(self.text_lines)
        self.text_tab.add_widget(self.text_layout)

        # Add tabs to the main panel
        self.tabs.add_widget(self.input_tab)
        self.tabs.add_widget(self.input_history_tab)
        self.tabs.add_widget(self.history_tab)
        self.tabs.add_widget(self.highscore_tab)
        self.tabs.add_widget(self.text_tab)

        # Fetch and display highscore data
        self.fetch_highscore_data()

        return self.tabs

    def fetch_highscore_data(self):
        """Fetch highscore data from the Django server and update the highscore tab."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                table = response.json().get('table', [])
                # Sort by value1 (descending order)
                table.sort(key=lambda x: x['s'], reverse=False)

                # Clear existing highscore content
                self.highscore_table.clear_widgets()

                # Add new highscore entries
                for entry in table:
                    values = [
                        entry['name'],
                        str(round(entry['s'],2)),
                        str(round(entry['u'],2)),
                        str(round(entry['v'],2)),
                        str(round(entry['m'],2))
                    ]
                    for value in values:
                        value_label = BorderedLabel(text=value, size_hint_x=None, width=150)
                        self.highscore_table.add_widget(value_label)
            else:
                self.show_popup("Error", f"Ошибка обращения к серверу: {response.status_code}  ")
                #print(f"Error fetching highscore data: {response.status_code}")
        except Exception as e:
            self.show_popup("Error", f"Ошибка обращения к серверу  ")
            #print(f"Error fetching highscore data: {str(e)}")

    def process_input(self, instance):
        global dm, t, al, i, m

        try:
            dm = float(self.dm_input.text)
            t = float(self.t_input.text)
            al = float(self.al_input.text)
            al = math.pi / 180 * al  # Convert degrees to radians

            # Check if dm is greater than the current mass
            if dm > m[i]:
                t = t * m[i] / dm
                dm = m[i]

            if dm < 0.05 * (M + m[i]) and t != 0:
                q_a()
                main_bl()
                t_f.append(t_f[i] + t)
                i += 1

                # Store data for history
                data_history.append({
                    "i": i,
                    "h": h[i],
                    "x": x[i],
                    "u": u[i],
                    "V_h": V_h[i],
                    "t_f": t_f[i]
                })
                input_history.append({
                    "dm": dm,
                    "t": t,
                    "al": al / math.pi * 180
                })
                if ((h[i] < 0) and (abs(h[i]) > h_min)):
                    t = 2 * h[i] / (math.sqrt(u[i] ** 2 + 2 * h[i] * (g - a * math.cos(al))) - u[i])
                    correct_bl()
                    # Show the results dialog
                    self.show_results_dialog()
                    i -= 1
                elif abs(h[i]) < h_min:
                    h[i] = 0
                # Display results
                result_text = (
                    f"\n h: {round(h[i], 2)},          x: {round(x[i], 2)}\n"
                    f"u: {round(u[i], 2)},          V_h: {round(V_h[i], 2)}\n\n"
                    f"Сек.расход не более:   {str(round(a_max * (M + m[i]) / C, 2))}, "
                    f"Время:     {str(round(100 / (a_max * (M + m[i]) / C), 2))}\n"
                    f"Остаток топл.:     {round(m[i], 2)},    a: {round(a, 2)}\n"
                    f"Общее время:       {round(t_f[i], 2)}\n"
                )
                self.result_label.text = result_text

                # Update input fields with values from the previous step
                self.dm_input.text = str(dm)
                self.t_input.text = str(round(t, 2))
                self.al_input.text = str(round(al * 180 / math.pi, 2))  # Convert radians back to degrees

                # Update history tabs
                self.update_history_tabs()

            else:
                self.show_popup("Error", "dm должно быть менее 5% общей массы.")

        except ValueError:
            self.show_popup("Error", "Введите корректные dm, t, al.")

    def update_history_tabs(self):
        # Clear existing history content
        self.history_table.clear_widgets()
        self.input_history_table.clear_widgets()

        # Add new history entries to the Input History tab
        for entry in input_history:
            values = [
                f"{entry['dm']:.2f}",
                f"{entry['t']:.2f}",
                f"{entry['al']:.1f}"
            ]
            for value in values:
                value_label = BorderedLabel(text=value, size_hint_x=None, width=150)
                self.input_history_table.add_widget(value_label)

        # Add new history entries to the История tab
        for entry in data_history:
            values = [
                str(entry["i"]),
                f"{entry['h']:.2f}",
                f"{entry['x']:.2f}",
                f"{entry['u']:.2f}",
                f"{entry['V_h']:.2f}",
                f"{entry['t_f']:.2f}"
            ]
            for value in values:
                value_label = BorderedLabel(text=value, size_hint_x=None, width=150)
                self.history_table.add_widget(value_label)

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=0)
        popup_label = Label(text=message)
        popup_button = Button(text="OK", size_hint=(1, 0.2))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_a_max_popup(self, a, t):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=0)
        popup_label = Label(text=f"a > a_max\n a: {a:.2f}\n t: {t:.2f}")
        popup_button = Button(text="OK", size_hint=(1, 0.2))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)

        popup = Popup(title="Внимание!", content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_results_dialog(self):
        """Display the results in a dialog box with Finish and Repeat buttons."""

        send_post_request()
        dialog_layout = BoxLayout(orientation='vertical', padding=20, spacing=0)
        scroll_view = ScrollView(do_scroll_x=True, do_scroll_y=True)
        grid_layout = GridLayout(cols=6, size_hint_y=1, spacing=0)

        # Add headers
        headers = ["h", "x", "u", "V_h", "t_f", "m"]
        for header in headers:
            header_label = BorderedLabel(text=header, size_hint_x=None, width=120, bold=True)
            grid_layout.add_widget(header_label)

        # Add data rows
        i_max = len(V_h)
        for i in range(0, i_max):
            values = [
                f"{round(h[i], 2)}",
                f"{round(x[i], 2)}",
                f"{round(u[i], 2)}",
                f"{round(V_h[i], 2)}",
                f"{round(t_f[i], 2)}",
                f"{round(m[i], 2)}"
            ]
            for value in values:
                value_label = BorderedLabel(text=value, size_hint_x=None, width=120)
                grid_layout.add_widget(value_label)

        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        scroll_view.add_widget(grid_layout)
        dialog_layout.add_widget(scroll_view)

        # Add buttons
        button_layout = BoxLayout(size_hint=(0.725, 0.2), spacing=0)
        finish_button = Button(text="Завершить")
        repeat_button = Button(text="Повторить")
        button_layout.add_widget(finish_button)
        button_layout.add_widget(repeat_button)
        dialog_layout.add_widget(button_layout)

        # Create the dialog
        dialog = Popup(title="Результаты", content=dialog_layout, size_hint=(0.9, 0.9))

        # Bind button actions
        finish_button.bind(on_press=lambda x: App.get_running_app().stop())  # Exit the program
        repeat_button.bind(on_press=lambda x: self.reset_program(dialog))  # Reset and close dialog

        dialog.open()

    def reset_program(self, dialog):
        """Reset the program and close the dialog."""
        global i, dm, t, al, h, V_h, x, u, m, t_f, data_history, input_history
        i = 0
        dm = 0
        t = 0
        al = 0
        h = [float(0.0000001)]
        V_h = [float(0)]
        x = [float(0)]
        u = [float(0)]
        m = m_start_fuel
        t_f = [float(0)]
        data_history = []
        input_history = []

        # Clear input fields
        self.dm_input.text = "100"
        self.t_input.text = "3.9"
        self.al_input.text = "42.7"

        # Clear result label
        self.result_label.text = "Тут будут результаты"

        # Close the dialog
        dialog.dismiss()


if __name__ == '__main__':
    SimulationApp().run()