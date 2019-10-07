if (!window.dash_clientside) {
     window.dash_clientside = {}
 }

window.dash_clientside.clientside = {
    display: function (value) {
        return 'Client says "' + value + '"';
    },

    figure: function (value) {

        fig_div = document.getElementById("fig-data")
        if (!fig_div) {
            throw "Figure data not loaded, aborting update."
        }

        fig_data = JSON.parse(document.getElementById("fig-data").innerText);

        if (!value | value == "None") {
            zoom = 4;
            center = {"lat": -33, "lon": 146.9211};
        }
        else {
            postcode_features = fig_data["geojson"]['features'].find(function (v) {
                return v["properties"]["POA_CODE16"] == value
            });

            zoom = postcode_features['properties']["zoom"];
            center = postcode_features['properties']["centroid"];
        }

        fig_layout = {
            mapbox: {
                zoom: zoom,
                center: center,
                style: "light",
            },

            margin: {r: 0, t: 0, l: 0, b: 0},
        };

        return {
            data: [fig_data],
            layout: fig_layout,
        }

    }

}