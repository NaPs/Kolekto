Kolekto
=======

.. image:: https://raw.github.com/NaPs/Kolekto/master/.artworks/kolekto.png


Kolekto is a really KISS movie catalog software.

Features:

- Cool CLI interface (and maybe a web interface to browse collection later)
- Able to query The Movie Database to collect metadata about movies
- Able to get informations from files itself depending of the container (title,
  quality, runtime...)
- As simple as possible: all movies are stored in a directory, a berkley
  database store the metadata for each movie, and a bunch of symlink are created
  depending of the patterns set in the config file ("by actors", "by title"...)
- Easy to extend, really!


Setup
-----

The fastest and more common way to install Kolekto is using pip::

    pip install kolekto


Debian
~~~~~~

If you use Debian Wheezy, you can also use the Tecknet repositories. Add theses
lines in your ``/etc/apt/source.list`` file::

    deb http://debian.tecknet.org/debian wheezy tecknet
    deb-src http://debian.tecknet.org/debian wheezy tecknet

Add the Tecknet repositories key in your keyring:

    # wget http://debian.tecknet.org/debian/public.key -O - | apt-key add -

Then, update and install the ``kolekto`` package::

    # aptitude update
    # aptitude install kolekto


Tutorial
--------

Create your Kolekto tree::

    $ mkdir /tmp/kolekto_test && cd /tmp/kolekto_test
    $ kolekto init
    Initialized empty Kolekto tree in /tmp/kolekto_test/


Check that the tree has been properly created::

    $ kolekto list


Look at the .kolekto directory created::

    $ tree -a
    .
    └── .kolekto
        ├── config
        ├── metadata.db
        └── movies

    2 directories, 2 files

The ``config`` file is the config file of the tree (not a joke!), the
``metadata.db`` file is the berkley database storing metadata for each movie in
the tree, and the movies directory is where to store movies themselves.

You can edit the config file using the following command::

    $ kolekto config

It will just launch your favorite editor.

There is two types of section in the config file, views and datasources. Before
to import movies, uncomment the tmdb section and fill the API key. You can get
it after a signup on themoviedb.org. I will come back to the views later.

Now, import a movie::

    $ kolekto import ~/Sintel.mkv
    Title to search [Sintel]?
    Please choose the relevant movie for the file: Sintel.ogv

    [1] Sintel (2010) by Colin Levy [tmdb]
    [2] Enter manually informations
    [3] None of these

    Choice [1-3]? 1
    Do you want to edit the movie metadata [y/N]

    Copying movie in kolekto tree...
     100% [=====================================]  420.31 M/s | Time: 00:00:01

Check that your movie has been imported::

    $ kolekto list
     3bb8414b6f70e5125e2092a3d96b483088a2283d  Sintel (2010) by Colin Levy

You can show more informations about the movie::

    $ kolekto show 3bb8414b6f70e5125e2092a3d96b483088a2283d
    title: Sintel
    directors: Colin Levy
    year: 2010
    cast: Halina Reijn
          Thom Hoffman
    writers: Esther Wouda
    collection: Blender Open Movies
    genres: Animation
            Fantasy
            Short
    title_fi: Sintel - Hiillos
    title_nl: Durian Open Movie Project
    score: 1162.625
    quality: 720p
    container: Matroska
    ext: mkv
    runtime: 14
    _datasource: tmdb
    _tmdb_id: 45745

Now reopen the config file (using ``kolekto config``), and add another view called
``"Example"`` with this pattern: ``'{genres}/{year}/{quality}/{title}.{ext}'``::

    view 'Example' {
        pattern = '{genres}/{year}/{quality}/{title}.{ext}'
    }

The following command will create symlinks for each view defined in your config
file::

    $ kolekto link
    Found 0 links to delete, 4 links to create

Inspect your Kolekto tree for the newly created links::

    $ tree
    .
    ├── Example
    │   ├── Animation
    │   │   └── 2010
    │   │       └── 720p
    │   │           └── Sintel.mkv -> ../../../../.kolekto/movies/3bb8414b6f70e5125e2092a3d96b483088a2283d
    │   ├── Fantasy
    │   │   └── 2010
    │   │       └── 720p
    │   │           └── Sintel.mkv -> ../../../../.kolekto/movies/3bb8414b6f70e5125e2092a3d96b483088a2283d
    │   └── Short
    │       └── 2010
    │           └── 720p
    │               └── Sintel.mkv -> ../../../..kolekto/movies/3bb8414b6f70e5125e2092a3d96b483088a2283d
    └── Titles
        └── Sintel.mkv -> ../.kolekto/movies/3bb8414b6f70e5125e2092a3d96b483088a2283d

    11 directories, 4 files


You can use the ``--help`` option to see all available commands.


Todo / Changelog
----------------

See the ``TODO.rst`` and ``CHANGELOG.rst`` files


Legal
-----

Kolekto is released under MIT license, copyright 2013 Antoine Millet.


Contribute
----------

You can send your pull-request for Kolekto through Github:

    https://github.com/NaPs/Kolekto

I also accept well formatted git patches sent by email.

Feel free to contact me for any question/suggestion/patch: <antoine@inaps.org>.
