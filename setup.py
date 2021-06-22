import setuptools


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='miraicle',
    version='0.2.3',
    author='Excaive',
    description='A Python SDK based on mirai-api-http',
    license='AGPL 3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Excaive/miraicle',
    install_requires=['requests', 'websocket-client'],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='mirai, bot',
    python_requires='>=3.6',
)
