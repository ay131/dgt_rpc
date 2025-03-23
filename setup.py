from setuptools import setup, find_packages

setup(
    name='odoo_xmlrpc',
    version='0.1.0',
    packages=find_packages(),
    description='A simple client for interacting with Odoo via XML-RPC',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ahmed Youssef',
    author_email='ahmed.youssef@compit.aun.edu.eg',
    url='https://github.com/ay131/odoo_xmlrpc',
    license='MIT',
    install_requires=[
        # No external dependencies required as xmlrpc.client is part of the standard library
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
) 