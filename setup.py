import os

from setuptools import setup

setup(
    name='messenger-server',
    version='0.1',
    packages=[''],
    url='https://github.com/bullbulk/messenger-server',
    license='',
    author='bullbulk',
    author_email='grur.ura@mail.ru',
    description='Server part of the Messenger'
)

os.mkdir('db')
