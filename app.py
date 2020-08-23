import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import time
import altair as alt


DATA_URL = ('african_covid_spread.csv')
@st.cache(persist=True)
def load_dataset():
    data= pd.read_csv(DATA_URL)
    return data

data = load_dataset()
st.header('African Covid-19 Stories')

#sidebar menu config
country_name_input = st.sidebar.multiselect('Country name', data.location.unique().tolist())
# by country name
if len(country_name_input) > 0:
    data = data[data['location'].isin(country_name_input)]
    
metrics = ['active_cases',
 'total_cases',
 'new_cases',
 'total_deaths',
 'new_deaths',
 'recovered',
 'new_recovered',
 'total_cases_per_million',
 'new_cases_per_million',
 'new_cases_smoothed_per_million',
 'total_deaths_per_million',
 'new_deaths_per_million']

cols = st.selectbox('Covid metric to view', metrics)
# let's ask the user which column should be used as Index
if cols in metrics:   
    metric_to_show_in_covid_Layer = cols
    
st.subheader('Comparision of infection growth')

################################################
### create the chloropleth map
st.subheader('evolution of total cases on map')
df_map_graph = data[data['date']>= '2020-02-13'] 
df_map_graph = df_map_graph.sort_values(by=['date'], ascending=True)

fig = px.choropleth(df_map_graph, 
                    locations='iso_code',
                    color='total_cases',
                    hover_name='location',
                    animation_frame='date',
                    scope='africa',
                    projection='natural earth',
                    hover_data=['total_deaths', 'recovered'],
                    height=700)
fig.update_layout(
    geo=dict(
        showframe = False,
        showcoastlines = False,
    )
)

st.plotly_chart(fig)


#####################
## another animated map 

st.subheader('Covid spread thought animated scatter graph')

# process data
scatter_graph = data[data['date']>='2020-02-20']
scatter_graph.columns = [col.lower() for col in scatter_graph.columns]
scatter_graph = scatter_graph.groupby(['date', 'location']).sum()[['lat', 'long','total_cases', 'recovered', 'total_deaths']]


# Compute bubble sizes
scatter_graph['size'] = scatter_graph['total_cases'].apply(lambda x: (np.sqrt(x/100) + 1) if x > 500 else (np.log(x) / 2 + 1)).replace(np.NINF, 0)
    
    # Compute bubble color
scatter_graph['color'] = (scatter_graph['recovered']/scatter_graph['total_cases']).fillna(0).replace(np.inf , 0)


# create the bubble map

days = scatter_graph.index.levels[0].tolist()

frames = [{
    'name' : 'frame_{}'.format(day),
    'data' : [{
        'type': 'scattermapbox',
        'lat' : scatter_graph.xs(day)['lat'],
        'lon' : scatter_graph.xs(day)['long'],
        'marker':go.scattermapbox.Marker(
            size=scatter_graph.xs(day)['size'],
            color=scatter_graph.xs(day)['color'],
            showscale=True,
            colorbar={'title':'recovered', 'titleside':'top', 'thickness':4, 'ticksuffix':' %'},
        ),
        'customdata':np.stack((scatter_graph.xs(day)['total_cases'], scatter_graph.xs(day)['recovered'],  scatter_graph.xs(day)['total_deaths'], pd.Series(scatter_graph.xs(day).index)), axis=-1),
        'hovertemplate': "<extra></extra><em>%{customdata[3]}  </em><br>🚨  %{customdata[0]}<br>🏡  %{customdata[1]}<br>⚰️  %{customdata[2]}",
    }],
    } for day in days]  


sliders = [{
    'transition':{'duration': 0},
    'x':0.08, 
    'len':0.88,
    'currentvalue':{'font':{'size':15}, 'prefix':'📅 ', 'visible':True, 'xanchor':'center'},  
    'steps':[
        {
            'label':day,
            'method':'animate',
            'args':[
                ['frame_{}'.format(day)],
                {'mode':'immediate', 'frame':{'duration':100, 'redraw': True}, 'transition':{'duration':50}}
              ],
        } for day in days]
}]

play_button = [{
    'type':'buttons',
    'showactive':True,
    'x':0.045, 'y':-0.08,
    'buttons':[{ 
        'label':'🎬', # Play
        'method':'animate',
        'args':[
            None,
            {
                'frame':{'duration':100, 'redraw':True},
                'transition':{'duration':50},
                'fromcurrent':True,
                'mode':'immediate',
            }
        ]
    }]
}]

# Defining the initial state
data = frames[0]['data']

# Adding all sliders and play button to the layout
layout = go.Layout(
    sliders=sliders,
    updatemenus=play_button,
    #margin={"r":0,"t":0,"l":0,"b":0}
    mapbox={
        'accesstoken':'pk.eyJ1IjoiaGVyaWMiLCJhIjoiY2lwcHh2cHpwMDA1aWhybnBqbHQzOXQydCJ9.4CM5ZOcHIkaSnKnXywwJlA',
        'center':{"lat": 9.08, "lon": 8.67},
        'zoom':1.5,
        'style':'light'
    }
)

# Creating the figure
fig = go.Figure(data=data, 
                layout=layout, 
                frames=frames)

# Displaying the figure
#fig.show()

st.plotly_chart(fig)
        
    
    




  
     





