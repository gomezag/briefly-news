import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from database.xata_api import XataAPI
from datetime import datetime


# Initialize the app
app = dash.Dash(__name__)
xata = XataAPI()

# Define the layout of the app
app.layout = html.Div([
    html.H1('Hello, World!'),
    html.Div(id="title_search_group", children=[
        dcc.Input(id='title_search', type='text', placeholder='Search in headlines'),
    ]),
    html.Div(id="date_search_group", children=[
        dcc.DatePickerRange(id='date_search', start_date='2023-05-01', end_date='2023-05-05'),
    ]),
    html.Button("Buscar", id="search"),
    html.Div(id='result_table')
])

@app.callback(
    Output("result_table", "children"),
    [Input("search", "n_clicks"),
     State('title_search', 'value'),
     State('date_search', 'start_date'),
     State('date_search', 'end_date')]
)
def update_results(btn, text, start_date, end_date):
    st_date = datetime.strptime(start_date, '%Y-%m-%d')
    ed_date = datetime.strptime(end_date, '%Y-%m-%d')
    articles = xata.query('news_article', filter={'date': {'$gt': st_date, '$lt': ed_date}, 'title': {'$contains':text}})
    rows = []
    for article in articles:
        row = []
        for key in ['date', 'title', 'subtitle', 'url']:
            if key == 'url':
                cell = html.Td(html.A("Link", href=article[key]))
            else:
                cell = html.Td(article[key])
            row.append(cell)
        rows.append(html.Tr(children=row))
    children = [html.Th(key) for key in ['Fecha', 'Titular', 'Resumen', 'URL']]
    children.extend(rows)
    table = html.Table(children=children)
    return html.Div(children=table)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
