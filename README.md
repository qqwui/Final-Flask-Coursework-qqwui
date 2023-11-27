# Final Flask Coursework: Higher Education E-sports League
## Overview
I decided to do my coursework for my college. It is a way of organising colleges, their teams and arrange leagues.
The details are in the writeup, this document is a brief description how to view the project.
## Structure
The directory structure looks like this:
<pre>
(root)
   |
   |-private/
   |    |
   |    |-debugging/
   |    |    |
   |    |    |-clear_table.py
   |    |    |-create_database.py
   |    |    |-dump_table.py
   |    |
   |    |-add_college.py
   |    |-add_fixture_dates_scores.py
   |    |-add_league.py
   |    |-(heel.db)
   |    |-set_fixtures.py
   |
   |-static/
   |    |-(...)
   |
   |-templates/
   |    |-(...)
   |
   |-main.py
   |-README.md
</pre>
- private/ is for all the admin tools in production. Normal users should never see these.
- private/debugging is for all the tools I used when developing this project. It would normally be deleted before going into production but I have left them here for documentation.
- static/ is for all the static assets like stylesheets and images.
- templates/ are for all the dynamic html pages.
- main.py is the main backend and also webserver for the project. Ideally, a dedicated webserver such as Apache would be used in production but it would be too complex to implement here.

Note that heel.db is created by create_database.py and is not source code. Don't try to open it in a text editor
Scripts in private/ and debugging/ should be ran in their respective directory.

## How to run
- Install Flask and bcrypt python libraries
- run create_database.py *in the debugging/ directory*
- run main.py
- the website should be accessible on 127.0.0.1:8080