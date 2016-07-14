from setuptools import setup, find_packages

setup(
    name='soft-delete',
    version='0.0.1',
    description='Soft delete plugin for django',
    long_description=open('README.rst').read(),
    author='Stuart George',
    author_email='stuart@accentdesign.com',
    url='https://github.com/AccentDesign/Accent_SoftDelete',
    download_url='',
    license='MIT',
    packages=[
        'soft_delete'
    ],
    install_requires=[
        'Django>=1.8',
    ],
    include_package_data=True,
    keywords=['django', 'soft', 'delete', 'accent', 'design'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
