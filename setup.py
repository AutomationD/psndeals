from setuptools import setup

setup(
        name='psndeals',
        version='0.1',
        py_modules=['psndeals'],
        include_package_data=True,
        install_requires=[
            'click',
            'click-config',
            'requests',
            'mechanize',
            'requests_oauthlib',
            'cookiejar',
            'tabulate'

        ],
        entry_points='''
        [console_scripts]
        psndeals=psndeals:cli
    ''',
)