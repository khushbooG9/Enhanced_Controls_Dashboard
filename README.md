# Enhanced_Controls_Dashboard

### Getting Started

### Setup Dev Environment
   - _NOTE: These instructions are based on a Windows 10 machine, using PyCharm Professional_

#### Starting the Development Server
  - install [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation)
  - create the conda virtual environment    
    * **\[EASIER\]** open PyCharm and click 'Create an environment from `environenment.yml`'
    * run `$ conda create --name <environment-name> --file ./requirements.txt` in your terminal
  - Add a Python run configuration (top right add configuration > python), then click run
  - Project will be running on http://127.0.0.1:8051/

#### Environment Variables
##### Follow these steps to change/set an environment variable
  1. create a `.env` file in the project root copied from `.env.template`
     1. adding a variable in `.env` requires it also be added to `.env.template`
  2. any change in `.env` requires a restart of the server

##### To use an Environment Variable
simply do
```python
import os

var = os.environ.get(<VAR>)
```
where `VAR` is the string name of the variable you want.

### Licence
[MIT](./LICENSE)