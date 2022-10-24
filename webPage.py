import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from pytz import country_names
import seaborn as sns
import streamlit as st
import altair as alt

'''
# Visualizacion de casos de Covid-19

'''

def rename_columns(input_data):
    output_data = input_data.rename(
                             columns = {
                                 'Province/State':'subregion',
                                 'Country/Region':'country',
                                 'Lat':'lat',
                                 'Long':'long'
                             })
    return output_data

def melt_data(input_data, value_var_name):
    output_data = input_data.melt(
                             id_vars = ['country', 'subregion', 'lat', 'long'],
                             var_name = 'date_RAW',
                             value_name = value_var_name
                            )
    return output_data

def dates(input_data):
    output_data = input_data.assign(
                             date = pd.to_datetime(input_data.date_RAW, format='%m/%d/%y')
                            )
    output_data.drop(columns = ['date_RAW'], inplace = True)
    return output_data

def ordering_data(input_data, value_var_name):
    output_data = (input_data.filter(['country', 'subregion', 'date', 'lat', 'long', value_var_name])
                  .sort_values(['country', 'subregion', 'date', 'lat', 'long'])
                  .reset_index(drop=True)
                  )
    return output_data

def get_data(input_csv, value_var_name):
    data = pd.read_csv(input_csv)
    data = rename_columns(data)
    data = melt_data(data, value_var_name)
    data = dates(data)
    data = ordering_data(data, value_var_name)
    
    return data

def difference_values(base = None, delta1 = None, delta2 = None):

    if delta1 == None:
        for i in range(len(base)):
            try:
                base[i+1] -=  base[i]
            except IndexError:
                pass    
    else:
        for i in range(len(base)):
            base[i] = base[i] - delta1[i] - delta2[i]

    return base


covid_positive = get_data("./DATA/time_series_covid19_confirmed_global.csv", 'CONFIRMED')
covid_deaths =  get_data("./DATA/time_series_covid19_deaths_global.CSV", 'DEATH')
covid_recovered =  get_data("./DATA/time_series_covid19_recovered_global.CSV", 'RECOVERED')

covid_deaths.drop(columns = ['lat', 'long'], inplace = True)
covid_recovered.drop(columns = ['lat', 'long'], inplace = True)

covid_data = (covid_positive
             .merge(covid_deaths, on = ['country', 'subregion', 'date'], how = "left")
             .merge(covid_recovered, on = ['country', 'subregion', 'date'], how = "left")
             )

#covid_data

countryNames = covid_data['country'].unique()

# convert column to datetime
covid_data['date'] = pd.to_datetime(covid_data['date'])


# Agrupacion de fechas por año y mes
covid_data['year_month_of_registration'] = covid_data['date'].map(lambda dt: dt.strftime('%Y-%m'))

# Agrupacion de fechas por año
covid_data['year_of_registration'] = covid_data['date'].map(lambda dt: dt.strftime('%Y'))

#----------------------------------------------------------------------------------BARRAS 1----------------------------------------------------------------------------------------
st.header("Numero de contagiados a nivel global (acumulado)")

covid_data_copy = covid_data

delta = covid_data_copy['CONFIRMED'].tolist()

covid_data_copy['delta'] = delta

grouped_df = covid_data_copy.groupby('year_month_of_registration')['delta'].sum().to_frame("count").reset_index()

data_1 = pd.DataFrame({
    'Numero de contagiados':  grouped_df['count'].tolist(),
    'Fecha':  grouped_df['year_month_of_registration'].tolist(),
})

bar_chart = alt.Chart(data_1).mark_bar(size=10).encode(
        y='Numero de contagiados:Q',
        x='Fecha:O',
    )

text = bar_chart.mark_text(
    align='center',
    baseline='middle',
    dx=1, # Nudges text to right so it doesn't appear on top of the bar
    color='white'
).encode(
    text='Numero de contagiados:Q'
)

st.altair_chart((bar_chart + text).properties(width=1200))

#----------------------------------------------------------------------------------BARRAS 2----------------------------------------------------------------------------------------
st.header("Numero de muertes a nivel global (acumulado)")

covid_data_copy = covid_data

delta = covid_data_copy['DEATH'].tolist()

covid_data_copy['delta'] = delta

grouped_df = covid_data_copy.groupby('year_month_of_registration')['delta'].sum().to_frame("count").reset_index()

data_1 = pd.DataFrame({
    'Numero de muertes':  grouped_df['count'].tolist(),
    'Fecha':  grouped_df['year_month_of_registration'].tolist(),
})

bar_chart = alt.Chart(data_1).mark_bar(size=10).encode(
        y='Numero de muertes:Q',
        x='Fecha:O',
    )

text = bar_chart.mark_text(
    align='center',
    baseline='middle',
    dx=1, # Nudges text to right so it doesn't appear on top of the bar
    color='white'
).encode(
    text='Numero de muertes:Q'
)

st.altair_chart((bar_chart + text).properties(width=1200))

#--------------------------------------------------------------------------------LINEAS 1------------------------------------------------------------------------------------------
st.header("Visualizacion de registros de casos de Covid-19 por busqueda de pais")

st.subheader("Visualizacion de total de registros por evento de Covid-19, por mes y año")

option = st.selectbox(
    '¿Que pais quieres visualizar?',
    countryNames)

st.write('Has seleccionado:', option)

rslt_df = covid_data.loc[covid_data['country'] == option]

covid_data_copy = rslt_df

#CONFIRMADOS

delta = difference_values(base = covid_data_copy['CONFIRMED'].tolist())

covid_data_copy['delta'] = delta

grouped_df = covid_data_copy.groupby('year_month_of_registration')['delta'].sum().to_frame("count").reset_index()

data_2 = pd.DataFrame({
    'Fecha':  grouped_df['year_month_of_registration'].tolist(),
    'Contagiados':  grouped_df['count'].tolist(),
})

#MUERTES

covid_data_copy = rslt_df

delta = difference_values(base = covid_data_copy['DEATH'].tolist())

covid_data_copy['delta'] = delta

grouped_df = covid_data_copy.groupby('year_month_of_registration')['delta'].sum().to_frame("count").reset_index()

data_2["Muertes"] = grouped_df['count'].tolist()

#Recuperados

covid_data_copy = rslt_df

delta = difference_values(base = covid_data_copy['RECOVERED'].tolist())

covid_data_copy['delta'] = delta

grouped_df = covid_data_copy.groupby('year_month_of_registration')['delta'].sum().to_frame("count").reset_index()

data_2["Recuperados"] = grouped_df['count'].tolist()

data_2["Recuperados"] = data_2["Recuperados"].astype(int)

data_3 = data_2.reset_index(drop=True).melt('Fecha', var_name ='Evento', value_name ='Total')

# Create a selection that chooses the nearest point & selects based on x-value
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['Fecha'], empty='none')

line = alt.Chart(data_3).mark_line().encode(
    x='Fecha',
    y='Total',
    color='Evento'
)

# Transparent selectors across the chart. This is what tells us the x-value of the cursor
selectors = alt.Chart(data_3).mark_point().encode(
    x='Fecha',
    opacity=alt.value(0),
).add_selection(
    nearest
)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'Total', alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart(data_3).mark_rule(color='gray').encode(
    x='Fecha',
).transform_filter(
    nearest
)

st.altair_chart(alt.layer(
    line, selectors, points, rules, text
).properties(
    width=1200, height=500
))

st.caption("Tabla")
data_2

#--------------------------------------------------------------------------------BARRAS 3------------------------------------------------------------------------------------------
st.subheader("Visualizacion de total de registros acumulados por evento de Covid-19, por año (con opcion de mostrar por mes)")

rslt_df = covid_data.loc[covid_data['country'] == option]

covid_data_copy = rslt_df

covid_data_copy["RECOVERED"] = covid_data_copy["RECOVERED"].astype(int)

option = 'year_of_registration'

agree = st.checkbox('Por mes')

if agree:
    option = 'year_month_of_registration'


#CONFIRMADOS
delta = difference_values(base = covid_data_copy['CONFIRMED'].tolist(), delta1 = covid_data_copy['DEATH'].tolist(), delta2 = covid_data_copy['RECOVERED'].tolist())

covid_data_copy['delta'] = delta

grouped_df = covid_data_copy.groupby(option)['delta'].sum().to_frame("count").reset_index()

data_4 = pd.DataFrame({
    'Fecha':  grouped_df[option].tolist(),
    'Contagiados':  grouped_df['count'].tolist(),
})

#MUERTES
grouped_df = covid_data_copy.groupby(option)['DEATH'].sum().to_frame("count").reset_index()

data_4["Muertes"] = grouped_df['count'].tolist()

#RECUPERADOS
grouped_df = covid_data_copy.groupby(option)['RECOVERED'].sum().to_frame("count").reset_index()

data_4["Recuperados"] = grouped_df['count'].tolist()

data_5 = data_4.reset_index(drop=True).melt('Fecha', var_name ='Evento', value_name ='Total')

bar_chart1 = alt.Chart(data_5).mark_bar(    
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3
).encode(
    x='Fecha',
    y='Total',
    color='Evento'
)

st.altair_chart(alt.layer(
     bar_chart1
).properties(
    width=1200, height=500
))

st.caption("Tabla")
data_4