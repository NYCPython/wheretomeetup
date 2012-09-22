from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='WhereToMeetup',
    description='WhereToMeetup connects meetup organizers with hosts and sponsors.',
    version='0.9.4',
    author='NYCPython',
    author_email='info@wheretomeetup.com',
    license='BSD',
    url='https://github.com/NYCPython/wheretomeetup',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        # 'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: WWW/HTTP',
    ],
    # dependencies should be managed with `pip install -r requirements.txt`
    install_requires=[],
    setup_requires=['nose'],
    tests_require=['coverage'],
    py_modules=['distribute_setup'],
    packages=['meetups'],
)
