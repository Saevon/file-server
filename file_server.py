#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
A simple file server, used to quickly serve individual files across the LAN
Can show folder contents, and allows you to download any files


"""

import bottle
import json
import os
import re

from functools import wraps


app = bottle.Bottle()


def json_return(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = json.dumps(func(*args, **kwargs), **app.config['json'])
        data = data.replace(' ', '&nbsp;').replace('\n', '<br/>')
        return data

    return wrapper



def html_list(list):
    output = ''
    for item in list:
        output += html_link(item) + html_nl()
    return output

def html_nl():
    return '''<br/ >'''

def html_link(rel_path):
    return str.format('''<a href="./{path}">{path}</a>''', **{
        "path": rel_path,
    })






def html_list_return(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = html_list(func(*args, **kwargs))
        return data
    return wrapper

def list_return(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        return '<br/>'.join(data)
    return wrapper

def is_subdir(path, directory):
    """
    Returns true if *path* in a subdirectory of *directory*.
    """
    path = os.path.realpath(path)
    directory = os.path.realpath(directory)

    return path.startswith(directory)


@html_list_return
def show_contents(folder):
    # Security: remove any symbolic links
    if not is_subdir(folder, app.config['static_root']):
        raise bottle.HTTPError(status=404)

    print "Showing: ", folder
    files = os.listdir(folder)

    file_output = []
    ignored_extensions = app.config['folder']['ignore']
    for file in files:
        path = os.path.join(folder, file)

        # Filter out any extensions we're ignoring
        if file.endswith(tuple(ignored_extensions)):
            continue
        # Filter out symbolic links, since they won't really work
        # (Could lead to blocked directories)
        # TODO: We could instead allow them if they point to an allowed abspath
        if os.path.islink(path):
            continue

        file_output.append({
            'name': file,
            'path': path,
            'isdir': os.path.isdir(path),
        })

    # TODO: change output
    # return sorted(file_output, key=lambda file: file['name'].lower())
    return sorted(files, key=lambda file: file.lower())

def if_upload_enabled(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        path = app.config['upload_path']
        if path is False:
            raise bottle.HTTPError(status=404)
        kwargs['upload_path'] = path

        return func(*args, **kwargs)
    return wrapper



@app.route('/upload', method='GET')
@if_upload_enabled
def upload_html(upload_path):
    output = u''

    success = 'success' in bottle.request.params
    if success:
        output += u'''
            Upload Succeded<script type="text/javascript">history.pushState({}, "Upload", "/upload");</script>
        '''

    output += u'''
        <form action="/upload" method="post" enctype="multipart/form-data">
            Select a file: <input type="file" name="upload" />
            <input type="submit" value="Start upload" />
        </form>
    '''

    return output

COPY_RE = re.compile(r'^(?P<name>.*) \((?P<num>[0-9]+)\)$')

@app.route('/upload', method='POST')
@if_upload_enabled
def upload(upload_path):
    upload = bottle.request.files.get('upload')

    name, ext = os.path.splitext(upload.filename)
    # if ext not in ('png', 'jpg', 'jpeg'):
    #     return 'File extension not allowed.'

    while os.path.exists(os.path.join(upload_path, name + ext)):
        match = COPY_RE.match(name)
        if match is not None:
            name = match.group('name')
            num = int(match.group('num'))
        else:
            num = 1
        name = '%s (%i)' % (name, num)

    full_path = os.path.join(upload_path, name + ext)
    upload.save(full_path)

    print "Uploaded: %s" % full_path

    return bottle.redirect('/upload?success')

@app.route('/')
def root():
    '''
    The root of the website
        if static_root is set, shows the show_contents
        if only upload_path is set, redirects to upload
    '''
    if app.config['static_root'] is False:
        if app.config['upload_path'] is False:
            # WTF? Nothing is on... Whatever
            raise bottle.HTTPError(status=204)

        # Otherwise show the upload path by default, since the static one is disabled
        return bottle.redirect('/upload')

    # Finally show the static root
    return show_contents(app.config['static_root'])

@app.route('/<filename:path>')
def static(filename):
    '''
    Allows access to any file in the static directory
    '''

    # Check if we're allowed to serve any files at all
    if not app.config['static_root']:
        raise bottle.HTTPError(status=404)

    # Check if the file exists
    path = os.path.join(app.config['static_root'], filename)
    if not os.path.exists(path):
        raise bottle.HTTPError(status=404)

    # Anything ending in a / is considered to be a folder by default
    if filename.endswith('/'):
        return show_contents(path)

    # Redirect all folders to use a trailing slash, to make relative links work
    if os.path.isdir(path):
        return bottle.redirect('/{0}/'.format(filename))

    print "Serving: ", path

    return bottle.static_file(filename, root=app.config['static_root'])


##################################################
# Settings & Startup
##################################################
app.config.update({
    'debug': True,

    'host': 'localhost',
    'port': 7070,

    'quiet': True,

    # Starting static folder
    'static_root': False,
    'upload_path': False,

    'json': {
        'sort_keys': True,
        'indent': 4,
    },
    'folder': {
        'ignore': [
            '.pyc',
        ],
    }
})


from optparse import OptionParser
app_parser = OptionParser(usage="usage: %prog [host] [options]")
app_parser.add_option(
    "-p", "--port",
    dest="port",
)
app_parser.add_option(
    "-v", "--debug", "--verbose",
    dest="debug",
    action="store_true",
)
app_parser.add_option(
    "-r", "--root",
    dest="static_root",
    action="store",
)
app_parser.add_option(
    "-u",
    "--upload",
    dest="upload_path",
    action="store",
    help="THe folder to save uploaded files (uploading is disabled unless this option is passed in",
)
app_parser.add_option(
    "-q", "--quiet",
    dest="debug",
    action="store_false",
)
app_parser.add_option(
    "--host",
    dest="host",
    action="store",
)
app_parser.add_option(
    "--open",
    dest="host",
    action="store_const",
    const="0.0.0.0",
)

def parse_options():
    '''
    Reads any commandline options, returning a final dict of options
    '''
    (options, args) = app_parser.parse_args()

    if len(args) > 1:
        app_parser.error("Too many arguments")
    elif len(args) == 1:
        app.config['host'] = args[0]
    elif options.host:
        app.config['host'] = options.host

    # Check that the root path is valid
    if options.static_root and not os.path.exists(options.static_root):
        app_parser.error("Root path does not exist: %" % options.static_root)

    # Remove any unset options, using the defaults defined earlier instead
    options = vars(options)
    options = dict((key, options[key]) for key in options if options[key] is not None)

    return options


if __name__ == '__main__':
    options = parse_options()

    app.config.update(options)

    # Debug only settings go here
    if app.config["debug"]:
        bottle.debug(True)
        app.config.update({
            'reloader': True,
            'quiet': False,
        })

    app.run(**app.config)
