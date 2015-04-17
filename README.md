statuspage
==========

This is a Python 2.7/Flask/Bootstrap based 'status-page' service. It allows you to create one or more pages that list the condition of your company services.

It can be backed with any SQLAlchemy-supported relational database (Amazon's RDS is a good option). Administration requires a Google login, that can be restricted to your company's hosted domain.


## Screenshots
<img src="/screenshots/status_page.png?raw=true" alt="Example Status Page" style="width:250px;">

<img src="/screenshots/admin.png?raw=true" alt="Page Administration" style="width:250px;">

<img src="/screenshots/manage.png?raw=true" alt="Page Management" style="width:250px;">

## Installation Requirements:

- Python (2.7), 
- PIP/easy_install libraries listed in [requirements.txt](app/requirements.txt).

Additionally, the following is required to be installed via apt-get or [OSX Homebrew](http://http://brew.sh/):

- uwsgi (if deploying, not needed for dev)

## Configuration

The service can be configured one of two ways:

- A .cfg file, based on the example [dev.cfg](app/dev.cfg) or [prod.cfg](app/prod.cfg).
- Environment variables, prefixed with STATUSPAGE_, and using the names below.

The parameter names are hopefully self explanatory, but you'll need the following:

- __DEBUG__
- __SQLALCHEMY_DATABASE_URI__
- __GOOGLE_LOGIN_CLIENT_ID__
- __GOOGLE_LOGIN_CLIENT_SECRET__
- __GOOGLE_LOGIN_REDIRECT_URI__  # URL of the server's oauth2 callback, like: http://status.blahblah.com/oauth2_callback
- __GOOGLE_LOGIN_REDIRECT_SCHEME__  # 'http' or 'https'
- __ADMIN_GOOGLE_IDS__  # array of email addresses, including domain, to make administrators
- __RESTRICT_LOGIN_DOMAIN__  # hosted Google blahblah.com domain to restrict logins


## Development

Create your own config file...don't modify dev.cfg, you might accidentally commit it to the repo. Once set up, run the dev server via:

`STATUSPAGE_CONFIG=../yourconfig.cfg python dev.py runserver`


## Paths
To administer the different status pages, visit /page/admin.

To view the pages you create, visit /page/PAGE_SLUG where page slug is what you set when creating the page.



## License

The contents of this repository are subject to the BitTorrent Open Source License Version 1.2 (the License). You may not copy or use this file, in either source code or executable form, except in compliance with the License. You may obtain a copy of the License at [http://www.bittorrent.com/license](http://www.bittorrent.com/license).

Software distributed under the License is distributed on an AS IS basis, WITHOUT WARRANTY OF ANY KIND, either express or implied.  See the License for the specific language governing rights and limitations under the License.
