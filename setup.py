from setuptools import setup, find_packages
import os

version = '0.1~dev'

base = os.path.dirname(__file__)

readme = open(os.path.join(base, 'README.rst')).read()
changelog = open(os.path.join(base, 'CHANGELOG.rst')).read()
todo = open(os.path.join(base, 'TODO.rst')).read()


setup(name='kubrick',
      version=version,
      description='A really KISS movie catalog software',
      long_description=readme + '\n' + changelog + '\n' + todo,
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent'],
      keywords='kubrick movies',
      author='Antoine Millet',
      author_email='antoine@inaps.org',
      url='https://github.com/NaPs/Kubrick',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      scripts=['kub'],
      entry_points={'kubrick.commands': ['list = kubrick.commands.list:List',
                                         'import = kubrick.commands.importer:Import',
                                         'gc = kubrick.commands.gc:Gc',
                                         'link = kubrick.commands.link:Link',
                                         'init = kubrick.commands.init:Init',
                                         'show = kubrick.commands.show:Show',
                                         'rm = kubrick.commands.rm:Rm',
                                         'refresh = kubrick.commands.refresh:Refresh',
                                         'dump = kubrick.commands.dump:Dump',
                                         'restore = kubrick.commands.restore:Restore',
                                         'config = kubrick.commands.config:Config'],
                    'kubrick.datasources': ['tmdb = kubrick.datasources.tmdb:TmdbDatasource',
                                            'mediainfos = kubrick.datasources.mediainfos:MediainfosDatasource']},
      install_requires=['dotconf', 'kaa-metadata', 'progressbar', 'fabulous', 'requests'])
