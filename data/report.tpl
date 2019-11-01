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
                <button class="w3-button mw-blood" onclick="appendData(releases)">Test 1</button>
                <button class="w3-button mw-blood" onclick="appendData(countries)">Test 2</button>
                <button class="w3-button mw-blood" onclick="displayRelease(releases_per_year)">Releases (per year)</button>
            </div>
        </div>
        
        <div id="myData"></div>
        <script>
            var release_link = 'https://www.metal-archives.com/albums/'
            var releases = [{
                "year": 1991,
                "releases": [{
                    "id": "1",
                    "release_name": "Soulside Journey",
                    "rating": 87,
                    "band_name": "Darkthrone",
                    "short_link": "Soulside_Journey/441258"
                }]
            }]

            var countries = [{
                "year": 1991,
                "releases": [{
                    "id": "1",
                    "release_name": "Test",
                    "rating": 87,
                    "band_name": "Darkthrone",
                    "short_link": "Soulside_Journey/441258"
                }]
            }]

            var releases_per_year = marker_releases

            function appendData(data) {
                var mainContainer = document.getElementById("myData");
                mainContainer.innerHTML = ""

                for (var j = 0; j < data.length; j++) {
                    var div_outer = document.createElement("div");
                    div_outer.innerHTML = '<h1>' + data[j].year + '</h1>'
                    mainContainer.appendChild(div_outer);
                    var list = document.createElement("ol");
                    mainContainer.appendChild(list);
                    for (var i = 0; i < data[j].releases.length; i++) {
                        console.log(i)
                        var div = document.createElement("li");
                        var link = '"' + release_link + data[j].releases[i].band_name + '/' + data[j].releases[i].short_link + '"';
                        div.innerHTML = '<a href=' + link + '>' + data[j].releases[i].release_name + '</a> (' + data[j].releases[i].rating + '%) by ' + data[j].releases[i].band_name;
                        list.appendChild(div);
                    }
                }
            }

            function displayRelease(data) {
                var mainContainer = document.getElementById("myData");
                mainContainer.innerHTML = "";

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
                        column.innerHTML = '<h3>' + key+ '</h3>';
                        var list = document.createElement("ol");
                        column.appendChild(list);
                        releases = data[i];

                        for (var k = 0; k < releases[key].length; k++) {
                            console.log(k);
                            var list_element = document.createElement("li");
                            var link = '"' + release_link + releases[key][k].link + '"';
                            list_element.innerHTML = '<a href=' + link + '>' + releases[key][k].name + '</a> (' + releases[key][k].rating + '%) by ' + releases[key][k].band;
                            //list_element.innerHTML = releases[key][k].name;
                            list.appendChild(list_element);
                        }
                    }
                }
            }
        </script>
    </body>
</html>
