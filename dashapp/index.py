from dash import Dash
from dashapp.app import app as dapp


class MainApplication:
    def __init__(self):
        self.__app = dapp

    @property
    def app(self):
        return self.__app


Application = MainApplication()
app = Application.app.server
