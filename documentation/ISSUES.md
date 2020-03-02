# Known Issues

* `PLAYED_IN` relationships are be overwritten with the last one found. An artist, which was a regular
    band member and helped out live in the past will be considered to be "only" `PL` [past (live)]. 
* The hierarchy of the instrument structure for artists may be in the wrong order.

## Starting Neo4j Appimage on Linux

If the Neo4j Appimage does not start the desktop window, check the console log for:

    The name org.freedesktop.secrets was not provided by any .service files
    
Installation of the gnome-keyring helped me in that case:

    sudo apt install gnome-keyring

## Library Hack

While crawling band links on Windows I encountered a defect in `Lib/http/client.py`. The percent escaped characters were
not resolved correctly. The solution for me was to change `putrequest()` (before `self._output()` is called). The line
looks like this:

    url = rfc3986.uri_reference(url).unsplit()
    
This hack needs to import `rfc3986` to function.