from setuptools import setup, find_packages

__version__ = "0.0"
exec(open("./pogoraidbot/version.py").read())

with open('README.md') as f:
    _LONG_DESCRIPTION = f.read()

setup(
    name='pogoraidbot',
    packages=find_packages(),
    version=__version__,
    license='gpl-3.0',
    description='A telegram bot to organize PoGo raid that it can be self hosted',
    long_description=_LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Roberto Bochet',
    author_email='robertobochet@gmail.com',
    url='https://github.com/RobertoBochet/pogoraidbot',
    keywords=['game', 'pokemongo', 'pogo', 'pokemongo-raid', 'telegram', 'telegrambot'],
    install_requires=[
        'python-telegram-bot ~= 12.7',
        'opencv-python ~= 4.1',
        'pytesseract ~= 0.3',
        'redis ~= 3.5',
        'jinja2 ~= 2.10',
        'requests ~= 2.22',
        'schema ~= 0.7',
        'apscheduler ~= 3.6',
        'mpu ~= 0.23'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.6'
)
