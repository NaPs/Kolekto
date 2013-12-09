Kolekto Changelog
=================

v1.2 released on 09/12/2013
---------------------------

- Added command profile system (first step to supporting tv shows)
- Added multiple patterns in a single view
- Added a progress bar on link generation operation
- Fixed bad usage of Dotconf API
- Fixed duplicate link problem
- Fixed creating parent directories on link even with dry-run
- Fixed config command with a non-ascii config file
- Fixed symlink to be relative to movies pool on import

v1.1 released on 27/07/2013
---------------------------

- Try to clean the filename before to search it on TMDB
- Added auto mode in import command (unattended import of movies)
- Import command now show gathered informations before to import movies
- Added the ``tmdb_votes`` field on movies
- Added the ability to delete original files after importing
- Added field alternative in view patterns (eg: {title_fr|original_title})
- Added default values on field alternatives (eg: {watched|"Unwatched"})
- Added watch, fav and crap commands
- Added ability to select movies using a file path instead of movie hash
  directly (eg: kolekto show ./Titles/my\ movie.mkv)
- Added the ability to import movies using a symlink instead of copying or
  hardlinking them
- Added the edit command (manual edit of a movie)
- Better error reporting
- Fixed a lot of bugs

v1.0 released on 28/02/2013
----------------------------

- Initial release