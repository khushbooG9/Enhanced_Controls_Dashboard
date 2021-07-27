# Enhanced_Controls_Dashboard

###Setup Dev Environment
_NOTE: These instructions are based on a Windows 10 machine, using PyCharm Professional_

####Environment Variables
  1. create a `.env` file in the project root copied from `.env.template`
  2. any change in `.env` requires a restart of the server

####Starting the Development Server
  - install [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation)
  - create the conda virtual environment    
    * **\[EASIER\]** open PyCharm and click 'Create an environment from `environenment.yml`'
    * run `$ conda create --name <environment-name> --file ./requirements.txt` in your terminal
  - Add a Python run configuration (top right add configuration > python), then click run
  - Project will be running on http://127.0.0.1:8051/

###Getting Started
 - any files in `assets/` will be used by the dash - add any CSS there
 - DO NOT edit `styles.scss` unless you have an [SCSS file watcher enabled in Pycharm](https://www.jetbrains.com/help/pycharm/transpiling-sass-less-and-scss-to-css.html)
   - if you don't have Pycharm Pro and therefore cannot use file watchers, just edit `styles.css` which is under the `styles.scss` dropdown