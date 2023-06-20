import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from database.xata_api import XataAPI
from datetime import datetime, timedelta, time
from dash_holoniq_wordcloud import DashWordcloud

xata = XataAPI()


def init_dashboard(server):

    # Initialize the app
    app = dash.Dash(server=server,
                    url_base_pathname='/')


    DEFAULT_START_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')
    loading_style = {'position': 'absolute', 'align-self': 'center'}

    # Define the layout of the app
    app.layout = html.Div([
        html.Script(src="/_vercel/insights/script.js", defer=True),
        html.H1("What's going on man!", className='title is-1'),
        html.Div(className='container main', children=[
            html.Div(className='box', children=[
                html.Div(className='columns', children=[
                    # html.Div(className='column is-one-third', id='formCol', children=[
                    #
                    # ]),
                    html.Div(className='column', id='app-column', children=[
                        dcc.Tabs(id='view-tab', value='filter', children=[
                            dcc.Tab(label='Filtro', value='filter', children=[
                                html.Div(className='columns', children=[
                                    html.Div(className='column', children=[
                                        html.Div(className='container', children=[
                                            html.H3('Búsqueda:', className='title is-3 center'),
                                            html.Div(id="search-form", className='form', children=[
                                                html.Div(className="field is-grouped", children=[
                                                    html.Label('Título: ', className='control label'),
                                                    html.Div(className='control', children=[
                                                        dcc.Input(id='title_search',
                                                                  type='text',
                                                                  placeholder='Search in headlines',
                                                                  className='input')
                                                    ]),
                                                ]),
                                                html.Div(className="field is-grouped", children=[
                                                    html.Label('Cuerpo: ', className='control label'),
                                                    html.Div(className='control', children=[
                                                        dcc.Input(id='body_search',
                                                                  type='text',
                                                                  placeholder='Search in headlines',
                                                                  className='input')
                                                    ]),
                                                ]),
                                                html.Div(className="field is-grouped", children=[
                                                    html.Label('URL: ', className='control label'),
                                                    html.Div(className='control', children=[
                                                        dcc.Input(id='url_search',
                                                                  type='text',
                                                                  placeholder='Search in headlines',
                                                                  className='input')
                                                    ]),
                                                ]),
                                                html.Div(className="field is-grouped", children=[
                                                    html.Label('Nombre: ', className='control label'),
                                                    html.Div(className='control', children=[
                                                        dcc.Input(id='poi_search',
                                                                  type='text',
                                                                  placeholder='Search for POI',
                                                                  className='input')
                                                    ]),
                                                ]),
                                                html.Div(id="date_search_group",
                                                         className='field is-grouped is-centered',
                                                         children=[
                                                             html.Label("Fecha: ", className='control label'),
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
                                                                     {'label': 'UltimaHora', 'value': 'ultimahora'},
                                                                     {'label': '5Dias', 'value': 'cincodias'},
                                                                     {'label': 'Todos', 'value': 'all'}],
                                                            id='sel_site', value='all')
                                                    ]),

                                                ]),
                                                html.Div(className='field is-grouped', children=[
                                                    html.Div('Limite: ', className='control label'),
                                                    html.Div(className='control', children=[
                                                        dcc.Input(type='number',
                                                                  min=1,
                                                                  id='limit',
                                                                  className='control input',
                                                                  value=500)
                                                    ])
                                                ]),
                                            ]),
                                            dcc.Loading(id='encontrados-loading', className='gifloader', children=[
                                                html.H4(id='encontrados', className='is-4 center'),
                                            ]),
                                            dcc.Loading(id='searchbtn-loading', className='gifloader', type='default',
                                                        children=[
                                                            html.Button("Buscar", id="search",
                                                                        className='button is-info')
                                                        ])
                                        ]),
                                    ]),
                                    html.Div(className='column', children=[
                                        html.Div(id='resumen', children=[]),
                                    ])
                                ])
                            ]),
                            dcc.Tab(label='Nombres', value='poi', children=[
                                html.Div(className='columns', children=[
                                    html.Div(className='column', id='wordcloudCol', children=[
                                        dcc.Loading(id='wordcloud-loading', className='gifloader', children=[
                                            DashWordcloud(id='wordcloud',
                                                          list=[],
                                                          width=550, height=471,
                                                          gridSize=16,
                                                          color='#f0f0c0',
                                                          backgroundColor='#001f00',
                                                          shuffle=False,
                                                          rotateRatio=0.5,
                                                          shrinkToFit=True,
                                                          shape='circle',
                                                          hover=True
                                                          ), ]),
                                    ]),
                                    html.Div(className='column', id='infoCol',
                                             children=[
                                                 dcc.Loading(id='table-loading2', className='gifloader', children=[
                                                     html.Div(id='clicktable',
                                                              className='clicktable',
                                                              children=[html.H3('', id='whoisname',
                                                                                className='title is-3',
                                                                                hidden=True),
                                                                        html.Button('', id='whois', hidden=True)
                                                                        ]
                                                              )
                                                 ]),
                                             ]),
                                ])
                            ]),
                            dcc.Tab(label='Chat', value='chat', children=[
                                html.Div(className='chat', id='askFormCol', children=[
                                    html.Div(className='chat-output',
                                             id='askResults',
                                             children=[
                                                 dcc.Loading(id='askrelated-loading', className='gifloader', children=[
                                                     html.Div(id='answer', children=[]),
                                                     html.Div(id='askrelated', children=[]),
                                                 ]),
                                             ]),
                                    html.Div(className='chat-input', children=[
                                        html.Div(className="control chat-prompt", children=[
                                            dcc.Input(id='question',
                                                      type='text',
                                                      placeholder='Preguntar algo',
                                                      className='input')
                                        ]),
                                        dcc.Loading(id='askbtn-loading',
                                                    type='circle',
                                                    children=[
                                                        html.Button("Preguntar", id="ask",
                                                                    className='button is-info'
                                                                    )
                                                    ]),
                                        html.Div(className='control is-grouped', children=[
                                            html.Div(className='control dropdown', children=[
                                                dcc.RadioItems(
                                                    options=[{'label': 'Vector', 'value': 'vector'},
                                                             {'label': 'Keyword', 'value': 'keyword'}],
                                                    id='ask_type', value='keyword', )
                                            ]),

                                        ]),
                                    ]),

                                ]),

                            ]),
                            dcc.Tab(label='Stats', value='stats', children=[
                                html.Div(className='column', id='resumen_graph', children=[
                                    dcc.Graph(id='article_timeline', className='stats-graph'),
                                ]),
                                html.Div(className='column', id='related_graph', children=[]),
                            ]),
                        ])
                    ]),

                ]),
            ]),
            dcc.Loading(id='table-loading', className='gifloader', children=[
                html.Div(id='result_table', className='resulttable', children=[]),
            ]),
        ]),
        dcc.Interval(id='heartbeat', interval=10 * 1000, n_intervals=0),
        # dcc.Loading(id='poinet-loading', className='gifloader', children=[
        #     dcc.Graph(id='poi-net')
        # ]),

        dcc.Store(id='articles'),
        dcc.Store(id='sites', data={
            'abc': xata.query('news_publisher', filter={'publisher_name': 'abc'})['records'][0]['id'],
            'lanacion': xata.query('news_publisher', filter={'publisher_name': 'lanacion'})['records'][0]['id'],
            'cincodias': xata.query('news_publisher', filter={'publisher_name': 'cincodias'})['records'][0]['id'],
            'ultimahora': xata.query('news_publisher', filter={'publisher_name': 'ultimahora'})['records'][0]['id']
        }),
        dcc.Store(id='whois-action', data=True),
        dcc.Store(id='filter', data={})
    ])
    init_callbacks(app)
    return app.server


def init_callbacks(app):
    @app.callback(
        Output("related_graph", "children"),
        Input("article_timeline", "clickData"),
    )
    def graph_click(clickData):

        return [str(clickData)]

    @app.callback(
        [Output('answer', 'children'),
         Output('askrelated', 'children'),
         Output('ask', 'children')],
        [Input('ask', 'n_clicks'),
         Input('whois-action', 'data'),
         State('question', 'value'),
         State('ask_type', 'value'),
         State('title_search', 'value'),
         State('date_search', 'start_date'),
         State('date_search', 'end_date'),
         Input('sel_site', 'value'),
         State('limit', 'value'),
         State('body_search', 'value'),
         State('url_search', 'value'),
         State('sites', 'data'),]
    )
    def ask_table(n, m, question, ask_type, title, start_date, end_date, site, limit, body, url_search, sites):
        if n or m:
            fquestion = f"La pregunta es: '{question}'. \n Fin de la pregunta. " \
                        f"Responde la pregunta de arriba , en castellano. \n Considera que la fecha de hoy es " \
                        f"{datetime.now().strftime('%Y-%m-%d')}." \
                        f"Se lo mas detallado posible."
            parms = {'question': fquestion, 'searchType': ask_type}
            query = {}
            date_q = {}
            if start_date:
                st_date = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                DEFAULT_START_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                st_date = datetime.strptime(DEFAULT_START_DATE, '%Y-%m-%d')
            date_q['$gt'] = st_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            if end_date:
                ed_date = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')
                ed_date = datetime.strptime(DEFAULT_END_DATE, '%Y-%m-%d')
            date_q['$lt'] = ed_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            query['date'] = date_q
            if site:
                if site != 'all':
                    query['publisher'] = sites[site]
                else:
                    query.pop('publisher', None)
            if title:
                query['title'] = {'$contains': title}
                # {'title':{'$contains': text.lower()}},
                # {'title':{'$contains': text.capitalize()}}
                # ]
            if body:
                query['article_body'] = {'$contains': body}
            if url_search:
                query['url'] = {'$contains': url_search}
            if ask_type == 'vector':
                parms['vectorSearch'] = {'column': 'embedding', 'contentColumn': 'article_body', 'filter': query}
            else:
                parms['search'] = {'filter': query}
            res = xata.client.search_and_filter().askTable('news_article', parms)
            if res.status_code == 200:
                res = res.json()
                answer = res['answer']
                id_articles = res['records']
                articles = [xata.read('news_article', id_art) for id_art in id_articles]

                result = []
                for article in articles:
                    result.append(html.Li(children=[
                        article['date'][:10] + ': ',
                        html.A(article['title'], href=article['url']),
                        html.P(f"({article['id']})")
                    ]))

                return answer, result, 'Preguntar'
            else:
                return res.json()['message'], None, 'Preguntar'
        return None, None, 'Preguntar'


    @app.callback(
        [Output('resumen', 'children')],
        [Input('heartbeat', 'n_intervals'),
         State('filter', 'data'), State('sites', 'data')]
    )
    def update_summary(n, query, sites):
        qfilter = query.copy()
        publisher = qfilter.pop('publisher.publisher_name', None)
        if publisher:
            qfilter['publisher'] = sites[publisher]
        date = qfilter.pop('date', None)
        query = {
            'aggs': {'total': {'count': "*"}
                     }
        }
        if qfilter != {}:
            query.update({'filter': qfilter})
        res = xata.client.search_and_filter().aggregateTable('news_article', query)
        data = res.json()
        total_articles = data["aggs"]["total"]
        if date:
            qfilter['date'] = {}
            end_date = datetime.strptime(date['$lt'], '%Y-%m-%d')

            qfilter['date']['$lt'] = end_date.strftime('%Y-%m-%dT%H:%M:%SZ%z')
            qfilter['date']['$gt'] = datetime.strptime(date['$gt'], '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%SZ%z')
            query.update({'filter': qfilter})
            res = xata.client.search_and_filter().aggregateTable('news_article', query)
            data = res.json()
            on_date_articles = data["aggs"]["total"]
        else:
            on_date_articles = '...'
        results_children = [
            html.Div(className='container', children=[
                html.H3(className='title is-3', children=[f'Total (todas las fechas): {total_articles}']),
                html.H3(className='title is-3', children=[f'Total en fecha: {on_date_articles}']),
                #html.H3(className='title is-3', children=[f'Artículos con tags: {tagged_articles} ']),
                #html.H3(className='title is-3', children=[f'Artículos con embedding: {embedded_articles} ']),
                #html.H3(className='title is-3', children=[f'Gastado en embedding*: {round(total_cost, 2)} $']),
            ])
        ]
        return results_children


    @app.callback(
        [Output('article_timeline', 'figure')],
        [Input('heartbeat', 'n_intervals'), State('article_timeline', 'relayoutData'), State('filter', 'data'),
         State('sites', 'data')]
    )
    def update_statistics(n, zoom_info, fquery, sites):
        qfilter = fquery.copy()
        qfilter.pop('date', None)
        qfilter.pop('POIs', None)
        graphs = []
        total_articles = 0
        for site in ['abc', 'lanacion', 'ultimahora', 'cincodias']:
            siteid = sites[site]
            if site == 'abc':
                for source in ['abccolor', 'EFE']:
                    query = {
                        'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}},
                                 'total': {'count': '*'}},
                    }
                    if source == 'EFE':
                        query['filter'] = {'source': source}
                    else:
                        query['filter'] = {'$not': {'source': 'EFE'}}
                    if qfilter:
                        query['filter'].update(qfilter)
                    res = xata.client.search_and_filter().aggregateTable('news_article', query)
                    if res.status_code == 200:
                        data = res.json()['aggs']['byDay']['values']
                        total_articles += res.json()['aggs']['total']
                        for d in data:
                            d['$key'] = datetime.strptime(d['$key'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        x = [d['$key'] for d in data]
                        y = [d['$count'] for d in data]
                        graphs.append(dict(x=x, y=y, type='bar', name=source))
                    else:
                        print(res.text)
                        pass
            else:
                qfilter.update({'publisher': siteid})
                query = {
                    'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}},
                             'total': {'count': '*'}}
                }
                if qfilter:
                    query.update({'filter': qfilter})
                res = xata.client.search_and_filter().aggregateTable('news_article', {
                    'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}},
                             'total': {'count': '*'}},
                    'filter': {
                        'publisher': siteid
                    }})
                if res.status_code == 200:
                    data = res.json()['aggs']['byDay']['values']
                    if len(data) > 0:
                        total_articles += res.json()['aggs']['total']
                        for d in data:
                            d['$key'] = datetime.strptime(d['$key'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        x = [d['$key'] for d in data]
                        y = [d['$count'] for d in data]
                        graphs.append(dict(x=x, y=y, type='bar', name=site))
                else:
                    print(res.text)
                    pass
        #
        # for field in ['embedding', 'POIs']:
        #     res = xata.client.search_and_filter().aggregateTable('news_article', {
        #         'aggs': {'byDay': {'dateHistogram': {'column': 'date', 'calendarInterval': 'day'}}},
        #         'filter': {'$exists': field}
        #     })
        #     data = res.json()['aggs']['byDay']['values']
        #     for d in data:
        #         d['$key'] = datetime.strptime(d['$key'], '%Y-%m-%dT%H:%M:%S.%fZ')
        #     x = [d['$key'] for d in data]
        #     y = [d['$count'] for d in data]
        #     graphs.append(dict(x=x, y=y, type='bar', name=field, base=0, opacity=0.5))

        fig = {
            'data': graphs,
            'layout': {
                'title': 'Conteo de Artículos',
                'barmode': 'stack',
                'xaxis': {
                    'range': [datetime.now() - timedelta(days=30), datetime.now()],
                    'rangeSlider': True
                },
                'yaxis': {},
            }
        }
        if zoom_info:
            for axis_name in ['axis', ]:
                if f'x{axis_name}.range[0]' in zoom_info:
                    fig['layout'][f'x{axis_name}']['range'] = [
                        zoom_info[f'x{axis_name}.range[0]'],
                        zoom_info[f'x{axis_name}.range[1]']
                    ]
                if f'y{axis_name}.range[0]' in zoom_info:
                    fig['layout'][f'y{axis_name}']['range'] = [
                        zoom_info[f'y{axis_name}.range[0]'],
                        zoom_info[f'y{axis_name}.range[1]']
                    ]
        if fig:
            fig['layout']['uirevision'] = '1'
            return [fig]
        else:
            return []


    @app.callback(
        [Output('result_table', 'children')],
        [Input('articles', 'data'),
         State('sites', 'data')]
    )
    def update_results_table(articles, sites):
        rows = []
        for article in articles:
            row = []
            for key in ['date', 'title', 'subtitle', 'url', 'authors']:
                if key == 'url':
                    try:
                        site = [key for key, value in sites.items() if value == article['publisher']['id']][0]
                    except:
                        site = article['publisher']
                    cell = html.Td(html.A(str(site), href=article[key]))
                elif key == 'authors':
                    cell = html.Td(", ".join(article[key]))
                else:
                    cell = html.Td(article[key])
                row.append(cell)
            rows.append(html.Tr(children=row))
        children = [html.Th(key) for key in ['Fecha', 'Titular', 'Resumen', 'URL', 'Autores', 'Sitio']]
        children.extend(rows)
        table = html.Table(children=children, className='table')
        return [table]


    @app.callback(
        [Output('filter', 'data')],
        [
         Input('title_search', 'value'),
         Input('date_search', 'start_date'),
         Input('date_search', 'end_date'),
         Input('sel_site', 'value'),
         Input('body_search', 'value'),
         Input('url_search', 'value'),
         Input('poi_search', 'value')]
    )
    def update_filter(text, start_date, end_date, site, body, url_search, poi):
        query = {}
        date_q = {}
        if start_date:
            st_date = start_date
        else:
            st_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        date_q['$gt'] = st_date
        if end_date:
            ed_date = end_date
        else:
            ed_date = datetime.now().strftime('%Y-%m-%d')
        date_q['$lt'] = ed_date
        query['date'] = date_q
        if text:
            query['title'] = {'$contains': text}
            # {'title':{'$contains': text.lower()}},
            # {'title':{'$contains': text.capitalize()}}
            # ]
        if body:
            query['article_body'] = {'$contains': body}
        if site:
            if site != 'all':
                query['publisher.publisher_name'] = site
            else:
                query.pop('publisher.publisher_name', None)

        if url_search:
            query['url'] = {'$contains': url_search}
        if poi:
            query['POIs'] = {'$includes': poi}
        return [query]


    @app.callback(
        [Output("encontrados", "children"),
         Output('articles', 'data'),
         Output('search', 'children')],
        [Input("search", "n_clicks"),
         State('filter', 'data'),
         State('limit', 'value')]
    )
    def update_articles(btn, query, limit):
        try:
            query['date']['$lt'] = datetime.strptime(query['date']['$lt'], '%Y-%m-%d')
            query['date']['$gt'] = datetime.strptime(query['date']['$gt'], '%Y-%m-%d')
        except KeyError:
            query['date'] = {'$lt': datetime.now(),
                             '$gt': datetime.now()-timedelta(days=1)}
        chunks = 0
        more = True
        cursor = None
        articles = []
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
            articles.extend(res['records'])
            if res.get('meta', {}).get('page', {}).get('more', False):
                more = True
                chunks += 1
                if limit:
                    if chunks * 20 >= limit:
                        more = False
                cursor = res["meta"]["page"]["cursor"]  # save next cursor for results
            else:
                more = False

        return f"Articulos encontrados: {len(articles)}", articles, 'Buscar'


    @app.callback(
        [Output('wordcloud', 'list')],
        [Input('articles', 'data')]
    )
    def update_wordcloud(articles):
        persons = articles.copy()
        if 'POIs' in [key for article in persons for key in article]:
            poi_counts = {}
            for article in persons:
                pois = article.get('POIs')
                if pois:
                    for poi in pois:
                        if poi in poi_counts:
                            poi_counts[poi] += 1
                        else:
                            poi_counts[poi] = 1

            persons = []
            for poi, count in poi_counts.items():
                persons.append({'POIs': poi, 'count': count})

            persons.sort(key=lambda x: x['count'], reverse=True)
            x = [person['count'] for person in persons]
            a = 10
            b = 30
            x_min = min(x)
            x_max = max(x)
            persons_norm = []
            for person in persons:
                count_norm = a + (person['count'] - x_min) * (b - a) / (x_max - x_min + 1)
                person['count_norm'] = count_norm
                person['label'] = str(person['POIs']) + ' - ' + str(person['count'])
                persons_norm.append([person['POIs'], person['count_norm'], person['label']])

            bpersons = persons_norm
        else:
            bpersons = []

        return [bpersons]


    @app.callback(
        Output('clicktable', 'children'),
        [Input('wordcloud', 'click'),
         State('articles', 'data')]
    )
    def wordcloud_click(clickdata, articles):
        if clickdata:
            name = clickdata[0]
            result = []
            for article in articles:
                if name in article.get('POIs', []):
                    result.append(html.Li(children=[
                        article['date'][:10] + ': ',
                        html.A(article['title'], href=article['url'])]))
            return html.Div(children=[html.Div(children=[html.H3(name, id='whoisname', className='title is-3'),
                                                         html.Button('Quién es?', className='button is-info', id='whois'),
                                                         ],
                                               className='wordcloud-info-panel'),
                                      html.Div(children=result)
                                      ])
        else:
            return ['']


    @app.callback(
        [Output('whois-action', 'data'),
         Output('question', 'value'),
         Output('view-tab', 'value')],
        [Input('whois', 'n_clicks'), State('whoisname', 'children'), State('whois-action', 'data'),
         State('view-tab', 'value')]
    )
    def whois(n, name, m, tab):
        if n:
            return True, f"Quien es {name}?", 'chat'
        return False, '', tab
