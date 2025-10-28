# SimplePlanes Screenshots Requests

by Janno Putter

---

## Project Description

My project will be a web app where users of the SimplePlanes.com community can request screenshots from me for their builds. 
In the app, users will be able to sign in and fill out a form with details and instructions on how they want their screenshots taken, I will be able to give them the screenshots via URL, and they will be limited by the amount of requests they can place within a certain time. 
The webb app will also notify me when deadlines are appraoching as well as when a new request is placed. 

- Feature 1: Users will be able to log in to save their requests. 
- Feature 2: Users will be able to fill out a form and place a URL of the build they want screenshots taken of.
- Feature 3: When a request is placed the user will be on a cooldown timer (10 days).
- Feature 4: I will be notified when a request is placed.
- Feature 5: I will be able to respond to the request by placing notes and the URL to the screenshots.
- Feature 6: I will be notified when a dealine to a request is approaching. 


---

## Project Links

- [GitHub repo for the project](https://github.com/J-B-Putter/SP-Request-Website-T3)
- [Project Documentation](https://j-b-putter.github.io/SP-Request-Website-T3/)
- [Live web app](https://sp-request-website-t3.onrender.com)


---

## Project Files

- Program source code can be found in the [app](app/) folder
- Project documentation is in the [docs](docs/) folder, including:
   - [Project requirements](docs/0-requirements.md)
   - Development sprints:
      - [Sprint 1](docs/1-sprint-1-prototype.md) - Development of a prototype
      - [Sprint 2](docs/2-sprint-2-mvp.md) - Development of a minimum viable product (MVP)
      - [Sprint 3](docs/3-sprint-3-refinement.md) - Final refinements
   - [Final review](docs/4-review.md)
   - [Setup guide](docs/setup.md) - Project and hosting setup

---

## Project Details

This is a digital media and database project for **NCEA Level 3**, assessed against standards [91902](docs/as91902.pdf) and [91903](docs/as91903.pdf).

The project is a web app that uses [Flask](https://flask.palletsprojects.com) for the server back-end, connecting to a SQLite database. The final deployment of the app is on [Render](https://render.com/), with the database hosted at [Turso](https://turso.tech/).

The app uses [Jinja2](https://jinja.palletsprojects.com/templates/) templating for structuring pages and data, and [PicoCSS](https://picocss.com/) as the starting point for styling the web front-end.

The project demonstrates a number of **complex database techniques**:
- Structuring the data using multiple tables
- Creating queries which insert, update or delete to modify data
- Creating customised data displays from multiple tables (e.g. web pages)
- Dynamically linking data between the database and a front-end display
- Applying data access permissions as appropriate to the outcome

The project demonstrates a number of **complex digital media (web) techniques**:
- Using non-core functionality
- Using sophisticated digital effects
- Applying industry standards or guidelines
- Using responsive design for use on multiple devices
- The integration of original media assets
- Using dynamic data handling and interactivity
- Automation through scripts

** EDIT THESE LISTS ABOVE TO MATCH YOUR PROJECT**



