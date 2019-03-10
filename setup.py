from setuptools import setup


setup(name = 'lullapy', version = '0.1.0', packages = ['andeart', 'andeart.lullapy'],
      url = 'https://github.com/andeart/lullapy', license = 'https://github.com/andeart/lullapy/blob/master/LICENSE.md',
      author = 'anurag.devanapally', author_email = 'mail@andeart.com',
      description = 'A collection of Python tools to automate and ease various pipeline processes.',
      install_requires = ['pathlib', 'colorama'])
