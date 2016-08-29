# compose-helper
Util for working with docker-compose projects and generating your own binaries.

## Setup
* **Clone** this repository:
```shell
git clone https://github.com/mbarrientos/compose-helper
```

* **Run** register_app.py to generate a binary and to setup the configuration for your app:
```shell
cd compose-helper
./register_app.py my_app /path/to/my_app
```
This will create a configuration file at `~/.compose_helper/config` and created a binary called `my_app` at `~/.compose_helper/bin`.

* **Add** these lines to your shell rc file (*.bashrc*, *.zshrc*, ...) to include the new binaries to PATH:
```bash
# Binaries from compose-helper
export PATH="/home/mbarrientos/.compose_helper/bin:$PATH"
```
Note: Modify path **/home/mbarrientos/.compose_helper/bin** with your actual config directory.

## How to use
Now you can run commands on your docker-compose application easily by typing:
```
my_app up -d
my_app exec /bin/bash

# You can specify a different docker-compose YAML file with '-f'
my_app -f docker-compose-production.yml up -d

# Flag "-s" can be used to target a different service than 'default_service'
my_app -s postgres tail -f /var/log/postgresql/postgresql.log
```

## Configuration
* **project_dir**: Path to your project.
* **default_service**: If specified, this will be the target of compose commands such as *run* or *exec*.
