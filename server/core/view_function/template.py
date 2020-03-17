#
# File: server/utils/template.py
# Copyright: Grimm Project, Ren Pin NGO, all rights reserved.
# License: MIT
# -------------------------------------------------------------------------
# Authors:  Ming Li(adagio.ming@gmail.com)
#
# Description: some template webpages.
#
# To-Dos:
#   1. make other supplements if needed.
#
# Issues:
#   No issue so far.
#
# Revision History (Date, Editor, Description):
#   1. 2019/08/19, Ming, create first revision.
#


from flask import render_template
from flask import url_for, redirect
from server.core import grimm as app


# test flask url_for, redirect
@app.route('/test-redirect')
def test_redirect():
    return redirect(url_for('home'))

# test flask render webpage
@app.route('/render')
def render():
    return render_template('patsy-doherty/index.html')