import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
from database.xata_api import XataAPI
from datetime import datetime
from llm.utils import get_related_people
from dash_holoniq_wordcloud import DashWordcloud

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
    query = {}
    date_q = {}
    if start_date:
        st_date = datetime.strptime(start_date, '%Y-%m-%d')
        date_q['$gt'] = st_date
    if end_date:
        ed_date = datetime.strptime(end_date, '%Y-%m-%d')
        date_q['$lt'] = ed_date
    if date_q != {}:
        query['date'] = date_q
    if text:
        query['title'] = {'$contains': text}
                         #{'title':{'$contains': text.lower()}},
                         #{'title':{'$contains': text.capitalize()}}
                         #]
    articles = xata.query('news_article', filter=query)['records']
    persons, links = get_related_people(articles)


    rows = []
    for article in links:
        row = []
        for key in ['date', 'title', 'subtitle', 'url', 'names']:
            if key == 'url':
                cell = html.Td(html.A("Link", href=article[key]))
            elif key == 'names':
                cell = html.Td(", ".join(article[key][:10]))
            else:
                cell = html.Td(article[key])
            row.append(cell)
        rows.append(html.Tr(children=row))
    children = [html.Th(key) for key in ['Fecha', 'Titular', 'Resumen', 'URL', 'POIs']]
    children.extend(rows)
    table = html.Table(children=children)
    # ptable = html.Table([
    #     html.Thead(
    #         html.Tr([html.Th(col) for col in persons.columns])
    #     ),
    #     html.Tbody([
    #         html.Tr([
    #             html.Td(persons.iloc[i][col]) for col in persons.columns
    #         ]) for i in range(len(persons[:10]))
    #     ])
    # ])
    x = persons['count']
    a = 10
    b = 30
    persons['count_norm'] = a + (x - x.min()) * (b - a) / (x.max() - x.min())
    persons = persons[['names', 'count_norm', 'count']].to_numpy()
    wordcloud = DashWordcloud(id='wordcloud',
                              list=persons,
                              width=700, height=600,
                              gridSize=16,
                              color='#f0f0c0',
                              backgroundColor='#001f00',
                              shuffle=False,
                              rotateRatio=0.5,
                              shrinkToFit=True,
                              shape='circle',
                              hover=True,
                              )

    return html.Div(children=[wordcloud, table])


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
