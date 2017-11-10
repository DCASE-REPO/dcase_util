from setuptools import setup, find_packages

requirements = [
    'numpy>=1.9.2',
    'matplotlib>=2.0.0',
    'librosa>=0.5.0',
    'six>=1.10.0',
    'soundfile>=0.9.0',
    'coloredlogs>=5.2',
    'tqdm >=4.11.2',
    'pyyaml>=3.11',
    'msgpack-python>=0.4.8',
    'pydot-ng >= 1.0.0',
    'pafy>=0.5.3.1',
    'pandas>=0.19.2',
    'youtube-dl>=2017.10.1',
    'validators>=0.12.0',
    'pyparsing>=2.2.0',
    'requests>=2.12.4',
    'titlecase>=0.12.0',
    'ujson>=1.35',
    'scipy>=0.19.1',
    'colorama>=0.3.7',
    'titlecase>=0.12.0',
    'python-magic>=0.4.13',
]

try:
   import pypandoc
   long_description = pypandoc.convert_file('README.md', 'rst')

except (IOError, ImportError, RuntimeError):
    long_description = 'A collection of utilities for Detection and Classification of Acoustic Scenes and Events'

setup(
    name='dcase_util',
    version='0.1.5',
    description='A collection of utilities for Detection and Classification of Acoustic Scenes and Events',
    author='Toni Heittola',
    author_email='toni.heittola@gmail.com',
    url='https://github.com/DCASE-REPO/dcase_util',
    download_url='https://github.com/DCASE-REPO/dcase_util/releases',
    packages=find_packages(),
    package_data={
        '': ['utils/example_data/*']
    },
    long_description=long_description,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords='audio sound',
    license='MIT',
    install_requires=requirements,
    setup_requires=['nose>=1.3'],
)
