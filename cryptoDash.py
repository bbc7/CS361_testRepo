# Proper improts
from dash import Dash, html, dcc, dash_table, Input, Output, State
import requests
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Load local data (THIS IS OLD FROM TESTING)
# definitions = pd.read_csv("definitions.csv")



############### MICROSERVICE #################
# Get definitions from partner's microservice.
# Market Cap Definition
parameters1 = {"arg1": "market_capitalization"}
response1 = requests.get("http://localhost:9000/wiki", params = parameters1)
def1 = str(response1.json()["1"] + response1.json()["2"])
sentences1 = def1.split(".")
marketCapDef = (sentences1[0] + ". " + sentences1[1] + ".")

# Price Chart (aka Run Chart) definition
parameters2 = {"arg1": "run_chart"}
response2 = requests.get("http://localhost:9000/wiki", params = parameters2)
priceChartDef = response2.json()["0"]
############### MICROSERVICE #################

# Put microservice-based definitions into a dictionary for later table use
definitions = {"Market Capitalization": marketCapDef, "Price Chart (Run Chart)": priceChartDef}
defItems = definitions.items()
defList = list(defItems)
defTable = pd.DataFrame(defList)
defTable.columns = ["Term", "Definitions"]




# Styling
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# What's new descriptions
whatIsNew = "Due to data licensing and/or regulatory concerns, the following are not being shown: 1) Luna and 2) Ripple"

# Function Declation: 
# - Generate main price chart
# - Calls API for each currency
def genLineChart(identifier):
    url = 'http://api.coincap.io/v2/assets/' + identifier + '/history?interval=d1'
    response = requests.get(url)
    dataframe = pd.DataFrame(response.json()['data'])
    dataframe["priceUsd"] = dataframe['priceUsd'].astype(float)
    figToReturn = px.line(dataframe, x='date', y = 'priceUsd', title=(identifier.upper() + " - Historical Price Data"))
    figToReturn.update_layout(title_x=0.5)
    return figToReturn

# Obtain main API call
url = 'http://api.coincap.io/v2/assets'
response = requests.get(url)
dataframe = response.json()['data']

# Arrange data into proper tabular form for easier use
tabularData = list()
count = 0
i = 0
while(count < 10):
    if (dataframe[i]['name'] != 'XRP' and dataframe[i]['name'] != "Terra" and dataframe[i]['name'] != 'USD Coin' and dataframe[i]['name'] != 'Binance USD'):
        tabularData.append((dataframe[i]['id'], dataframe[i]['symbol'], dataframe[i]['name'], round(float(dataframe[i]['marketCapUsd'])/1000000, 2)))
        count = count + 1
    i = i + 1

tabularData = pd.DataFrame(data=tabularData, columns=["ID", "Symbol", "Name", "Market Cap"])
tabularData2 = tabularData.copy()
tabularData2.drop(columns=['ID'], inplace=True)
tabularData2.rename(columns={'Market Cap': 'Market Cap ($billions)'}, inplace=True)


# Create Dash application
app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

# Generate starting graphs
marketCapChart = px.pie(tabularData, values = 'Market Cap', names = 'Name')
priceChart= genLineChart('bitcoin')


app.layout = html.Div(children=[
    html.H1(children='Cryptocurrency Dashboard', style={'text-align':'center'}),

    html.Div(children='Basic Market Data\n\n', style={'text-align':'center'}),
    html.A(html.Button("Market Capitalization Data", style={'horizontalAlign':'middle'}), href='#pieChartLabel'),
    html.A(html.Button("Price Charts"), href="#priceChart"),
    html.Button("What's New?", id="open"),
    dbc.Modal(
        [
            dbc.ModalHeader("What's New?"),
            dbc.ModalBody(html.Div(whatIsNew)),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        id="modal",
    ) ,


    html.Hr(style={'height':'15px'}),

    dash_table.DataTable(
    defTable.to_dict('records'),
    [{"name": i, "id": i} for i in defTable.columns],
    style_cell={'padding': '5px', 'whiteSpace':'normal', 'textAlign':'left'},
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        'margin-left': 'left',
    },
),

    html.Hr(style={'height':'15px'}),

    html.H4("Top 10 Largest Cryptocurencies - Current Data", id = "pieChartLabel", style={'text-align':'center'}),

    dcc.Graph(
        id='example-graph',
        figure=marketCapChart
    ),
    html.Div(" "),

    dash_table.DataTable(
    tabularData2.to_dict('records'),
    [{"name": i, "id": i} for i in tabularData2.columns],
    style_cell={'padding': '5px'},
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold'
    },
    fill_width=False
),
    html.Hr(style={'height':'15px'}),

    dcc.Dropdown(
        options=tabularData["Name"],
        id="dropdownID",
        value = 'Bitcoin'
    ),
    html.Div(id='dd-output-container'),

    dcc.Graph(
        id="priceChart",
        figure=priceChart)

])


@app.callback(
    Output('priceChart', 'figure'),
    Input('dropdownID', 'value')
)
def update_output(value):
    if (value == "BNB"):
        fig3 = genLineChart('binance-coin')
    elif (value == "Shiba Inu"):
        fig3 = genLineChart('shiba-inu')
    else:
        fig3 = genLineChart(value.lower())

    return fig3



@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



if __name__ == '__main__':
    app.run_server(port=8125, debug=True)