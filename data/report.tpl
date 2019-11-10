<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>metal metal mapper reports</title>
        <link rel="stylesheet" href="w3.css">
    </head>
    <body class="mw-dark-blood">
        <div class="w3-container mw-blood">
            <h1>meta metal mapper reports</h1>
        </div>

        <div class="w3-container mw-dark-blood">
             <div class="w3-bar">
                <button class="w3-button mw-blood" onclick="displayRelease(releases_per_year)">Releases (per year)</button>
                <button class="w3-button mw-blood" onclick="displayReleaseAll(releases_all)">Releases (all)</button>
            </div>
        </div>
        
        <div id="metalData"></div>

        <script>

            var release_link = 'https://www.metal-archives.com/albums/'
            var releases_per_year = marker_releases_year
            var releases_all = marker_releases_all

            function displayRelease(data) {
                var mainContainer = document.getElementById("metalData");
                mainContainer.innerHTML = "";
                mainContainer.className ="w3-container"
                
                // TODO: Refactor this into a variable of its own.
                // The first element always contains the available release types.
                amount_release_types = data[0].categories.length;

                for (var i = 1; i < data.length - 1; i++) {
                    var div_outer = document.createElement("div");
                    div_outer.innerHTML = '<h2>' + data[i].year + '</h2>';
                    mainContainer.appendChild(div_outer);
                    var row = document.createElement("div");
                    row.className = "w3-row";
                    mainContainer.appendChild(row);

                    // Construct the columns, each containing an ordered list.
                    for (key in data[i]) {
                        if (key === "year") {continue;}
                        var column = document.createElement("div");
                        column.className = "w3-col m4 l4";
                        row.appendChild(column);
                        // Add the release category on top.
                        column.innerHTML = '<h3>' + key + '</h3>';
                        var list = document.createElement("ol");
                        column.appendChild(list);
                        releases = data[i];

                        for (var k = 0; k < releases[key].length; k++) {
                            var list_element = document.createElement("li");
                            var link = '"' + release_link + releases[key][k].link + '"';
                            list_element.innerHTML = '<a href=' + link + '>' + releases[key][k].name + '</a> (' + releases[key][k].rating + '%) by ' + releases[key][k].band;
                            list.appendChild(list_element);
                        }
                    }
                }
            }

            function displayReleaseAll(data) {
                var mainContainer = document.getElementById("metalData");
                mainContainer.innerHTML = "";
                mainContainer.className ="w3-container"
                
                // TODO: Refactor this into a variable of its own.
                amount_release_types = 3;

                var div_outer = document.createElement("div");
                div_outer.innerHTML = '<h2>All releases by rating</h2>';
                mainContainer.appendChild(div_outer);
                var row = document.createElement("div");
                row.className = "w3-row";
                mainContainer.appendChild(row);

                // Construct the columns, each containing an ordered list.
                for (key in data) {
                    var column = document.createElement("div");
                    column.className = "w3-col m4 l4";
                    row.appendChild(column);
                    // Add the release category on top.
                    column.innerHTML = '<h3>' + key + '</h3>';
                    //var list = document.createElement("ol");
                    //column.appendChild(list);
                    releases = data;

                    for (var k = 0; k < releases[key].length; k++) {
                        var list_element = document.createElement("div");
                        var link = '"' + release_link + releases[key][k].link + '"';
                        list_element.innerHTML = releases[key][k].rank + '. <a href=' + link + '>' + releases[key][k].release_name + '</a> (' + releases[key][k].ratings + '%) by ' + releases[key][k].band_name;
                        column.appendChild(list_element);
                        //list.appendChild(list_element);
                    }

                    mainContainer.appendChild(column);
                }
            }

        </script>
    </body>
</html>
