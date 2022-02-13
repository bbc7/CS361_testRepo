# import requests
# url = 'https://rest.coinapi.io/v1/exchangerate/BTC/USD/history?period_id=10DAY&time_start=2016-01-01T00:00:00&time_end=2016-02-01T00:00:00'
# headers1 = {'X-CoinAPI-Key' : '936B9382-C258-47E3-9C92-6C20309830A7'}
# response = requests.get(url, headers=headers1)

# print(response.text)
from dash import Dash, html, dcc, dash_table, Input, Output
import requests
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

definitions = pd.read_csv("definitions.csv")
definitions.to_csv("testDefs.csv")
print(definitions)

def genLineChart(identifier):
    url = 'http://api.coincap.io/v2/assets/' + identifier + '/history?interval=d1'
    response = requests.get(url)
    dataframe = pd.DataFrame(response.json()['data'])
    dataframe["priceUsd"] = dataframe['priceUsd'].astype(float)
    figToReturn = px.line(dataframe, x='date', y = 'priceUsd', title=(identifier.upper() + " - Historical Price Data"))
    figToReturn.update_layout(title_x=0.5)
    return figToReturn


url = 'http://api.coincap.io/v2/assets'
response = requests.get(url)



app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

dataframe = response.json()['data']

# marketCap = pd.DataFrame(columns=["Coin", "Market Cap"], index = "Coin")
test = list()

for i in range(10):
    # print(dataframe[i]['symbol'])
    # print(dataframe[i]['marketCapUsd'])
    test.append((dataframe[i]['id'], dataframe[i]['symbol'], dataframe[i]['name'], round(float(dataframe[i]['marketCapUsd'])/1000000, 2)))
# print(response.json()['data'][1])

test = pd.DataFrame(data=test, columns=["ID", "Symbol", "Name", "Market Cap"])
# test2 = pd.DataFrame(data=prices, columns=["Price", "Date"])
test2 = test.copy()
test2.drop(columns=['ID'], inplace=True)

print(test2)

fig = px.pie(test, values = 'Market Cap', names = 'Name')

# dataframe2["priceUsd"] = dataframe2['priceUsd'].astype(float)
fig2 = genLineChart('bitcoin')


app.layout = html.Div(children=[
    html.H1(children='Cryptocurrency Dashboard', style={'text-align':'center'}),

    html.Div(children='Basic Market Data\n\n', style={'text-align':'center'}),
    html.Button("Market Capitalization Data", style={'horizontalAlign':'middle'}),
    html.Button("Price Charts"),
    html.Button("What's New?"),
    html.Hr(style={'height':'10px'}),

    dash_table.DataTable(
    definitions.to_dict('records'),
    [{"name": i, "id": i} for i in definitions.columns],
    style_cell={'padding': '5px', 'whiteSpace':'normal', 'textAlign':'left'},
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        'margin-left': 'left',
    },
),

    html.Hr(style={'height':'10px'}),

    html.H4("Top 10 Largest Cryptocurencies - Current Data", style={'text-align':'center'}),

    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    html.Div(" "),

    dash_table.DataTable(
    test2.to_dict('records'),
    [{"name": i, "id": i} for i in test2.columns],
    style_cell={'padding': '5px'},
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold'
    },
    fill_width=False
),
    html.Hr(style={'height':'10px'}),

    dcc.Dropdown(
        options=['bitcoin', 'ethereum'],
        id="dropdownID",
        value = 'bitcoin'
    ),
    html.Div(id='dd-output-container'),

    dcc.Graph(
        id="Bitcoin Price",
        figure = fig2)

])


# @app.callback(
#     Output('dd-output-container', 'children'),
#     Input('dropdownID', 'value')
# )

# def update_output(value):
#     fig2 = genLineChart(value)

# print(test2)

if __name__ == '__main__':
    app.run_server(debug=True)