from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='apispace',
      version='0.1',
      description='Python package for interacting with the ArchivesSpace API',
      long_description=readme(),
      author='Alicia Detelich',
      author_email='adetelich@gmail.com',
      classifiers=[
          'Development Status : : Beta',
          'License :: OSI Approved :: MIT License'
          'Programming Language :: Python :: 3.6',
          'Natural Language :: English',
          'Operating System :: OS Independent' #HOPEFULLY - haven't tested on Windows yet
          ],
      url='https://github.com/ucancallmealicia/apispace',
      license='MIT',
      keywords=['archives', 'API', 'ArchivesSpace'],
      packages=['apispace'],
      install_requires=['requests', 
                        'pymysql'
                        ],
      include_package_data=True,
      zip_safe=False)