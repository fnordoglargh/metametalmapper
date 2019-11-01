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
            <h1>metal metal mapper reports</h1>
        </div>

        <div class="w3-container mw-dark-blood">
             <div class="w3-bar">
                <button class="w3-button mw-blood" onclick="appendData(releases)">Releases</button>
                <button class="w3-button mw-blood" onclick="appendData(countries)">Countries</button>
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
        </script>
    </body>
</html>
