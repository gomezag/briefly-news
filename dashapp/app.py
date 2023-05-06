import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from database.xata_api import XataAPI
from datetime import datetime
from llm.utils import get_related_people
from dash_holoniq_wordcloud import DashWordcloud
import pandas as pd

# Initialize the app
app = dash.Dash(__name__)
xata = XataAPI()

DEFAULT_START_DATE='2023-05-01'
DEFAULT_END_DATE='2023-05-05'

# Define the layout of the app
app.layout = html.Div([
    html.H1('Hello, World!'),
    html.Div(id="title_search_group", children=[
        dcc.Input(id='title_search', type='text', placeholder='Search in headlines'),
    ]),
    html.Div(id="date_search_group", children=[
        dcc.DatePickerRange(id='date_search', start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE),
    ]),
    html.Button("Buscar", id="search"),
    dcc.Dropdown(options=[{'label':'ABC Color', 'value':'abc'},
                          {'label':'La Nación Py', 'value':'lanacion'},
                          {'label':'Todos', 'value':'all'}], id='sel_site', value='all'),
    html.Div(id='result_table'),

])

@app.callback(
    Output("result_table", "children"),
    [Input("search", "n_clicks"),
     State('title_search', 'value'),
     State('date_search', 'start_date'),
     State('date_search', 'end_date'),
     State('sel_site', 'value')]
)
def update_results(btn, text, start_date, end_date, site):
    query = {}
    date_q = {}
    if start_date:
        st_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        st_date = datetime.strptime(DEFAULT_START_DATE, '%Y-%m-%d')
    date_q['$gt'] = st_date
    if end_date:
        ed_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        ed_date = datetime.strptime(DEFAULT_END_DATE, '%Y-%m-%d')
    date_q['$lt'] = ed_date
    query['date'] = date_q
    if text:
        query['title'] = {'$contains': text}
                         #{'title':{'$contains': text.lower()}},
                         #{'title':{'$contains': text.capitalize()}}
                         #]
    if site:
        if site != 'all':
            query['publisher.publisher_name'] = site
        else:
            query.pop('publisher.publisher_name', None)
    chunks = 0
    more = True
    cursor = None
    persons = pd.DataFrame()
    links = []
    while chunks < 1000 and more:
        cquery = dict(
            filter=query,
            page={'after': cursor, 'size': 20},
            sort={'date': 'desc'}
        )

        if cursor:
            cquery.pop('sort', None)
            cquery.pop('filter', None)

        res = xata.query('news_article', **cquery)
        articles = res['records']
        pers, lin = get_related_people(articles)
        persons = pd.concat([persons, pers], ignore_index=True, sort=False)
        links.extend(lin)
        if res.get('meta', {}).get('page', {}).get('more', False):
            more = True
            chunks += 1
            cursor = res["meta"]["page"]["cursor"]  # save next cursor for results
        else:
            more = False

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

    return html.Div(children=[html.Div(f"Articulos encontrados: {len(links)}"),
                              wordcloud,
                              table])


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
