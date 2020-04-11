# Design Notes

## Thread count performance evaluation

Test data consists of 18 bands and 203 artists.

    1349/5575
    Amputation/14401
    Burzum/88
    Carpathian_Forest/147
    Darkthrone/146
    Demonaz/3540325611
    Dimmu_Borgir/69
    Emperor/30
    Enslaved/104
    Gehenna/2155
    Gorgoroth/770
    Ihsahn/60496
    Immortal/75
    Mayhem/67
    Old_Funeral/3969
    Satyricon/341
    Thorns/1131
    Zyklon-B/1421

Time (in min) to add data into empty database:

|Threads|Run 1|Run 2|Run 3|Avg.|Factor\*|
|---|---|---|---|---|---|
|1|4:00|5:18|3:45|4:20|1|
|2|1:56|1:56|1:55|1:56|2.24|
|4|1:13|1:17|1:12|1:14|3.51|
|8|0:49|0:49|0:53|0:50|5.2|

\* Times faster than baseline with one thread.

