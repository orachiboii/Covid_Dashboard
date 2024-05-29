from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# Read Dataset
df = pd.read_csv('covid_data.csv')

app = FastAPI()

# Set up Cross-Origin Resource Sharing
# https://stackoverflow.com/questions/65635346/how-can-i-enable-cors-in-fastapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/districts/", response_model=List[str])
async def get_districts():
    # Return list of unique districts + "All Districts"
    districts = df['District'].unique().tolist()
    districts.insert(0, "All Districts")
    return districts

@app.post("/district/")
async def get_district_data(districts: List[str]):
    if not districts:
        raise HTTPException(status_code=400, detail="No districts selected")

    if "All Districts" in districts:
        return df.to_dict(orient='records') 
        #‘records’ : list like [{column -> value}, … , {column -> value}]
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html

    elif len(districts) == 1:
        district_data = df[df['District'] == districts[0]].iloc[0].to_dict() 
        return district_data
    else:
        filtered_df = df[df['District'].isin(districts)]
        return filtered_df.to_dict(orient='records') 

@app.post("/district/chart/")
async def get_district_chart(districts: List[str]):
    if not districts:
        raise HTTPException(status_code=400, detail="No districts selected")

    if "All Districts" in districts:
        fig = generate_stacked_bar_chart(df, 'All Districts')
    elif len(districts) == 1:
        district_data = df[df['District'] == districts[0]].iloc[0]
        fig = generate_pie_chart(district_data)
    else:
        filtered_df = df[df['District'].isin(districts)]
        fig = generate_stacked_bar_chart(filtered_df, 'Selected Districts')

    # Return as base64 for web app
    # https://stackoverflow.com/questions/38061267/matplotlib-graphic-image-to-base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return {"image": img_str}

# https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html
def generate_pie_chart(data):
    labels = ['Active', 'Deceased', 'Recovered']
    values = [data['Active'], data['Deceased'], data['Recovered']]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title('COVID-19 Cases')
    return fig

# https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html
def generate_stacked_bar_chart(data, title):
    fig, ax = plt.subplots()
    colors = ['blue', 'red', 'green']

    statuses = ['Active', 'Deceased', 'Recovered']
    bottom = [0] * len(data)

    for k, status in enumerate(statuses):
        ax.bar(data['District'], data[status], label=status, color=colors[k], bottom=bottom)
        bottom = [i + j for i, j in zip(bottom, data[status])]

    plt.xticks(rotation=90)
    ax.set_xlabel('District')
    ax.set_ylabel('Count')
    ax.set_title(f'COVID-19 Cases by District ({title})')
    ax.legend(loc="upper right")

    plt.tight_layout()
    return fig

# FastAPI Basics : https://www.youtube.com/watch?v=tLKKmouUams&t=1272s
# FastAPI + Next.js Dashboard: 
#   Backend: https://www.youtube.com/watch?v=2MMmmJ19QzE&t=1481s
#   Frontend: https://www.youtube.com/watch?v=UDvhgJTWtfQ&t=486s
