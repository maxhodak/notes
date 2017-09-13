from setuptools import setup

setup(name='notes',
      version='0.1',
      description='A system for keeping notes',
      url='https://github.com/maxhodak/notes',
      author='Max Hodak',
      author_email='maxhodak@gmail.com',
      license='MIT',
      packages=['notes'],
      entry_points = {
        'console_scripts': [
          'notes = notes.main:main',
        ],
      },
      zip_safe=False
)
