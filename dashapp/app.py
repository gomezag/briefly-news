import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from database.xata_api import XataAPI
from datetime import datetime, timedelta
from llm.utils import get_related_people
from dash_holoniq_wordcloud import DashWordcloud
import pandas as pd

# Initialize the app
app = dash.Dash(__name__)
xata = XataAPI()

DEFAULT_START_DATE = (datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')

# Define the layout of the app
app.layout = html.Div([
    html.H1("What's going on man!", className='title is-1'),
    html.Div(id='encontrados'),
    html.Div(className='columns', children=[
        html.Div(className='column', children=[
            html.Div(className='container', children=[
                html.Div(className="field is-grouped", children=[
                    html.Label('Title contains: ', className='control label'),
                    html.Div(className='control', children=[
                        dcc.Input(id='title_search',
                              type='text',
                              placeholder='Search in headlines',
                              className='input')
                    ]),
                ]),
                html.Div(className="field is-grouped", children=[
                    html.Label('Body contains: ', className='control label'),
                    html.Div(className='control', children=[
                        dcc.Input(id='body_search',
                              type='text',
                              placeholder='Search in headlines',
                              className='input')
                    ]),
                ]),
                html.Div(id="date_search_group", className='field is-grouped is-centered', children=[
                    html.Label("Fechas: ", className='control label'),
                    html.Div(className='control', children=[
                        dcc.DatePickerRange(id='date_search',
                                            start_date=DEFAULT_START_DATE,
                                            end_date=DEFAULT_END_DATE),
                    ]),
                ]),
                html.Div(className='field is-grouped', children=[
                    html.Div('Sitio: ', className='control label'),
                    html.Div(className='control dropdown', children=[
                        dcc.Dropdown(
                            options=[{'label': 'ABC Color', 'value': 'abc'},
                                     {'label': 'La Nación Py', 'value': 'lanacion'},
                                     {'label': 'Todos', 'value': 'all'}],
                            id='sel_site', value='all')
                    ]),

                ]),
                html.Div(className='field is-grouped', children=[
                        html.Div('Limit: ', className='control label'),
                        html.Div(className='control', children=[
                            dcc.Input(type='number',
                                      min=1,
                                      id='limit',
                                      className='control input',
                                      value=20)
                        ])

                ]),
                html.Button("Buscar", id="search", className='button is-info'),
            ]),

        ]),
        html.Div(className='column', children=[
            DashWordcloud(id='wordcloud',
                          list=[],
                          width=700, height=600,
                          gridSize=16,
                          color='#f0f0c0',
                          backgroundColor='#001f00',
                          shuffle=False,
                          rotateRatio=0.5,
                          shrinkToFit=True,
                          shape='circle',
                          hover=True
                          ),
        ]),
        html.Div(className='column', id='clicktable',
                 children=[
            html.Div('Hello')
        ]),

    ]),

    html.Div(id='result_table', children=[]),

    html.Div(id='sink', children=[])
])

@app.callback(
    [Output('clicktable', 'children')],
    [Input('wordcloud', 'click'),
     State('wordcloud', 'list')]
)
def onclick(clickdata, list):
    return [clickdata]


def wordcloud_hover(item, dimension, event):
    return True


@app.callback(
    [Output("encontrados", "children"),
     Output('wordcloud', 'list'),
     Output('result_table', 'children')],
    [Input("search", "n_clicks"),
     State('title_search', 'value'),
     State('date_search', 'start_date'),
     State('date_search', 'end_date'),
     State('sel_site', 'value'),
     State('limit', 'value'),
     State('body_search', 'value')]
)
def update_results(btn, text, start_date, end_date, site, limit, body):
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
    if body:
        query['article_body'] = {'$contains': body}
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
    while more:
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
            if limit:
                if chunks*20 >= limit:
                    more = False
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
                cell = html.Td(", ".join(article[key][:10]), className='cell')
            else:
                cell = html.Td(article[key])
            row.append(cell)
        rows.append(html.Tr(children=row))
    children = [html.Th(key) for key in ['Fecha', 'Titular', 'Resumen', 'URL', 'POIs']]
    children.extend(rows)
    table = html.Table(children=children, className='table')
    x = persons['count']
    a = 10
    b = 30
    persons['count_norm'] = a + (x - x.min()) * (b - a) / (x.max() - x.min())
    persons['label'] = persons['names'].astype(str) + ' - ' + persons['count'].astype(str)
    bpersons = persons[['names', 'count_norm', 'label']].to_numpy()

    return f"Articulos encontrados: {len(links)}", bpersons, table


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
