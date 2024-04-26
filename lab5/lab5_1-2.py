import os
import csv
import webbrowser
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons, RadioButtons

# початкові параметри
INIT_AMPLITUDE = 1.0
INIT_FREQUENCY = 1.0
INIT_PHASE = 0.0
INIT_NOISE_MEAN = 0.0
INIT_NOISE_DISPERSION = 0.1
SHOW_NOISE = True
BASE_NOISE = np.random.normal(0, 1, 1000)

# ф-ія для створення нового шуму
def generate_new_noise(event):
    global BASE_NOISE
    BASE_NOISE = np.random.normal(0, 1, 1000)
    update(None)

# ф-ія для генерації гармоніки з шумом
def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, SHOW_NOISE=True):
    t = np.linspace(0, 10, 1000)
    y = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    if SHOW_NOISE:
        scaled_noise = noise_mean + np.sqrt(noise_covariance) * BASE_NOISE
        y += scaled_noise

    return t, y

# фільтрація сигналу
def filter_signal(y, filter_type='None', sigma=None, window_size=None):
    if filter_type == 'None':
        filtered_y = y
    elif filter_type == 'Gaussian':
        window = signal.windows.gaussian(window_size, std=sigma)
        filtered_y = signal.convolve(y, window / window.sum(), mode='same')
    elif filter_type == 'Uniform':
        window = np.ones(window_size) / window_size
        filtered_y = signal.convolve(y, window, mode='same')
    return filtered_y

# нове вікно
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1.5, 1.5]})
plt.subplots_adjust(bottom=0.6, hspace=0.9)

# базові графіки
t, y = harmonic_with_noise(INIT_AMPLITUDE, INIT_FREQUENCY, INIT_PHASE, INIT_NOISE_MEAN, INIT_NOISE_DISPERSION, SHOW_NOISE)
filtered_y = filter_signal(y, 'None')

line1, = ax1.plot(t, y, lw=2, color='b', label='Оригінальний сигнал')
line2, = ax2.plot(t, filtered_y, lw=2, color='g', label='Відфільтрований сигнал')

ax1.set_xlabel('Час (с)')
ax1.set_ylabel('Амплітуда')
ax1.set_title('Гармоніка з накладеним шумом')

ax2.set_xlabel('Час (с)')
ax2.set_ylabel('Амплітуда')
ax2.set_title('Відфільтрована гармоніка')

# ф-ія для відображення обох графіків в одному вікні
def plot_signals(t, y, filtered_y):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1]})
    plt.subplots_adjust(hspace=0.5)

    ax1.plot(t, y, 'b-', label='Оригінальний сигнал')
    ax1.set_xlabel('Час (с)')
    ax1.set_ylabel('Амплітуда')
    ax1.set_title('Гармоніка з накладеним шумом')
    ax1.legend()

    ax2.plot(t, filtered_y, 'g-', label='Відфільтрований сигнал')
    ax2.set_xlabel('Час (с)')
    ax2.set_ylabel('Амплітуда')
    ax2.set_title('Відфільтрована гармоніка')
    ax2.legend()

    plt.show()

# ф-ія для експорту даних у csv-файл
def export_data(filename='data_export_matplotib.csv'):
    global t, y, filtered_y
    t, y = harmonic_with_noise(amp_slider.val, freq_slider.val, phase_slider.val, noise_mean_slider.val, 
                               noise_covariance_slider.val, checkbox.get_status()[0])
    filtered_y = filter_signal(y, filter_type_buttons.value_selected, sigma_slider.val, window_size_slider.val)

    amplitude = amp_slider.val
    frequency = freq_slider.val
    phase = phase_slider.val
    noise_mean = noise_mean_slider.val
    noise_covariance = noise_covariance_slider.val
    show_noise = int(checkbox.get_status()[0])
    filter_type = filter_type_buttons.value_selected
    sigma = sigma_slider.val
    window_size = int(window_size_slider.val)

    header = ["Time", "Original Signal", "Filtered Signal", "Amplitude",
              "Frequency", "Phase", "Noise Mean", "Noise Covariance",
              "Show Noise", "Filter Type", "Gaussian STD", "Window Size"]
    data = np.column_stack((t, y, filtered_y, [amplitude] * len(t), [frequency] * len(t), [phase] * len(t), 
                            [noise_mean] * len(t), [noise_covariance] * len(t), 
                            [show_noise] * len(t), [filter_type] * len(t), 
                            [sigma] * len(t), [window_size] * len(t)))

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

    print(f'Результати успішно збережено у файл: {os.path.abspath(filename)}')

# ф-ія для експорту графіків у PDF
def export_to_pdf(filename='plot.pdf'):
    plt.figure(figsize=(10, 8))
    plt.subplot(2, 1, 1)
    plt.plot(t, y, lw=2, color='b', label='Оригінальний сигнал')
    plt.title('Гармоніка з накладеним шумом')
    plt.xlabel('Час (с)')
    plt.ylabel('Амплітуда')

    plt.subplot(2, 1, 2)
    plt.plot(t, filtered_y, lw=2, color='g', label='Відфільтрований сигнал')
    plt.title('Відфільтрована гармоніка')
    plt.xlabel('Час (с)')
    plt.ylabel('Амплітуда')
    plt.tight_layout()

    plt.savefig(filename, format='pdf')
    print(f'Графіки збережено у PDF: {os.path.abspath(filename)}')
    webbrowser.open(os.path.abspath(filename))

# слайдери
ax_phase = plt.axes([0.25, 0.5, 0.65, 0.03])
phase_slider = Slider(ax_phase, 'Фаза', -np.pi, np.pi, valinit=INIT_PHASE, valstep=0.1)

ax_frequency = plt.axes([0.25, 0.45, 0.65, 0.03])
freq_slider = Slider(ax_frequency, 'Частота', 0.1, 5.0, valinit=INIT_FREQUENCY, valstep=0.005)

ax_amplitude = plt.axes([0.25, 0.4, 0.65, 0.03])
amp_slider = Slider(ax_amplitude, 'Амплітуда', 0.1, 5.0, valinit=INIT_AMPLITUDE, valstep=0.05)

ax_noise_mean = plt.axes([0.25, 0.35, 0.65, 0.03])
noise_mean_slider = Slider(ax_noise_mean, 'Шум (середнє)', -1.0, 1.0, valinit=INIT_NOISE_MEAN, valstep=0.01)

ax_noise_covariance = plt.axes([0.25, 0.3, 0.65, 0.03])
noise_covariance_slider = Slider(ax_noise_covariance, 'Шум (дисперсія)', 0.01, 1.0, valinit=INIT_NOISE_DISPERSION, valstep=0.01)

ax_sigma = plt.axes([0.25, 0.25, 0.65, 0.03])
sigma_slider = Slider(ax_sigma, 'Sigma', 0.1, 8, valinit=2.0, valstep=0.05)

ax_window_size = plt.axes([0.25, 0.2, 0.65, 0.03])
window_size_slider = Slider(ax_window_size, 'Window Size', 3, 21, valinit=5, valstep=2)

# чекбокс
ax_checkbox = plt.axes([0.1, 0.9, 0.2, 0.1])
checkbox = CheckButtons(ax_checkbox, ['Показати шум'], [SHOW_NOISE])

# вибір типу фільтра
ax_filter_type = plt.axes([0.3, 0.07, 0.4, 0.1])
filter_type_buttons = RadioButtons(ax_filter_type, ['None', 'Gaussian', 'Uniform'], active=0)

# кнопки ("Reset", "Новий шум", "Зберегти (CSV), "Зберегти (PDF)")
reset_button_ax = plt.axes([0.3, 0.01, 0.1, 0.04])
reset_button = Button(reset_button_ax, 'Reset')

ax_new_noise_button = plt.axes([0.4, 0.01, 0.1, 0.04])
new_noise_button = Button(ax_new_noise_button, 'Новий шум')

ax_save_button = plt.axes([0.5, 0.01, 0.1, 0.04])
save_button = Button(ax_save_button, 'Зберегти (CSV)')

ax_export_button = plt.axes([0.6, 0.01, 0.1, 0.04])
export_button = Button(ax_export_button, 'Зберегти (PDF)')

# ф-ія оновлення графіка
def update(val):
    amplitude = amp_slider.val
    frequency = freq_slider.val
    phase = phase_slider.val
    noise_mean = noise_mean_slider.val
    noise_covariance = noise_covariance_slider.val
    show_noise = checkbox.get_status()[0]
    filter_type = filter_type_buttons.value_selected

    sigma = sigma_slider.val if filter_type == 'Gaussian' else None
    window_size = int(window_size_slider.val) if filter_type in ['Gaussian', 'Uniform'] else None

    t, y = harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise)
    filtered_y = filter_signal(y, filter_type, sigma, window_size)

    line1.set_data(t, y)
    line2.set_data(t, filtered_y)

    ax1.set_title(f'Гармоніка з накладеним шумом (A={amplitude:.2f}, f={frequency:.2f}, φ={phase:.2f})')

    if filter_type == 'None':
        ax2.set_title('Відфільтрована гармоніка (без фільтрації)')
    else:
        ax2.set_title(f'Відфільтрована гармоніка (тип={filter_type})')
    fig.canvas.draw_idle()

# ф-ія reset
def reset(event):
    amp_slider.reset()
    freq_slider.reset()
    phase_slider.reset()
    noise_mean_slider.reset()
    noise_covariance_slider.reset()
    filter_type_buttons.set_active(0)
    sigma_slider.reset()
    window_size_slider.reset()
    update(None)

# ф-ія-івент зберегти дані
def save_signal(event):
    export_data()

# ф-ія=івент зберегти pdf
def export_plot(event):
    export_to_pdf()

# слайдери/кнопоки до ф-ій update, reset, save_signal та export_plot
amp_slider.on_changed(update)
freq_slider.on_changed(update)
phase_slider.on_changed(update)
noise_mean_slider.on_changed(update)
noise_covariance_slider.on_changed(update)
checkbox.on_clicked(update)
filter_type_buttons.on_clicked(update)
sigma_slider.on_changed(update)
window_size_slider.on_changed(update)
new_noise_button.on_clicked(generate_new_noise)
reset_button.on_clicked(reset)
save_button.on_clicked(save_signal)
export_button.on_clicked(export_plot)

plt.show()