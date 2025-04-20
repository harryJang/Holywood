# COMP3900 H18A Holywood Project Document

## Project Setup

### Virtual environments

Virtual environments are independent groups of Python libraries, one for each project. Packages installed for one project will not affect other projects or the operating system’s packages.

We used virtual environments to manage the dependencies to make sure **compatibility** of our project since it's likely that we need to work with different versions of Python libraries on our local machine. 

### Create an environment

Create a project folder and a `venv` folder within:

#### Linux/MacOS

```
$ mkdir holywood
$ cd holywood
$ python3 -m venv venv
```

#### Windows

```
> mkdir holywood
> cd holywood
> py -3 -m venv venv
```

### Activate the environment

#### Linux/MacOS

```
$ . venv/bin/activate
```

#### Windows

```
> venv\Scripts\activate
```

### Python Packages

Use pip commend for python and pip3 command for python3 to install python packages

##### Install Flask

```
pip install Flask
```

##### Install pymysql

```
pip install pymysql
```

##### Install SQL connector

```
pip install mysql-connector-python
```

##### Install APScheduler

```
pip install APScheduler
```

##### Install cryptography

```
pip install cryptography
```

##### Install numpy

```
pip install numpy
```

##### Install surprise

```
pip install scikit-surprise
```

##### Install pandas

```
pip install pandas
```

##### Install scipy

```
pip install scipy
```

##### Install sklearn

```
pip install scikit-learn
```

##### Install XGBoost

```
pip install xgboost
```

##### Install SerpApi

```
pip install google-search-results
```

##### Install Pytest

```
pip install pytest
```



#### Alternative Approach

##### Install Pipreqs

```
pip install pipreqs
```

##### Generate dependencies

Under the current working directory type the following command in the terminal. This command will generate a requirements.txt file which contains all python dependencies and their verisions

```
pipreqs
```

##### Install requirements.txt

```
pip install -r requirements.txt
```



### Configuring MySQL

**Change the password in get_pw() function** to your own MySQL database password in  **mysql_util.py**

### Run The Application

Now you can run your application using the `flask` command. 

Direct **under the `holywood` directory** and run the following command:

```
$ flask --app web run --debug
```

Debug mode shows an interactive debugger whenever a page raises an exception, and restarts the server whenever you make changes to the code. You can leave it running and just reload the browser page.

You’ll see output similar to this:

```
* Serving Flask app "flaskr"
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: nnn-nnn-nnn
```

You can quit the application when pressing CTRL+C if needed.

### Error Handling

#### ssl.SSLCertVerificationError

In case you encounter this error, it's likely to come from wishlist.py. What you need to do is **double click** a file called "**Install Certificates.command**". You can **find this file in Applications if you are using macOS

## Project Architecture

### Database Overview

![Holywood Data Diagrams](/Users/honne/Downloads/Holywood Data Diagrams.png)

#### Schemas in data.sql

The script below describes how we store data and relationships of data models in MySQL database with comments for attributes

```mysql

CREATE TABLE if not exists Movies (			-- Movie Data Model
    id INT NOT NULL AUTO_INCREMENT, 		-- Movie ID
    name VARCHAR(255) NOT NULL, 			-- Movie Name
    poster VARCHAR(1024), 				    -- Movie Poster in Url Form
    director VARCHAR(255) NOT NULL, 		-- Movie Director
    casts JSON NOT NULL, 					-- Movie Main Casts
    description TEXT, 						-- Movie Description
    release_date DATE,						-- Movie Release Date
    avg_rating DECIMAL(4, 2) DEFAULT 0,		-- Movie Average Rating Based on User Review Ratings
    count_reviews INT DEFAULT 0,			-- Movie Popularity Based on Number of User Reviews
    PRIMARY KEY (id),						-- Primary Key Constraint on Movie ID
    UNIQUE(name)							-- Unique Constraint on Movie Name
);

CREATE TABLE if not exists Genres (			-- Genre Data Model
    id INT NOT NULL,						-- Genre ID
    name VARCHAR(45) NOT NULL,				-- Genre Name
    PRIMARY KEY (id)                        -- Primary Key Constraint on Genre ID
);

CREATE TABLE if not exists Genres_of_Movies (			-- Genre and Movie Relationship Data Model
    genre_id INT NOT NULL,								-- Genre ID
    movie_id INT NOT NULL,								-- Movie ID
    PRIMARY KEY (genre_id, movie_id),					-- Primary Key Constraint on Genre ID and Movie ID
    FOREIGN KEY (genre_id) REFERENCES Genres(id),		-- Foreign Key Constraint on Genre ID
    FOREIGN KEY (movie_id) REFERENCES Movies(id)		-- Foreign Key Constraint on Movie ID
);

CREATE TABLE if not exists Users (				                -- User Data Model
    id INT NOT NULL AUTO_INCREMENT,				                -- User ID
    username VARCHAR(255) NOT NULL,				                -- User Name
    password VARCHAR(255) NOT NULL,				                -- User Password
    email VARCHAR(45),										    -- User Email
    role ENUM('USER', 'ADMIN', 'MODERATOR') DEFAULT 'USER',		-- User Role (Enum specifies three role types)
    PRIMARY KEY (id),											-- Primary Key Constraint on User ID
    UNIQUE (username)											-- Unique Constraint on User Name
);


CREATE TABLE if not exists Reviews (				-- Review Data Model
    id INT NOT NULL AUTO_INCREMENT,				    -- Review ID
    user_id INT NOT NULL,							-- User ID 
    movie_id INT NOT NULL,							-- Movie ID
    rating INT NOT NULL,							-- Review Rating 
    comment TEXT NOT NULL,							-- Review Comment
    flagged TINYINT DEFAULT 0,						-- Review Report Indicator (0 - Not Reported, 1 - Reported)
    CHECK (rating >= 1 AND rating <= 5),			-- Check Constraint on Review Rating
    PRIMARY KEY (id),								-- Primary Key Constraint on Review ID
    FOREIGN KEY (user_id) REFERENCES Users(id),		-- Foreign Key Constraint on User ID
    FOREIGN KEY (movie_id) REFERENCES Movies(id)	-- Foreign Key Constraint on Movie ID
);


CREATE TABLE if not exists ReviewFlags (			    -- Reported Review Data Model
    moderator_id INT NOT NULL,							-- Reporting Admin/Moderator ID
    review_id INT NOT NULL,								-- Review ID
    PRIMARY KEY (moderator_id, review_id),			    -- Primary Key Constraint on Moderator ID and Review ID
    FOREIGN KEY (moderator_id) REFERENCES Users(id),	-- Foreign Key Constraint on User ID
    FOREIGN KEY (review_id) REFERENCES Reviews(id)		-- Foreign Key Constraint on Review ID
);


CREATE TABLE if not exists WishLists (			    -- User Wish List Data Model
    user_id INT NOT NULL,							-- User ID
    movie_id INT NOT NULL,							-- Movie ID
    PRIMARY KEY (user_id, movie_id),				-- Primary Key Constraint on User ID and Movie ID
    FOREIGN KEY (user_id) REFERENCES Users(id),		-- Foreign Key Constraint on User ID
    FOREIGN KEY (movie_id) REFERENCES Movies(id)	-- Foreign Key Constraint on Movie ID
);

CREATE TABLE if not exists BannedLists (					-- Ban List Data Model
    banning_user_id INT NOT NULL,							-- User ID of Banning User
    banned_user_id INT NOT NULL,							-- User ID of Banned User
    PRIMARY KEY (banning_user_id, banned_user_id),			-- Primary Key Constraint on Two Users
    FOREIGN KEY (banning_user_id) REFERENCES Users(id),	    -- Foreign Key Constraint on Banning User ID
    FOREIGN KEY (banned_user_id) REFERENCES Users(id)		-- Foreign Key Constraint on Banned User ID
);

CREATE TABLE if not exists Contributions (			-- User Contribution Data Model
    id INT NOT NULL AUTO_INCREMENT,					-- Contribution ID
    user_id INT NOT NULL,						    -- User ID
    movie_id INT NOT NULL,							-- Movie ID
    approved INT DEFAULT -1,                        -- Approval Indicator (-2 - Not Approve | -1 -> Pending | >0 -> Approver ID)
    name VARCHAR(255) NOT NULL,						-- Updated Movie Name
    poster VARCHAR(1024),							-- Updated Movie Poster
    director VARCHAR(255) NOT NULL,				    -- Updated Movie Director
    casts JSON NOT NULL,							-- Updated Movie Casts
    description TEXT,							    -- Updated Movie Description
    release_date DATE,							    -- Updated Movie Release Date
    PRIMARY KEY (id),								-- Primary Key Constraint on Contribution ID
    FOREIGN KEY (user_id) REFERENCES Users(id),		-- Foreign Key Constraint on User ID
    FOREIGN KEY (movie_id) REFERENCES Movies(id)	-- Foreign Key Constraint on Movie ID
);
```



## Project Layouts

The project directory will contain:

- `web/`, a Python package containing **our application code and files**.
- `tests/`, a directory containing **test modules**.
- `venv/`, a Python **virtual environment** where Flask and other dependencies are installed.
- `Work Diary/`, our **work diary** for weekly check-in.
- `.gitIgnore`, **version control config**.
- `README.md`, **user document** contains infomation about project setup/installation/stucture (**this file**). 
- `data.sql`, our project database script

Here's our project layouts in detail:

```
holywood
├── web/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── banlist.py
│   ├── contribution.py
│   ├── movie.py
│   ├── movie_recommendation.py
│   ├── mysql_util.py
│   ├── review.py
│   ├── search.py
│   ├── sorting.py
│   ├── theater.py
│   ├── user.py
│   ├── wishlist.py
│   ├── wishlist_email.py
│   ├── templates/
│   │   ├── admin/
│   │       ├── adminFlag.html
│   │       ├── movieList.html
│   │   │   ├── reviewContribution.html
│   │   │   ├── selectModerator.html
│   │   │   └── viewDetail.html
│   │   ├── auth/
│   │   │   ├── signin.html
│   │   │   └── signup.html
│   │   ├── movie/
│   │       ├── detail.html
│   │       ├── home.html
│   │       ├── search.html
│   │       └── sorting.html
│   │   └── user/
│   │       ├── banlist.html
│   │       ├── editReview.html
│   │       ├── myProfile.html
│   │       ├── review.html
│   │       ├── userContribute.html
│   │       ├── userProfile.html
│   │       └── wishlist.html
│   └── static/
│       ├── script.js
│       └── styles.css
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_db.py
│   ├── test_admin.py
│   ├── test_auth.py
│   ├── test_banlist.py
│   ├── test_contribution.py
│   ├── test_movie.py
│   ├── test_review.py
│   ├── test_search.py
│   ├── test_sorting.py
│   ├── test_theater.py
│   ├── test_user.py
│   └── test_wishlist.py
├── venv/
├── Work Diary/
├── .gitIgnore
├── README.md
├── data.sql
└── testdb.sql
```

## Project Intro 

This section includes a brief introduction of each python file

#### __init__.py
This file initializes web application, registers all the blue prints and schedule the behaviour(sending a notification through an email) that needs to occur on a daily basis.


#### admin.py (Qihan Zhuang)

admin.py provides most functionalities to user with admin role (get_flagged_reviews/get_contributions/get_users), with specific requirements of contribution list (similar to a to do list of regulators), the admin will only see the contribution that with approved / not approved yet status in the list, when the contribution has been denied by the admin/moderator, only the denied contributor can see the contribution.

#### auth.py (Wenqi Zhao)



#### banlist.py (Wenqi Zhao)



#### contribution.py (Qihan Zhuang)

contribution.py contains functions for the contribution part, details function lets admin/moderator see details of a contribution in contribution list so that the regulators can make sure the contribution is thoroughly checked, (un)validate_contribution will function as its name: once the contribution is validated by regulators, the content of contribution will be replacing the original movie info. If the contribution has been denied, the approved attribute of selected contribution will be set to -2 and now display in the contribution list. Update_movie function will insert a record of contribution and set to pending (-1 in the approved attribute) if the role is user, the movie will be immediately updated if the role is not user.

#### movie.py (Qihan Zhuang)

movie.py contains functions related to displaying/searching movies, index function will provide the default page of our application, the page will render the latest 20 movies in descending order and data masked for safety check, details function will display all the required info (detail of the movie, similar movie recommendation, theatre/timeslots if movies are currently on air) about a selected movie with data masking. add_wishlist/tag_search/sorting/search_movie will render corresponding pages with specific functions been called and data returned as the content of pages

#### movie_recommendation.py (Yunseok Jang)
movie_recommendation.py contains two main functions which are recommendation_for_home_page and recommendation_for_detail_page. The name of those functions are quite self explanatory. They returns a list of movies that will be recommended to user at home page and movie detail page respectively.

Methods that are used for getting recommendation are collaborative filtering, cosine similarity and factorization.

Collaborative filtering is used for recommendation_for_home_page and it uses matrix of user-movie rating to predict specific users' potential rating for movies the user haven't seen. If the prediction is higher, the movie will be more likely to be recommended to the user.

For recommendation_for_detail_page, factorization is used. So factors such as release date, how many times it has been wishlisted, the number of reviews are used to determine how the movie is similar to selected movie. If it's more similar, it is likely to be recommended.

Yunseok Jang(z5286005) who has created this file initially thougth there are three different features so he created three methods. But since the team dicided to go with only two, cosine similarity is not used. It can be used to find most similar movie of selected movie by user's history in future implementation.

#### mysql_util.py (Qihan Zhuang)

mysql_util.py contains all the functionalities for connecting Flask application to MySQL database. The file mainly consists of a utility class named MysqlUtil for CRUD operations on data tables. Functions like insert/delete/update/fetchxxx support single transaction and will close the database when they are called. Functions with suffix WithoutClose support multiple transaction and will not close the database when they are called, they are created for code refactoring purpose (to avoid unnecessary duplicate initalization of MysqlUtil class).

#### review.py (Qihan Zhuang)

review.py contains operations of add/delete/edit/flag/unflag reviews. All system users can add review to the selected movie, reviewer can edit/delete their own reviews. Admin can delete/flag any reviews, moderators can flag others' reviews to help the admin better regulate the system.

#### search.py (Yunseok Jang)
search.py contains functions to let user allow to search movies by keywords and genres. User can search by multiple keywords and if the keywords appear in one of its name, description, casts or directors, the movie will appear in the result. The order can vary determined by how the movie is related to the keywords. The more matches, the higher position it will show up on.

#### sorting.py (Yunseok Jang)
sorting.py will sort all the movies in the database in some order. Currently, there are 6 criteria which are most/lease recent, highest/lowest rating and most/least review. By default, it will rank them with most recent movies.

#### theater_recommendation.py (Wenqi Zhao)



#### user.py (Yunseok Jang && Wenqi Zhao && Qihan Zhuang)



#### wishlist.py/wishlist_email.py (Yunseok Jang)
wishlist.py allows user to add a movie to his/her wishlist, remove one from the wishlist and get the whole wishlist. Also, user can check other users' wishlist by clicking users' profile on the user review. When user has a movie in the wishlist and that movie is released today, the user will get a notification of the movie being released by an email. That feature is implemented in wishlist_email.py. It has been scheduled to happen on daily basis. Related code is in __init__.py.



## Testing

We've implemented several tests for our application using Pytest functions.

Since our backend connects to database by using MySQL utility functions instead of initialising databases in the flask application. Our tests will make the following assumptions:

```
The system contains 3 users
username:admin | password:123456 | role : ADMIN
username:moderator | password:123456 | role : USER
username:user | password:123456 | role : USER
```

In the configuration of test folder (conftest.py):

```python
def login(self, username="admin", password="123456"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )
```

The login function will take in admin user as the default login user for convenience.

```python
auth.login() // login as admin
auth.login(username="user", password="123456") // login as other users
```

To run the test, type the following command under project directory and venv

```
pytest
```

