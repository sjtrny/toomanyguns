from flask import Flask
from multipage import Route, MultiPageApp
from index import Index
from about import About


class MyApp(MultiPageApp):
    def get_routes(self):

        return [
            Route(Index, "index", "/"),
            Route(About, "about", "/about/"),
        ]

server = Flask(__name__)

app = MyApp(name=__name__, server=server, url_base_pathname="")

if __name__ == "__main__":
    server.run(host="0.0.0.0", debug=True)
