#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================


from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
from datetime import datetime
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.auth    import login_required
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    user_id = session.get("user_id")
    if user_id:
        with connect_db() as client:
            # Get all the responses from the DB
            sql = """
                SELECT  
                    description,
                    build_url,
                    deadline,
                    user_id

                FROM requests
                WHERE user_id = ?
                        
                ORDER BY sub_date DESC            
            """
            params=[user_id]
            result = client.execute(sql, params)
            prev_requests = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", prev_requests=prev_requests)
    else:
        return render_template("pages/welcome.jinja")
 

#-----------------------------------------------------------
# Welcome page route
#-----------------------------------------------------------
@app.get("/welcome/")
def welcome():
    return render_template("pages/welcome.jinja")

#-----------------------------------------------------------
# Admin Dashboard page route
#-----------------------------------------------------------
@app.get("/admin-dashboard/")
def show_admin_dashboard():
    with connect_db() as client:
        # Get all the requests without response from the DB
        sql = """
            SELECT  
                requests.id,
                build_url,
                description,
                mods,
                deadline,
                users.SP_username AS builder

            FROM requests
            JOIN users ON requests.user_id = users.id
            WHERE response_url IS NULL

            ORDER BY deadline ASC            
        """
        params=[]
        result = client.execute(sql, params)
        incomplete_requests = result.rows

        # And show them on the page
        return render_template("pages/admin-dashboard.jinja", incomplete_requests=incomplete_requests)
  

#-----------------------------------------------------------
# Request page route
#-----------------------------------------------------------
@app.get("/request/")
@login_required
def show_request_form():
    user_id = session.get("user_id")
    with connect_db() as client:
        # Get all the Completed Projects from the DB
        sql = """
            SELECT sub_date
            FROM requests
            WHERE user_id = ?
        """
        params=[user_id]
        result = client.execute(sql, params)
        sub_date_time = result.rows
        # Check if user has a request history
        if sub_date_time :            
            # Getting the last submission date in the user's data base
            db_date_str = sub_date_time[-1]['sub_date']  # format: YYYY-MM-DD HH:MM:SS

            # Convert to datetime object
            db_date = datetime.strptime(db_date_str, "%Y-%m-%d %H:%M:%S")

            # Cooldown duration in days
            cooldown_days = 10
            
            # Adding cooldown days
            cooldown_end = db_date + timedelta(days=cooldown_days)

        else:
            cooldown_end = datetime.now()
            
            cooldown_days = 0

     

    return render_template("pages/request.jinja", cooldown_end = cooldown_end, cooldown_days = cooldown_days)
  

#-----------------------------------------------------------
# User page route
#-----------------------------------------------------------
@app.get("/user/")
def user():
    return render_template("pages/user.jinja")


#-----------------------------------------------------------
# User registration form route
#-----------------------------------------------------------
@app.get("/register/")
def register_form():
    return render_template("pages/register.jinja")


#-----------------------------------------------------------
# User login form route
#-----------------------------------------------------------
@app.get("/login/")
def login_form():
    return render_template("pages/login.jinja")


#-----------------------------------------------------------
# Previous Projects page route 
# - Show all the responses for the logged in user
#-----------------------------------------------------------
@app.get("/previous_projects/")
def show_all_previous_projects():
    with connect_db() as client:
        # Get all the Completed Projects from the DB
        sql = """
            SELECT  
                build_url,
                response_url,
                preview_img

            FROM requests
            WHERE response_url NOT NULL

            ORDER BY sub_date DESC            
        """
        params=[]
        result = client.execute(sql, params)
        previous_projects = result.rows

        # And show them on the page
        return render_template("pages/previous_projects.jinja", previous_projects=previous_projects)


#-----------------------------------------------------------
# Responses page route 
# - Show all the responses for the logged in user
#-----------------------------------------------------------
@app.get("/responses/")
def show_all_responses():
    user_id = session.get("user_id")
    with connect_db() as client:
        # Get all the responses from the DB
        sql = """
            SELECT  
                description,
                response_url,
                notes,
                user_id

            FROM requests
            WHERE user_id = ?
                   
            ORDER BY sub_date DESC            
        """
        params=[user_id]
        result = client.execute(sql, params)
        responses = result.rows

        # And show them on the page
        return render_template("pages/responses.jinja", responses=responses)


#-----------------------------------------------------------
# Respond page route - Show a single request to respond to
#-----------------------------------------------------------
@app.get("/respond/<int:id>")
def respond_to_request(id):
    with connect_db() as client:
        # Get the thing details from the DB, including the owner info
        sql = """
            SELECT 
                user_id,
                description,
                build_url,
                deadline,
                users.SP_username AS builder

            FROM requests
            JOIN users ON requests.user_id = users.id

            WHERE requests.id=?
        """
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            request = result.rows[0]
            return render_template("pages/respond.jinja", request=request)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for submitting the response
#-----------------------------------------------------------
@app.post("/submit-response/<int:id>")
def submit_response(id):
    # Get the data from the form
    notes = request.form.get("notes")
    response_url = request.form.get("response_url")
    preview_img = request.form.get("preview_img")

    # Sanitise the text inputs
    notes = html.escape(notes)
    response_url = html.escape(response_url)
    preview_img = html.escape(preview_img)

    with connect_db() as client:
        # Add the request to the DB
        sql = "INSERT INTO requests (notes, response_url, preview_img) VALUES (?, ?, ?) WHERE id= ?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Submitted", "success")
        return redirect("/admin-dashboard")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/things/")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = """
            SELECT things.id,
                   things.name,
                   users.name AS owner

            FROM things
            JOIN users ON things.user_id = users.id

            ORDER BY things.name ASC
        """
        params=[]
        result = client.execute(sql, params)
        things = result.rows

        # And show them on the page
        return render_template("pages/things.jinja", things=things)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/thing/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB, including the owner info
        sql = """
            SELECT things.id,
                   things.name,
                   things.price,
                   things.user_id,
                   users.name AS owner

            FROM things
            JOIN users ON things.user_id = users.id

            WHERE things.id=?
        """
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            thing = result.rows[0]
            return render_template("pages/thing.jinja", thing=thing)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for placing a request, using data posted from a form
# - Restricted to logged in users
#-----------------------------------------------------------
@app.post("/place-request")
@login_required
def place_a_request():
    # Get the data from the form
    description  = request.form.get("description")
    build_url = request.form.get("build_url")
    mods = request.form.get("mods")
    deadline = request.form.get("deadline")
    deadline_time = request.form.get("deadline_time")

    # Sanitise the text inputs
    description = html.escape(description)
    build_url = html.escape(build_url)

    # Get the user id from the session
    user_id = session["user_id"]

    with connect_db() as client:
        # Add the request to the DB
        sql = "INSERT INTO requests (user_id, description, build_url, mods, deadline) VALUES (?, ?, ?, ?, ?)"
        params = [user_id, description, build_url, mods, deadline]
        client.execute(sql, params)
        
        # Go back to the home page
        flash(f"Request Placed", "success")
        return redirect("/")

#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
# - Restricted to logged in users
#-----------------------------------------------------------
@app.post("/add")
@login_required
def add_a_thing():
    # Get the data from the form
    name  = request.form.get("name")
    price = request.form.get("price")

    # Sanitise the text inputs
    name = html.escape(name)

    # Get the user id from the session
    user_id = session["user_id"]

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO things (name, price, user_id) VALUES (?, ?, ?)"
        params = [name, price, user_id]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/things")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
# - Restricted to logged in users
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
@login_required
def delete_a_thing(id):
    # Get the user id from the session
    user_id = session["user_id"]

    with connect_db() as client:
        # Delete the thing from the DB only if we own it
        sql = "DELETE FROM things WHERE id=? AND user_id=?"
        params = [id, user_id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Thing deleted", "success")
        return redirect("/things")



#-----------------------------------------------------------
# Route for adding a user when registration form submitted
#-----------------------------------------------------------
@app.post("/add-user")
def add_user():
    # Get the data from the form
    username = request.form.get("SP_username")
    password = request.form.get("password")

    with connect_db() as client:
        # Attempt to find an existing record for that user
        sql = "SELECT * FROM users WHERE SP_username = ?"
        params = [username]
        result = client.execute(sql, params)

        # No existing record found, so safe to add the user
        if not result.rows:
            # Sanitise the name
            username = html.escape(username)

            # Salt and hash the password
            hash = generate_password_hash(password)

            # Add the user to the users table
            sql = "INSERT INTO users (SP_username, password_hash) VALUES (?, ?)"
            params = [username, hash]
            client.execute(sql, params)

            # And let them know it was successful and they can login
            flash("Registration successful", "success")
            return redirect("/login")

        # Found an existing record, so prompt to try again
        flash("Username already exists. Try again...", "error")
        return redirect("/register")


#-----------------------------------------------------------
# Route for processing a user login
#-----------------------------------------------------------
@app.post("/login-user")
def login_user():
    # Get the login form data
    username = request.form.get("SP_username")
    password = request.form.get("password")

    with connect_db() as client:
        # Attempt to find a record for that user
        sql = "SELECT * FROM users WHERE SP_username = ?"
        params = [username]
        result = client.execute(sql, params)

        # Did we find a record?
        if result.rows:
            # Yes, so check password
            user = result.rows[0]
            hash = user["password_hash"]

            # Hash matches?
            if check_password_hash(hash, password):
                # Yes, so save info in the session
                session["user_id"]   = user["id"]
                session["user_name"] = user["SP_username"]
                session["logged_in"] = True

                # Test user authority
                if session["user_id"] == 1:
                    # Give admin dashboard for admin user
                    flash("Login successful", "success")
                    return redirect("/admin-dashboard")
                else:
                    # Head back to the home page
                    flash("Login successful", "success")
                    return redirect("/")

        # Either username not found, or password was wrong
        flash("Invalid credentials", "error")
        return redirect("/login")


#-----------------------------------------------------------
# Route for processing a user logout
#-----------------------------------------------------------
@app.get("/logout")
def logout():
    # Clear the details from the session
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("logged_in", None)

    # And head back to the home page
    flash("Logged out successfully", "success")
    return redirect("/welcome")

#-----------------------------------------------------------
# Route for deleting a user, Id given in the route
# - Restricted to logged in users
#-----------------------------------------------------------
@app.get("/delete-user/<int:id>")
@login_required
def delete_my_account(id):
    with connect_db() as client:
        # Delete the user from the DB
        sql = "DELETE FROM users WHERE id=?"
        params = [id]
        client.execute(sql, params)
        # Clear the details from the session
        session.pop("user_id", None)
        session.pop("user_name", None)
        session.pop("logged_in", None)

        # Go back to the home page
        flash("Account deleted", "success")
        return redirect("/welcome")


#-----------------------------------------------------------
# Terms of Service page route
#-----------------------------------------------------------
@app.get("/ToS/")
def terms_of_service():
    return render_template("pages/ToS.jinja")

