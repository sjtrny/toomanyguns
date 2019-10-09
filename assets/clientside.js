if (!window.dash_clientside) {
     window.dash_clientside = {}
 }

window.dash_clientside.clientside = {

    figure: function (all_data, postcode) {

        if (!all_data) {
            throw "Figure data not loaded, aborting update."
        }

        fig_dict = {
                type: "choroplethmapbox",
                geojson: all_data["geojson"],
                locations: all_data["locations"],
                z: all_data["z"],
                text: all_data["text"],
                hoverinfo: "text",
                colorscale:  "Viridis",
                colorbar: {title: "Firearms"},
                marker: {opacity:0.5, line:{width:1}}
        };


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

            fig_data = [fig_dict]
        }
        else {
            postcode_features_idx = all_data["geojson"]['features'].findIndex(function (v) {
                return v["properties"]["POA_CODE16"] == postcode
            });

            postcode_features = all_data["geojson"]['features'][postcode_features_idx];

            zoom = postcode_features['properties']["zoom"];
            center = postcode_features['properties']["centroid"];
            firearms = postcode_features["properties"]["Registered Firearms"];

            new_layer = {
                type: "choroplethmapbox",
                geojson: postcode_features,
                locations: [postcode_features["properties"]["POA_CODE16"]],
                z: [1],
                text: `Postcode: ${postcode}<br>Firearms: ${firearms}`,
                hoverinfo: "text",
                colorscale:  [
                    ['0.0', 'rgb(255,166,36)'],
                    ['1.0', 'rgb(255,166,36)'],
                ],
                marker: {opacity:0.5, line:{width:5, color:'rgb(255,166,36)'}},
                showscale: false,
            }

            fig_dict["locations"] = all_data["locations"].filter((value, index) => (postcode_features_idx-1) !== index);

            fig_data = [fig_dict, new_layer]
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
            fig_data[0]["showscale"] = false;
            delete fig_data[0]["colorbar"]
        }

        return {
            data: fig_data,
            layout: fig_layout,
        }

    },

}