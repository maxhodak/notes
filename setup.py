from setuptools import setup

setup(name='notes',
      version='1.3.2',
      description='A system for keeping notes',
      url='https://github.com/maxhodak/notes',
      author='Max Hodak',
      author_email='maxhodak@gmail.com',
      license='MIT',
      packages=['notes'],
      entry_points = {
        'console_scripts': [
          'notes = notes.main:main',
          'note = notes.main:main',
        ],
      },
      install_requires = [
        'cryptography',
        'web3',
        'python-dateutil'
      ],
      zip_safe=False)
