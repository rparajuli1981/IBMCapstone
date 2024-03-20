# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

pd.set_option('display.max_columns', None)

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df['Launch Site'].unique()

success_df = spacex_df[spacex_df['class'] == 1].groupby("Launch Site").sum().reset_index()
failed_df = spacex_df[spacex_df['class'] == 0].groupby("Launch Site").sum().reset_index()

print(failed_df[failed_df["Launch Site"]=='CCAFS LC-40'].iloc[0,1])

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': launch_sites[0], 'value': launch_sites[0]},
                                                 {'label': launch_sites[1], 'value': launch_sites[1]},
                                                 {'label': launch_sites[2], 'value': launch_sites[2]},
                                                 {'label': launch_sites[3], 'value': launch_sites[3]},
                                             ],
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),
                                html.Br(),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0 Kg', 10000: '10000 Kg'},
                                                value=[0, 10000]),
                                html.Div(id='output-container-range-slider'),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    success_df = spacex_df.groupby("Launch Site")['class'].sum().reset_index()
    failed_df = spacex_df[spacex_df['class']==0].groupby("Launch Site")['class'].count().reset_index()
    if entered_site == 'ALL':
        fig = px.pie(success_df, values='class',
        names='Launch Site',
        title='Total success launches by sites')
    else:
        # return the outcomes piechart for a selected site
        success = success_df[success_df["Launch Site"] == entered_site].iloc[0,1]
        failed = failed_df[failed_df["Launch Site"]==entered_site].iloc[0,1]
        data = pd.DataFrame({'result':['success','failed'], 'class':[success, failed]})
        fig = px.pie(data, values='class',
        names='result',
        title='Success and Failed Launches')
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id="payload-slider", component_property="value"))
def get_scatter(site, payload):
    if site == 'ALL':
        new_df = spacex_df
        new_df2 = new_df[new_df["Payload Mass (kg)"] >= payload[0]]
        new_df3 = new_df2[new_df["Payload Mass (kg)"] <= payload[1]]
        fig2 = px.scatter(new_df3, y="class", x="Payload Mass (kg)", color="Booster Version Category")
    else:
        new_df = spacex_df[spacex_df["Launch Site"] == site]
        new_df2 = new_df[new_df["Payload Mass (kg)"] >= payload[0]]
        new_df3 = new_df2[new_df["Payload Mass (kg)"] <= payload[1]]
        fig2 = px.scatter(new_df3, y="class", x="Payload Mass (kg)", color="Booster Version Category")
    return fig2
# Run the app
if __name__ == '__main__':
    app.run_server()
