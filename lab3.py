import os
import datetime
import pandas as pd
import seaborn as sns
import urllib.request
from spyre import server
import matplotlib.pyplot as plt

############# Функції з лаби 2 ###############

def download_data(province_ID, start_year=1981, end_year=2024):
    # перевіряю, чи існує папка для зберігання
    if not os.path.exists("lab2_VHI"):
        os.makedirs("lab2_VHI")
    
    # перевіряю, чи файл уже завантажений
    filename_pattern = f"VHI-ID_{province_ID}_"
    existing_files = [file for file in os.listdir("lab2_VHI") if file.startswith(filename_pattern)]
    if existing_files:
        print(f"=] Файл для VHI-ID №{province_ID} вже існує: {existing_files[0]}\n")
        return
    
    # скачую
    url_download = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={province_ID}&year1={start_year}&year2={end_year}&type=Mean"
    vhi_url_open = urllib.request.urlopen(url_download)
    
    # створюю назви файлу з датою та часом
    year_month_now = datetime.datetime.now().strftime("%d-%m-%Y")
    h_m_s_time_now = datetime.datetime.now().strftime("%H-%M-%S")
    filename = f"VHI-ID_{province_ID}_{year_month_now}_{h_m_s_time_now}.csv"
    
    file_path = os.path.join("lab2_VHI", filename)
    with open(file_path, 'wb') as output:
        output.write(vhi_url_open.read())

    # виводжу відповідний текст
    print()
    print(f"=] VHI-файл {filename} завантажений успішно!")
    print(f"=] Тека зберігання: {os.path.abspath(file_path)}")
    print()

    return

def dataframer(folder_path):
    fr, columns  = [], ["Year", "Week", "SMN", "SMT", "VCI", "TCI", "VHI", "empty"]

    # отримую список файлів CSV у папці
    csv_files = filter(lambda x: x.endswith('.csv'), os.listdir(folder_path))

    # перебираю файли
    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)
        province_ID = int(file_name.split('_')[1])
        
        # зчитую та обробляю CSV файли
        df = pd.read_csv(file_path, header=1, names=columns) # зчитую файл CSV у df
        df.at[0, "Year"] = df.at[0, "Year"][9:] # виправляю рік у стовпці Year

        df = df.drop(df.index[-1]) # видаляю останній рядокі
        df = df.drop(df.loc[df["VHI"] == -1].index) # видаляю рядки з невизначеним VHI
        df = df.drop("empty", axis=1) # видаляю порожній стовбець

        df.insert(0, "province_ID", province_ID, True) # вставяю стовбець 'province_ID'
        df['Year'] = df['Year'].astype(int) # Year у ціле число.
        df["Week"] = df["Week"].astype(int) # Week у ціле число.

        fr.append(df) # додаю до списку

    # об'єдную дані у фрейм, видаливши дублікати
    df_res = pd.concat(fr).drop_duplicates().reset_index(drop=True)
    # відкидаю області 12 та 20
    df_res = df_res.loc[(df_res.province_ID != 12) & (df_res.province_ID != 20)]

    return df_res

def change_province_id(df):
    # словник між старими і новими індексами областей
    province_mapping = {
        1: 22,
        2: 24,
        3: 23,
        4: 25,
        5: 3,
        6: 4,
        7: 8,
        8: 19,
        9: 20,
        10: 21,
        11: 9,
        13: 10,
        14: 11,
        15: 12,
        16: 13,
        17: 14,
        18: 15,
        19: 16,
        21: 17,
        22: 18,
        23: 6,
        24: 1,
        25: 2,
        26: 7,
        27: 5,
    }
    
    # міняю індекси областей у фреймі
    df_copy = df.copy() # попередньо зробивши копію фрейма міняю
    df_copy['province_ID'] = df_copy['province_ID'].replace(province_mapping)
    
    return df_copy

##############################################

# скачую файли
for index in range(1, 28):
    print(f"!] Завантаження CSV-файлу за VHI-ID №{index}...")
    download_data(index, 1981, 2024)

# для сприйняття замість айді ставлю назви
ids_with_names = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 
    4: 'Донецька', 5: 'Житомирська', 6: 'Закарпатська', 
    7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 
    10: 'Кіровоградська', 11: 'Луганська', 12: 'Львівська', 
    13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 
    19: 'Харківська', 20: 'Херсонська', 21: 'Хмельницька',
    22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}

# клас веб-додатку
class Web_Analyzator(server.App):
    title = "Analyzator LAB3000"

    # інпути
    inputs = [{
        # вибір типу індексів
        "type": 'dropdown',
        "label": 'Select Data',
        "options": [
            {"label": "Vegetation Condition Index (VCI)", "value": "VCI"},
            {"label": "Temperature Condition Index (TCI)", "value": "TCI"},
            {"label": "Vegetation Health Index (VHI)", "value": "VHI"}
        ],
        "key": 'data_type',
        "action_id": "update_data"
    }, {
        # вибір області
        "type": 'dropdown',
        "label": 'Select Province',
        "options": [{"label": f"{ids_with_names[province_id]}", "value": province_id} 
                    for province_id in range(1, 26) if province_id not in [12, 20]],
        "key": 'province_id',
        "action_id": "update_data"
    }, {
        # вибір діапазону років
        "type": 'text',
        "key": 'week_range',
        "label": 'Week Range (e.g., 1-52)',
        "value": '1-52',
        "action_id": 'update_data'
    }, {
        # вибір кольору хітмапи
        "type": 'dropdown',
        "label": 'Select Color Map',
        "options": [
            {"label": "Yellow-Green-Blue", "value": "YlGnBu"},
            {"label": "Red-Blue", "value": "RdBu"},
            {"label": "Green-Blue", "value": "GnBu"},
            {"label": "Purple-Green", "value": "viridis"},
            {"label": "Plasma", "value": "plasma"},
            {"label": "Inferno", "value": "inferno"},
            {"label": "Magma", "value": "magma"},
            {"label": "Cividis", "value": "cividis"},
            {"label": "Coolwarm", "value": "coolwarm"},
            {"label": "Jet", "value": "jet"},
            {"label": "Hot", "value": "hot"},
            {"label": "Spectral", "value": "Spectral"},
            {"label": "Spring", "value": "spring"},
            {"label": "Summer", "value": "summer"},
            {"label": "Autumn", "value": "autumn"},
            {"label": "Winter", "value": "winter"}
        ],
        "key": 'color_map',
        "action_id": "update_data"
    }, {
        # за замовчуванням весь діапазон
        "type": 'text',
        "key": 'year_range',
        "label": 'Year Range',
        "value": 'All',
        "action_id": 'update_data'
    }, {
        # оновити дані
        "type": "simple",
        "label": 'Submit',
        "key": 'submit_button',
        "id": "update_data"
    }]

    # кнопка оновити дані
    controls = [{
        "type": "button",
        "label": "update",
        "id": "update_data"
    }]

    # вкладки
    tabs = ["Table", "Plot"]

    # виводи, які будуть відображатись на сторінці
    outputs = [
        {
            "type": "table",
            "id": "table",
            "tab": "Table",
            "control_id": "update_data"
        },
        {
            "type": "plot",
            "id": "plot",
            "tab": "Plot",
            "control_id": "update_data"
        }
    ]
    # ф-ія для отримання дф та його обробки
    def getData(self, params):
        data_type = params['data_type'] # отримую значення індксів
        province_id = params.get('province_id', None) # отримую значення id області, якщо є, else встановлюємо None
        folder_path = "lab2_VHI"
        
        # створюю датафрейм і міняю айді (лаба2)
        df_old = dataframer(folder_path)
        df = change_province_id(df_old)

        week_range = params['week_range'].split('-') # отримую діапазон тижнів
        
        # в інти
        start_week = int(week_range[0])
        end_week = int(week_range[1])
        
        # залишаю лише рядки з тижнями в заданому діапазоні
        df = df[(df['Week'] >= start_week) & (df['Week'] <= end_week)]
        year_range = params['year_range'] # отримую діапазон років з параметрів
        
        # якщо заданий діапазон
        if year_range.lower() != 'all':
            # розділив на початковий і кінцевий
            year_range = year_range.split('-')
            start_year = int(year_range[0])
            end_year = int(year_range[1])
            df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

        # якщо є id
        if province_id is not None:
            province_id = int(province_id) # в інт
            df = df[df['province_ID'] == province_id]

        return df[['province_ID', 'Year', 'Week', data_type]]
    
    def getPlot(self, params):
        df = self.getData(params) # отримую дф
        data_type = params['data_type'] # отримую індекси
        province_id = int(params['province_id']) # отримую ID області в інт
        province_name = ids_with_names[province_id] # отримую назви області
        year_range = params['year_range'] # отримую діапазон років

        # якщо заданий діапазон
        if year_range.lower() != 'all':
            # розділив на початковий і кінцевий
            year_range = year_range.split('-')
            start_year = int(year_range[0])
            end_year = int(year_range[1])
            year_range = f"{start_year}-{end_year}" # рядок діапазону
        else:
            # якщо all - "All years"
            year_range = "All years"

        # створюю фігуру
        plt.figure(figsize=(10, 15))
        plt.subplot(2, 1, 1) # перший сабплот
        sns.heatmap(df.pivot(index='Year', columns='Week', values=data_type), cmap=params['color_map'],
            cbar_kws={'label': data_type}, linewidths=.7) # хіт мап
        plt.title(f"Heatmap of {data_type} for province [{province_name}]\n{year_range}") # заголовок
        plt.xlabel("Week")  # назва осі X
        plt.ylabel("Year")  # назва осі Y

        plt.subplot(2, 1, 2) # другий сабплот
        # лінійний графік
        for year in df['Year'].unique():
            data_year = df[df['Year'] == year]
            plt.plot(data_year['Week'], data_year[data_type], marker='.', linestyle='-', label=year)

        plt.title(f'Graph {data_type} for province [{province_name}]\n{year_range}') # заголовок
        plt.xlabel('Week')  # назва осі X
        plt.ylabel(data_type)  # назва осі Y
        plt.grid(True)  # врубив сітку графіка
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=9) # легенда графіка
        plt.tight_layout() # авто-вирівнювання та відступи між графіками
        return plt.gcf()
    
app = Web_Analyzator()
app.launch(port=6969)