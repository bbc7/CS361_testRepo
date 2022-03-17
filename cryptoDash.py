# NAME: Colin Bebee
# CLASS: CS 361
# PROJECT: Cryptocurrency Dashboard
# DATE: 3/16/2022 (final revision)

# Proper imports
from dash import Dash, html, dcc, dash_table, Input, Output, State
import requests
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import time


############### MICROSERVICE #################
# Get definitions from partner's microservice. 
# This needs to run as a separate process on port 9000.
# String manipulation of definitions are used to improve aesthetics.
#
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

# CSS Styling
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# What's new descriptions
whatIsNew = "Due to data licensing and/or regulatory concerns, the following are not being shown: 1) Luna and 2) Ripple"

# FUNCTION DECLARATIONS FOR CHARTS 2 & 3
# - Generate main price chart
# - Calls API for each currency
def genLineChart(identifier):
    keepTrying = True   # Used in order to account for API errors
    while(keepTrying == True):
        url = 'http://api.coincap.io/v2/assets/' + identifier + '/history?interval=d1'
        response = requests.get(url)
        if(response.status_code == 429):
            print('API issue: retrying line chart data')
            time.sleep(0.1) # Used to address API limits (too frequest of requests)
        else:
            dataframe = pd.DataFrame(response.json()['data'])
            dataframe["priceUsd"] = dataframe['priceUsd'].astype(float)
            figToReturn = px.line(dataframe, x='date', y = 'priceUsd', title=(identifier.upper() + " - Historical Price Data"))
            figToReturn.update_layout(title_x=0.5)
            keepTrying = False
    return figToReturn

# Obtains volume data for each currency (expects a list of 3 currencies).
def genBigMovers(listOfIDs):
    volumeData = pd.DataFrame(columns=['Currency', 'Volume last 24 Hours'])
    i = 0
    while (i < len(listOfIDs)):
        currency = listOfIDs[i]
        url = 'http://api.coincap.io/v2/assets/' + currency
        response = requests.get(url)
        if (response.status_code == 200):
            dataframe = pd.DataFrame(response.json()['data'], index = [0])
            dataframe["volumeUsd24Hr"] = dataframe['volumeUsd24Hr'].astype(float)
            new_row = {'Currency': currency.capitalize(), 'Volume last 24 Hours': dataframe.iat[0,7]}
            volumeData = volumeData.append(new_row, ignore_index=True)
            i = i +1
            time.sleep(0.1) # Used to address API limits (too frequest of requests)
        else:
            print('API issue: retrying volume data')
            time.sleep(0.1) 
            volumeData = pd.DataFrame(columns=['Currency', 'Volume last 24 Hours'])
            i = 0   # Reset in order to loop the entire list again due to API error
    figToReturn = px.bar(volumeData, x='Currency', y = 'Volume last 24 Hours', title="Trading Volume of Top 3 Currencies (by market cap) over Last 24 Hours")
    figToReturn.update_layout(title_x=0.5)
    figToReturn.update_traces(marker_color='green')
    return figToReturn


# Utilize API call for market capitalization data (primary item on the dashboard)
url = 'http://api.coincap.io/v2/assets'
keepTrying = True   # Used in order to account for API errors
while(keepTrying == True):
    response = requests.get(url)
    if(response.status_code == 429):
        print('API issue: retrying market cap data')
        time.sleep(0.1)   # Used to address API limits (too frequent of requests)
    else:
        dataframe = response.json()['data']
        keepTrying = False

# Arrange market cap data into proper tabular form for easier use
tabularData = list()
count = 0
i = 0
while(count < 10):
    # Condition is excluding cerain currencies due to data issues with the API
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

# Generate starting graphs for dashboard
marketCapChart = px.pie(tabularData, values = 'Market Cap', names = 'Name')
priceChart= genLineChart('bitcoin')
volumeChart = genBigMovers(tabularData["ID"][0:3])

# Design layout of dashboard application
app.layout = html.Div(children=[
    # Top menu, labels, and buttons
    html.H1(children='Cryptocurrency Dashboard', style={'text-align':'center'}),
    html.Div(children='Basic Market Data\n\n', style={'text-align':'center'}),
    html.A(html.Button("Market Capitalization Data", style={'horizontalAlign':'middle'}), href='#pieChartLabel'),
    html.A(html.Button("Price Charts"), href="#priceChart"),
    html.A(html.Button("Volume Data"), href="#volumeChart"),
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
    html.Hr(style={'height':'15px'}),       # Line break

    # Definitions data (relies on partner's microservice)
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
    html.Hr(style={'height':'15px'}),       # Line break

    # Market Capitalization Pie Chart
    html.H4("Top 10 Largest Cryptocurencies - Current Data", id = "pieChartLabel", style={'text-align':'center'}),
    dcc.Graph(
        id='example-graph',
        figure=marketCapChart
    ),
    html.Div(" "),

    # Market Capitalization Table
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
    html.Hr(style={'height':'15px'}),       # Line Break

    # Price chart and dropdown selection for chart
    dcc.Dropdown(
        options=tabularData["Name"],
        id="dropdownID",
        value = 'Bitcoin'
    ),
    html.Div(id='dd-output-container'),

    dcc.Graph(
        id="priceChart",
        figure=priceChart),
    
    html.Hr(style={'height':'15px'}),       # Line break

    # Volume chart and checkboxes (top 3 currencies only)
    dcc.Checklist(
        options =[
            {'label': tabularData["ID"][0].capitalize(), 'value': tabularData["ID"][0]},
            {'label': tabularData["ID"][1].capitalize(), 'value': tabularData["ID"][1]},
            {'label': tabularData["ID"][2].capitalize(), 'value': tabularData["ID"][2]},
        ],
        id = "checklistID",
        labelStyle={'display':'block'},
        value = tabularData["ID"][0:3]
    ),

    dcc.Graph(
        id="volumeChart",
        figure = volumeChart)
])
# End dashboard design


#### CALLBACKS FOR UPDATING DASHBOARD DATA ####
# Callback for updating price chart
@app.callback(
    Output('volumeChart', 'figure'),
    Input('checklistID', 'value')
)
def update_output(value):
    fig4 = genBigMovers(value)
    return fig4

# Callback for updating price chart
@app.callback(
    Output('priceChart', 'figure'),
    Input('dropdownID', 'value')
)
def update_output2(value):
    if (value == "BNB"):
        fig3 = genLineChart('binance-coin')
    elif (value == "Shiba Inu"):
        fig3 = genLineChart('shiba-inu')
    else:
        fig3 = genLineChart(value.lower())

    return fig3

# Callback for modal at top menu of dashboard
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
#### END CALLBACKS ####


# Main() for running (make note of port usage)
if __name__ == '__main__':
    app.run_server(port=8125, debug=True)