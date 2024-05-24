from fastapi import FastAPI, HTTPException
from typing import List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = pd.read_csv('covid_data.csv')

app = FastAPI()

@app.get("/districts/", response_model=List[str])
def get_districts():
    districts = df['District'].unique().tolist()
    districts.insert(0, "All Districts")
    return districts

@app.post("/district/")
def get_district_data(districts: List[str]):
    if not districts or ("All Districts" in districts and len(districts) > 1):
        raise HTTPException(status_code=400, detail="Invalid selection")
    if "All Districts" in districts:
        return df.to_dict(orient='records')
    elif len(districts) == 1:
        district_data = df[df['District'] == districts[0]].iloc[0].to_dict()
        return district_data
    else:
        filtered_df = df[df['District'].isin(districts)]
        return filtered_df.to_dict(orient='records')

@app.post("/district/chart/")
def get_district_chart(districts: List[str]):
    if not districts:
        raise HTTPException(status_code=400, detail="No districts selected")

    if "All Districts" in districts:
        return generate_bar_chart(df, 'All Districts')
    elif len(districts) == 1:
        district_data = df[df['District'] == districts[0]].iloc[0]
        return generate_pie_chart(district_data)
    else:
        filtered_df = df[df['District'].isin(districts)]
        return generate_bar_chart(filtered_df, 'Selected Districts')

def generate_pie_chart(data):
    labels = ['Active', 'Deceased', 'Recovered']
    values = [data['Active'], data['Deceased'], data['Recovered']]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text='COVID-19 Cases')
    return fig.to_json()

def generate_bar_chart(data, title):
    fig = make_subplots(rows=1, cols=1)
    colors = ['red', 'blue', 'green']
    for i, status in enumerate(['Active', 'Deceased', 'Recovered']):
        fig.add_trace(go.Bar(x=data['District'], y=data[status], name=status, marker_color=colors[i]))

    fig.update_layout(barmode='stack', title_text=f'COVID-19 Cases by District ({title})')
    return fig.to_json()
