if (!window.dash_clientside) {
     window.dash_clientside = {}
 }

window.dash_clientside.clientside = {

    figure: function (fig_data, postcode) {

        if (!fig_data) {
            throw "Figure data not loaded, aborting update."
        }

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
            postcode_features = fig_data["geojson"]['features'].find(function (v) {
                return v["properties"]["POA_CODE16"] == postcode
            });

            zoom = postcode_features['properties']["zoom"];
            center = postcode_features['properties']["centroid"];
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
            fig_data["showscale"] = false;
            delete fig_data["colorbar"]
        }

        return {
            data: [fig_data],
            layout: fig_layout,
        }

    },

}