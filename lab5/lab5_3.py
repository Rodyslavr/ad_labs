import csv
import subprocess
import numpy as np
from scipy import signal
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Plasma256 as palette
from bokeh.models import Button, CheckboxGroup, Select, Slider

# початкові параметри
INIT_AMPLITUDE = 1.0
INIT_FREQUENCY = 1.0
INIT_PHASE = 0.0
INIT_NOISE_MEAN = 0.0
INIT_NOISE_DISPERSION = 0.1
SHOW_NOISE = True
BASE_NOISE = np.random.normal(0, 1, 1000)


# ф-ія і кнопка "Новий шум"
def generate_new_noise():
    global BASE_NOISE
    BASE_NOISE = np.random.normal(0, 1, 1000)
    update(None, None, None)

# ф-ія для генерації гармоніки з шумом
def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_dispersion, show_noise=True):
    t = np.linspace(0, 10, 1000)
    y = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    if show_noise:
        scaled_noise = noise_mean + np.sqrt(noise_dispersion) * BASE_NOISE
        y += scaled_noise

    return t, y

# фільтрація сигналу
def filter_signal(y, filter_type, gaussian_std=2, gaussian_window=5, uniform_window=5, alpha=0.6):
    if filter_type == "gaussian":
        window = signal.windows.gaussian(gaussian_window, std=gaussian_std)
        filtered_y = signal.convolve(y, window / window.sum(), mode='same')
    elif filter_type == "uniform":
        filtered_y = np.convolve(y, np.ones(uniform_window) / uniform_window, mode='same')
    elif filter_type == "exponential":
        filtered_y = exponential_filter(y, alpha=alpha)

    return filtered_y

# експоненційний фільтр
def exponential_filter(y, alpha=0.6):
    filtered_y = np.zeros_like(y)
    filtered_y[0] = y[0]  # Перше значення не фільтруємо
    
    for i in range(1, len(y)):
        filtered_y[i] = alpha * y[i] + (1 - alpha) * filtered_y[i-1]
        
    return filtered_y

# ф-ія для задання стилізованих графіків
def set_plot_properties(plot, title, width, height):
    plot.title.text_font_size = "16pt"
    plot.xaxis.axis_label_text_font_size = "14pt"
    plot.yaxis.axis_label_text_font_size = "14pt"
    plot.xaxis.major_label_text_font_size = "12pt"
    plot.yaxis.major_label_text_font_size = "12pt"
    plot.title.text = title
    plot.width = width
    plot.height = height



# стилі віджетів
slider_styles = {"width": 300, "bar_color": palette[128]}
noise_slider_styles = {"width": 300, "bar_color": palette[200]}
changing_noise_slider_styles = {"width": 300, "bar_color": palette[64]}

# графіки
plot1 = figure(title="Гармоніка з накладеним шумом", x_axis_label='Час (с)', y_axis_label='Амплітуда',
               x_axis_type="linear", y_axis_type="linear", background_fill_color="#F0F0F0")

plot2 = figure(title="Відфільтрована гармоніка", x_axis_label='Час (с)', y_axis_label='Амплітуда',
               x_axis_type="linear", y_axis_type="linear", background_fill_color="#F0F0F0")

set_plot_properties(plot1, "Гармоніка з накладеним шумом", 750, 400)
set_plot_properties(plot2, "Відфільтрована гармоніка", 750, 400)

line1 = plot1.line([], [], line_width=3, line_color=palette[128], line_alpha=0.8,
                   line_cap="round", line_join="round")

line2 = plot2.line([], [], line_width=3, line_color=palette[200], line_alpha=0.8,
                   line_cap="round", line_join="round")

# слайдери
amp_slider = Slider(title="Амплітуда", value=INIT_AMPLITUDE, start=0.1, end=5.0, step=0.1, **slider_styles)
freq_slider = Slider(title="Частота", value=INIT_FREQUENCY, start=0.1, end=5.0, step=0.1, **slider_styles)
phase_slider = Slider(title="Фаза", value=INIT_PHASE, start=-np.pi, end=np.pi, step=0.1, **slider_styles)
noise_mean_slider = Slider(title="Шум (середнє)", value=INIT_NOISE_MEAN, start=-1.0, end=1.0, step=0.1, **noise_slider_styles)
noise_dispersion_slider = Slider(title="Шум (дисперсія)", value=INIT_NOISE_DISPERSION, start=0.01, end=1.0, step=0.01, **noise_slider_styles)
gaussian_window_slider = Slider(title="Gaussian Window", value=5, start=3, end=21, step=2, **changing_noise_slider_styles)
gaussian_std_slider = Slider(title="Gaussian STD", value=2, start=0.1, end=8.0, step=0.1, **changing_noise_slider_styles)
uniform_window_slider = Slider(title="Uniform Window", value=5, start=3, end=21, step=2, **changing_noise_slider_styles)
alpha_slider = Slider(title="Alpha", value=0.6, start=0.1, end=0.9, step=0.1, **changing_noise_slider_styles)

# чекбокс
checkbox_group = CheckboxGroup(labels=["Показати шум"], active=[0], width=200)

# спадне меню
filter_menu = Select(title="Згладжування", value="none", options=["none", "gaussian", "uniform", "exponential"], width=200)

# кнопки
reset_button = Button(label="Reset", button_type="success", width=100)
new_noise_button = Button(label="Новий шум", button_type="warning", width=100)
export_button = Button(label="Експорт даних", button_type="primary", width=100)

# ф-ія оновлення графіків
def update(attr, old, new):
    amplitude = amp_slider.value
    frequency = freq_slider.value
    phase = phase_slider.value
    noise_mean = noise_mean_slider.value
    noise_dispersion = noise_dispersion_slider.value
    show_noise = 0 in checkbox_group.active
    filter_type = filter_menu.value
    gaussian_std = gaussian_std_slider.value
    gaussian_window = int(gaussian_window_slider.value)
    uniform_window = int(uniform_window_slider.value)
    alpha_value = alpha_slider.value

    t, y = harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_dispersion, show_noise)
    line1.data_source.data = {'x': t, 'y': y}
    plot1.title.text = f'Гармоніка з накладеним шумом (A={amplitude:.2f}, f={frequency:.2f}, φ={phase:.2f})'

    if filter_type == "none":
        filtered_y = y  # Без фільтрації, просто копіюємо вхідний сигнал
    else:
        filtered_y = filter_signal(y, filter_type, gaussian_std, gaussian_window, uniform_window, alpha_value)

    line2.data_source.data = {'x': t, 'y': filtered_y}

# ф-ія експорту даних в txt файл
def export_data(filename='data_export_bokeh.csv'):
    time, y = harmonic_with_noise(amp_slider.value, freq_slider.value, phase_slider.value,
                                  noise_mean_slider.value, noise_dispersion_slider.value,
                                  0 in checkbox_group.active)

    amplitude = amp_slider.value
    frequency = freq_slider.value
    phase = phase_slider.value
    noise_mean = noise_mean_slider.value
    noise_dispersion = noise_dispersion_slider.value
    show_noise = int(0 in checkbox_group.active)
    filter_type = filter_menu.value
    gaussian_std = gaussian_std_slider.value
    uniform_window = int(uniform_window_slider.value)
    alpha_value = alpha_slider.value
    gaussian_window = int(gaussian_window_slider.value)

    # Отримання відфільтрованих даних
    filtered_y = filter_signal(y, filter_type, gaussian_std, gaussian_window, uniform_window, alpha_value)

    header = ["Time", "Original Signal", "Filtred Signal", "Amplitude", "Frequency",
              "Phase", "Noise Mean", "Noise Covariance", "Show Noise", "Filter Type",
              "Gaussian STD", "Gasussian Window", "Uniform Window", "Alpha"]
    data = zip(time, y, filtered_y, [amplitude] * len(time), [frequency] * len(time),
               [phase] * len(time), [noise_mean] * len(time), [noise_dispersion] * len(time),
               [show_noise] * len(time), [filter_type] * len(time),
               [gaussian_std] * len(time), [gaussian_window] * len(time),
               [uniform_window] * len(time), [alpha_value] * len(time))

    with open(filename, "w", newline='') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(header)
        writer.writerows(data)
        
# ф-ія reset
def reset():
    amp_slider.value = INIT_AMPLITUDE
    freq_slider.value = INIT_FREQUENCY
    phase_slider.value = INIT_PHASE
    noise_mean_slider.value = INIT_NOISE_MEAN
    noise_dispersion_slider.value = INIT_NOISE_DISPERSION
    filter_menu.value = "none"
    update(None, None, None)

# підключення слайдерів, чекбоксу, спадного меню та кнопок до функцій
amp_slider.on_change('value', update)
freq_slider.on_change('value', update)
phase_slider.on_change('value', update)
noise_mean_slider.on_change('value', update)
noise_dispersion_slider.on_change('value', update)
checkbox_group.on_change('active', update)
filter_menu.on_change('value', update)
export_button.on_click(export_data)
gaussian_std_slider.on_change('value', update)
uniform_window_slider.on_change('value', update)
alpha_slider.on_change('value', update)
gaussian_window_slider.on_change('value', update)
reset_button.on_click(reset)
new_noise_button.on_click(generate_new_noise)

# лейаут
layout = column(
    gridplot([[plot1, plot2]], toolbar_location="above"),
    row(noise_mean_slider, noise_dispersion_slider),
    row(amp_slider, freq_slider, phase_slider),
    row(gaussian_std_slider, gaussian_window_slider, uniform_window_slider, alpha_slider),
    row(new_noise_button, reset_button, export_button, filter_menu, checkbox_group)
)
curdoc().add_root(layout)

# запуск    
if __name__ == "__main__":
    subprocess.run(["bokeh", "serve", "--show", __file__])