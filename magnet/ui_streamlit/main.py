import time

import numpy as np
import pandas as pd
import requests
import streamlit as st

"""
# My first app
Here's our first attempt at using data to create a table:

## 参考
- [document](https://docs.streamlit.io/en/stable/getting_started.html)
- [streamlitでファイルをダウンロード](https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806)
"""

st.text("draw a line chart")
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
st.line_chart(chart_data)


st.text("plot a map")
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
)

st.map(map_data)


st.text("Add interactivity with widgets")
st.text("Use checkboxes to show/hide data")
if st.checkbox("input name to show"):
    df = pd.DataFrame(
        [
            {"name": "bob", "age": 20},
            {"name": "mary", "age": 30},
        ]
    )
else:
    df = pd.DataFrame(
        [
            {"name": "bob", "age": 20},
        ]
    )

df


st.sidebar.text("Use a selectbox for options")
option = st.sidebar.selectbox(
    "Which number do you like best?",
    pd.DataFrame(
        [
            {"name": "bob", "age": 20},
            {"name": "mary", "age": 30},
        ]
    ),
)

"You selected: ", option


left_column, right_column = st.beta_columns(2)
pressed = left_column.button("Press me?")
if pressed:
    right_column.write("Woohoo!")

expander = st.beta_expander("FAQ")
expander.write("Here you could put in some really, really long explanations...")


@st.cache
def get_covid_df(url):
    response_json = requests.get(url).json()
    df = pd.DataFrame(response_json["data"])
    return df


url = "https://raw.githubusercontent.com/tokyo-metropolitan-gov/covid19/development/data/daily_positive_detail.json"
df_covid = get_covid_df(url)

"""
# 東京都のCOVID-19感染者数
東京都 新型コロナウイルス感染症対策サイトの[Github](https://github.com/tokyo-metropolitan-gov/covid19)からデータを取得
"""

st.write(df_covid)


"Starting a long computation..."

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    # Update the progress bar with each iteration.
    latest_iteration.text(f"Iteration {i+1}")
    bar.progress(i + 1)
    time.sleep(0.1)

"...and now we're done!"


st.text("Enjoy!!!")
pd.DataFrame(
    [
        {"name": "bob", "age": 20},
    ]
)
