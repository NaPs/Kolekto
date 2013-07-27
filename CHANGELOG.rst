Kolekto Changelog
=================

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