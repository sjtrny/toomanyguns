from common import MarkdownApp
import flask

class About(MarkdownApp):

    title = "About"
    breadcrumbs = None

    markdown = """
## About

This website shows firearms ownership in NSW by postcode.

This information has been made public thanks to the NSW Greens through a FOI request to NSW Police. 
    
## FAQ

##### Doesn't toomanyguns.org already exist?

Yes, but it could be better, so we made our own.

##### This doesn't work on my computer/browser?

It's best viewed on a modern browser such as Safari or Chrome with graphics acceleration enabled.

##### How did you make this?

This website is built on [Dash for Python](https://github.com/plotly/dash) by Plotly.

You can find the code on [Github](https://github.com/sjtrny/toomanyguns)

##### Who made this?

I did, you can find more details on my website [sjtrny.com](https://sjtrny.com)

## Data

##### Postcode Information

Sourced from [https://www.matthewproctor.com/australian_postcodes](https://www.matthewproctor.com/australian_postcodes)

##### Postal Area Geography Data

This information is available from the ABS under the listing [1270.0.55.003 - Australian Statistical Geography Standard (ASGS): Volume 3 - Non ABS Structures, July 2016](https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/1270.0.55.003July%202016?OpenDocument)

The specific file used is titled "Postal Areas ASGS Ed 2016 Digital Boundaries in ESRI Shapefile Format"

##### Firearms Data

We did our best to scrape [http://toomanyguns.org](http://toomanyguns.org).

Don't worry, you don't need to scrape it yourself, [click here to download it](downloads/firearms_2019.csv).
    """

    def postlayout_setup(self):

        @self.server.route(
            f"{self.config.url_base_pathname}downloads/firearms_2019.csv",
            endpoint=f"{self.config.url_base_pathname}:serve_file"
        )
        def serve_file():
            return flask.send_file(
                "firearms_2019.csv",
                as_attachment=True,
            )