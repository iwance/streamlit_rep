import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO


st.title("Вывод информации для Юнит ВБ")


def upload_file():
    # Выбор типа файла
    file_type = st.radio("Выберите тип файла", ('Excel', 'CSV'))

    if file_type == 'Excel':
        uploaded_file = st.file_uploader("Загрузите Excel файл", type=["xlsx"])
    
    elif file_type == 'CSV':
        delimiter = st.radio("Выберите разделитель для CSV", (';', ','))
        uploaded_file = st.file_uploader("Загрузите CSV файл", type=["csv"])

    return uploaded_file
#uploaded_file = st.file_uploader("Загрузите файл", type='xlsx')

uploaded_file = upload_file()

if uploaded_file is not None:
    
    dfs = pd.read_excel(uploaded_file, sheet_name=None)
    
    #st.write(list(dfs.keys()))
    
    df_y = dfs['ЯМ КОМИССИЯ']
    df_oz = dfs['ОЗОН КОМИССИЯ']
    df_seb = dfs['Себестоимость']
    df_data = dfs['Лист с данными']
    df_wb = dfs['ВБ КОМИССИЯ']
    
    df_seb = df_seb.iloc[1:]
    
if len(df_data) == 5:
    value_chp_wb = df_data.iloc[0, 1]
    value_chp_oz = df_data.iloc[0, 3]
    value_chp_y = df_data.iloc[0, 5]
    
    model_wb = df_data.iloc[1, 1]
    tax_wb = df_data.iloc[2, 1]
    bud_wb = df_data.iloc[3, 1]
    
    model_oz = df_data.iloc[1, 3]
    tax_oz= df_data.iloc[2, 3]
    bud_oz = df_data.iloc[3, 3]
    count_oz = df_data.iloc[4, 3]
    
    model_y = df_data.iloc[1, 5]
    tax_y = df_data.iloc[2, 5]
    bud_y = df_data.iloc[3, 5]

elif len(df_data) == 7:
    value_chp_wb = df_data.iloc[2, 1]
    value_chp_oz = df_data.iloc[2, 3]
    value_chp_y = df_data.iloc[2, 5]
    
    model_wb = df_data.iloc[3, 1]
    tax_wb = df_data.iloc[4, 1]
    bud_wb = df_data.iloc[5, 1]
    
    model_oz = df_data.iloc[3, 3]
    tax_oz= df_data.iloc[4, 3]
    bud_oz = df_data.iloc[5, 3]
    count_oz = df_data.iloc[6, 3]
    
    model_y = df_data.iloc[3, 5]
    tax_y = df_data.iloc[4, 5]
    bud_y = df_data.iloc[5, 5]
    where_y = df_data.iloc[6, 5]

    
    df_unit_wb = df_seb[['Артикул продавца', 'Наименование товара', 'Категория вб', 'Длина', 'Ширина', 'Высота', 'С/С']]
    df_unit_wb = df_unit_wb.assign(Объем_л=(df_unit_wb['Длина'] * df_unit_wb['Ширина'] * df_unit_wb['Высота']) / 1000)
    
    df_unit_wb = pd.merge(df_unit_wb, df_wb, left_on='Категория вб', right_on='Предмет', how='left')
    
    if model_wb == 'FBO':
        df_unit_wb['ИТОГО Логистика'] = ((df_unit_wb['Объем_л'] - 1 ) * 8 + 33)  
        df_unit_wb['Базовая стоимость'] =  (df_unit_wb['ИТОГО Логистика'] + df_unit_wb['С/С'] ) / (1 - value_chp_wb - df_unit_wb['Склад WB, %'] / 100 - tax_wb - bud_wb)
        df_unit_wb['ИТОГО Комиссия'] = df_unit_wb['Склад WB, %'] * df_unit_wb['Базовая стоимость'] / 100
        
    elif model_wb == 'FBS':
        df_unit_wb['ИТОГО Логистика'] = ((df_unit_wb['Объем_л'] - 1 ) * 8 + 33) 
        df_unit_wb['Базовая стоимость'] =  (df_unit_wb['ИТОГО Логистика'] + df_unit_wb['С/С'] ) / (1 - value_chp_wb - df_unit_wb['Склад продавца - везу на склад WB, %'] / 100  - tax_wb - bud_wb)
        df_unit_wb['ИТОГО Комиссия'] = df_unit_wb['Склад продавца - везу на склад WB, %'] * df_unit_wb['Базовая стоимость'] / 100
    
    df_unit_wb['Налог'] = tax_wb * df_unit_wb['Базовая стоимость']
    df_unit_wb['Маркетинг'] = bud_wb * df_unit_wb['Базовая стоимость']
    df_unit_wb['Прибыль минус расходы с 1шт'] = df_unit_wb['Базовая стоимость'] - df_unit_wb['С/С'] \
                                                - df_unit_wb['ИТОГО Комиссия'] - df_unit_wb['ИТОГО Логистика'] \
                                                - df_unit_wb['Налог'] -  df_unit_wb['Маркетинг']
    
    df_unit_wb['Маржа'] = df_unit_wb['Прибыль минус расходы с 1шт'] / df_unit_wb['Базовая стоимость']

    st.title('Юнит ВБ')
    
    st.dataframe(df_unit_wb)
    
    csv = df_unit_wb.to_csv(index=False).encode('utf-8')
    
    # Кнопка скачивания
    st.download_button(
        label="Скачать результат в CSV",
        data=csv,
        file_name='unit_wb_result.csv',
        mime='text/csv'
    )


    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_unit_wb.to_excel(writer, index=False)
    
    # Получаем данные Excel файла
    excel_data = output.getvalue()
    
    # Кнопка скачивания
    st.download_button(
        label="Скачать результат в Excel",
        data=excel_data,
        file_name='unit_wb_result.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )










    
    st.title('Теперь с Озон')
    
    df_unit_oz = df_seb[['Артикул продавца', 'Наименование товара', 'Категория озон', 'Длина', 'Ширина', 'Высота', 'С/С']]
    
    df_unit_oz = df_unit_oz.assign(Объем_л=(df_unit_oz['Длина'] * df_unit_oz['Ширина'] * df_unit_oz['Высота']) / 1000)

    df_unit_oz = pd.merge(df_unit_oz, df_oz[['Категория товаров', 'Вознаграждение на FBS', 'Вознаграждение на FBO']], left_on='Категория озон', right_on='Категория товаров', how='left')
    
    df_unit_oz['Оплата за отправление FBS'] = df_oz[df_oz['Количество отправлений'] == count_oz]['Тариф за отправление'].item()
    
    if model_oz == 'FBS':
        df_unit_oz['Базовая стоимость'] = (df_unit_oz['С/С'] + ((df_unit_oz['Объем_л'] - 1) * 12 + 76) \
        +  df_unit_oz['Оплата за отправление FBS'] ) / (1 - value_chp_oz - (0.055 + 0.015)  \
        - df_unit_oz['Вознаграждение на FBS']  -  tax_oz - bud_oz)
        
        df_unit_oz['ИТОГО Логистика'] = ((df_unit_oz['Объем_л'] - 1) * 12) + 76 + (0.055 + 0.015) * df_unit_oz['Базовая стоимость'] + df_unit_oz['Оплата за отправление FBS'] 
        df_unit_oz['ИТОГО Комиссия'] = df_unit_oz['Вознаграждение на FBS'] * df_unit_oz['Базовая стоимость'] #/ 100
        
    elif model_oz == 'FBO':
        df_unit_oz['Базовая стоимость'] = ( df_unit_oz['С/С'] + (df_unit_oz['Объем_л'] - 1) * 10 + 63)\
        / (1 - value_chp_oz - (0.055 + 0.015) - df_unit_oz['Вознаграждение на FBO']  -  tax_oz - bud_oz)
        
        df_unit_oz['ИТОГО Логистика'] = ((df_unit_oz['Объем_л'] - 1) * 10) + 63 + (0.055 + 0.015) * df_unit_oz['Базовая стоимость']
        df_unit_oz['ИТОГО Комиссия'] = df_unit_oz['Вознаграждение на FBO'] * df_unit_oz['Базовая стоимость']# / 100
    
    
    df_unit_oz['Налог'] = tax_oz * df_unit_oz['Базовая стоимость']
    df_unit_oz['Маркетинг'] = bud_oz * df_unit_oz['Базовая стоимость']
    df_unit_oz['Прибыль минус расходы с 1шт'] = df_unit_oz['Базовая стоимость'] - df_unit_oz['С/С'] \
                                                - df_unit_oz['ИТОГО Комиссия'] - df_unit_oz['ИТОГО Логистика'] \
                                                - df_unit_oz['Налог'] -  df_unit_oz['Маркетинг'] 
    
    df_unit_oz['Маржа'] = df_unit_oz['Прибыль минус расходы с 1шт'] / df_unit_oz['Базовая стоимость']
    
    st.dataframe(df_unit_oz)
    
    csv_oz = df_unit_oz.to_csv(index=False).encode('utf-8')
    
    # Кнопка скачивания
    st.download_button(
        label="Скачать результат в CSV",
        data=csv_oz,
        file_name='unit_oz_result.csv',
        mime='text/csv'
    )


    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_unit_oz.to_excel(writer, index=False)
    
    # Получаем данные Excel файла
    excel_data_oz = output.getvalue()
    
    # Кнопка скачивания
    st.download_button(
        label="Скачать результат в Excel",
        data=excel_data_oz,
        file_name='unit_oz_result.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )










    df_unit_y = df_seb[['Артикул продавца', 'Наименование товара', 'Категория ям', 'Длина', 'Ширина', 'Высота', 'С/С']]
    df_unit_y = df_unit_y.assign(Объемный_вес=(df_unit_y['Длина'] * df_unit_y['Ширина'] * df_unit_y['Высота']) / 5000)
    df_unit_y['Объемный_вес'] = df_unit_y['Объемный_вес'].round(1)
    df_unit_y = pd.merge(df_unit_y, df_y[['Категория', 'Тариф FBY', 'Тарифы FBS, Экспресс', 'Тариф DBS']], left_on='Категория ям', right_on='Категория', how='left')
    df_unit_y['Обработка заказа'] = df_y[df_y['FBS'] == where_y].iloc[:, 10].item()
    df_unit_y = pd.merge(df_unit_y, df_y[['Доставка между населенными пунктами', 'Unnamed: 14', 'Unnamed: 17']].dropna(), left_on='Объемный_вес', right_on='Доставка между населенными пунктами', how='left')

    if model_oz == 'FBS':
        df_unit_y['Базовая стоимость'] = (df_unit_y['С/С'] + df_unit_y['Unnamed: 14' + (df_unit_y['Обработка заказа'])] + 0.12) \
         / (1 - (0.013 + 0.014 + 0.045) - df_unit_y['Тарифы FBS, Экспресс']  -  tax_y - bud_y - value_chp_y)
        
        df_unit_y['Доставка покупателю'] = df_unit_y['Базовая стоимость'] * 0.045
    
        df_unit_y['ИТОГО Логистика'] = ((df_unit_y['Обработка заказа'])) + df_unit_y['Доставка покупателю'] + df_unit_y['Unnamed: 14'] 
        df_unit_y['ИТОГО Комиссия'] = df_unit_y['Тарифы FBS, Экспресс'] * df_unit_y['Базовая стоимость'] #/ 100
        
    elif model_oz == 'FBO':
        df_unit_y['Базовая стоимость'] = ( df_unit_y['С/С'] + df_unit_y['Unnamed: 17'] + 0.12)\
        / (1 - (0.013 + 0.014 + 0.045) - df_unit_y['Тариф FBY']  -  tax_y - bud_y - value_chp_y)
        df_unit_y['Доставка покупателю'] = df_unit_y['Базовая стоимость'] * 0.045
    
        df_unit_y['ИТОГО Логистика'] = df_unit_y['Доставка покупателю'] + df_unit_y['Unnamed: 17'] 
        df_unit_y['ИТОГО Комиссия'] = df_unit_y['Тариф FBY'] * df_unit_y['Базовая стоимость']# / 100
    
    df_unit_y['Прием выплат'] = df_unit_y['Базовая стоимость'] * 0.013 + 0.12
    
    df_unit_y['Карта пэй'] = df_unit_y['Базовая стоимость'] * 0.014
    df_unit_y['Налог'] = tax_y * df_unit_y['Базовая стоимость']
    df_unit_y['Маркетинг'] = bud_y * df_unit_y['Базовая стоимость']
    
    
    df_unit_y['Прибыль минус расходы с 1шт'] = df_unit_y['Базовая стоимость'] - df_unit_y['С/С'] \
                                                - df_unit_y['ИТОГО Комиссия'] - df_unit_y['ИТОГО Логистика'] \
                                                - df_unit_y['Налог'] -  df_unit_y['Маркетинг'] \
                                                - df_unit_y['Прием выплат'] - df_unit_y['Карта пэй']

    #value_chp_y * X = X - C/C - X * (Тариф) - X * (0.045 + 0.013 + 0.014) - (Обработка) - (Unnamed) - tax * X - bud * X - 0.12 
    # Обработка + Unnamed + 0.12 + C/C 
    # 1 - value - тариф - (0.045 + 0.013 + 0.014) - tax - bud
    
    df_unit_y['Маржа'] = df_unit_y['Прибыль минус расходы с 1шт'] / df_unit_y['Базовая стоимость']

    st.title('Теперь Яндекс Маркет')
    st.dataframe(df_unit_y)
    
    csv_y = df_unit_y.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="Скачать результат в CSV",
        data=csv_y,
        file_name='unit_oz_result.csv',
        mime='text/csv'
    )


    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_unit_y.to_excel(writer, index=False)
    
    # Получаем данные Excel файла
    excel_data_y = output.getvalue()
    
    # Кнопка скачивания
    st.download_button(
        label="Скачать результат в Excel",
        data=excel_data_y,
        file_name='unit_oz_result.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )