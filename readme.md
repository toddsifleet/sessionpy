A python user authenticator
=============

I wanted a simple way to authenticate users in any type of python app.  Authenticating users includes passwords, sessions, remember me token, and email auth tokens.  Sessionpy handles all of these things in one place, so it doesn't have to be rebuilt in every app.

Goals
============

* Completely database agnostic.
    * MySql
    * Postgres
    * Sqlite
    * more? (to come)
* Super simple usage:
    * config.py
        * set db attrs
        * set pw hash atts
        * more? (to come)
    * sessionpy.py init => create all necessary tables

* Authenticate users in with username/email and password.
* Authenticate users with email/remember me tokens.
* Create and manage sessions for authenticated users
* Deliver a basic User/Session/Token ORM




More to come...
======

License:
-------

See LICENSE
