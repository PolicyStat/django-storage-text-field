from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='django-storage-text-field',
    version="1.0.0",
    package_dir={'storage_text_field': 'storage_text_field'},
    packages=['storage_text_field', 'storage_text_field.tests'],
    description='Custom Django field that saves content to storages and a reference to the stored file in the database.',  # noqa
    author='Jason Ward',
    author_email='jason.ward@policystat.com',
    license='MIT License',
    url='http://github.com/PolicyStat/django-storage-text-field/',
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Web Environment',
    ],
)
