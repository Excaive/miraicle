import setuptools


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='miraicle',
    version='0.1.0',
    author='Excaive',
    description='A Python SDK of mirai',
    license='AGPL 3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Excaive/miraicle',
    install_requires=['requests'],
    packages=setuptools.find_packages(),
    classifiers=[],
    keywords='mirai, bot',
    python_requires='>=3.6',
)
