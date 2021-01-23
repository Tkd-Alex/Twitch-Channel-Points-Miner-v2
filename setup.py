import os
import setuptools


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()


setuptools.setup(
    name="Twitch-Channel-Points-Miner-v2",
    version="2.3.1",
    author="Tkd-Alex (Alessandro Maggio)",
    author_email="alex.tkd.alex@gmail.com",
    description="A simple script that will watch a stream for you and earn the channel points.",
    license='GPLv3+',
    keywords="python bot streaming script miner twtich channel-points",
    url="https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=read('requirements.txt').splitlines(),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English"
    ],
    python_requires=">=3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
