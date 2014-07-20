# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('Qollate'),
                  _class="brand", _href=URL('default', 'index'))
response.title = 'Qollate'
response.subtitle = 'HCI-Q Software'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = ''
response.meta.description = 'Qollate is software for conducting HCI-Q studies'
response.meta.keywords = 'hci, hci-q, qollate, qmethod'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), []), (T('About'), False, URL('default', 'about'), [(T('About'), False, URL('default', 'about'), []), (T('License'), False, URL('default', 'license'), [])]),  (T('Contact'), False, URL('default', 'contact'), [])
]

DEVELOPMENT_MENU = True

if "auth" in locals():
    auth.wikimenu() 
