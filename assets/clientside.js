if (!window.dash_clientside) {
     window.dash_clientside = {}
 }

window.dash_clientside.clientside = {

    figure: function (all_data, postcode) {

        if (!all_data) {
            throw "Figure data not loaded, aborting update."
        }

        fig_data = [{...all_data}];

        bsBreakpoints.init();
        bp = bsBreakpoints.getCurrentBreakpoint();

        if (!postcode | postcode == "None") {

            if (bp == "small" | bp == "xSmall") {
                zoom = 4;
            }
            else {
                zoom = 5;
            }

            center = {"lat": -33, "lon": 146.9211};
        }
        else {
            postcode_features_idx = all_data["geojson"]['features'].findIndex(function (v) {
                return v["properties"]["POA_CODE16"] == postcode
            });

            postcode_features = all_data["geojson"]['features'][postcode_features_idx]

            zoom = postcode_features['properties']["zoom"];
            center = postcode_features['properties']["centroid"];

            new_layer = {
                type: "choroplethmapbox",
                geojson: postcode_features,
                locations: [postcode_features["properties"]["POA_CODE16"]],
                z: [1],
                colorscale:  [
                    ['0.0', 'rgb(255,166,36)'],
                    ['1.0', 'rgb(255,166,36)'],
                ],
                marker: {opacity:0.5, line:{width:5, color:'rgb(255,166,36)'}},
                showscale: false,
            }

            fig_data[0]["geojson"]['features'].splice(postcode_features_idx, 1)

            fig_data.push(new_layer)
        }

        fig_layout = {
            mapbox: {
                zoom: zoom,
                center: center,
                style: "streets",
            },

            margin: {r: 0, t: 0, l: 0, b: 0},
        };



        if (bp != "xLarge") {
            all_data["showscale"] = false;
            delete all_data["colorbar"]
        }

        return {
            data: fig_data,
            layout: fig_layout,
        }

    },

}