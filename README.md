# manganloader

## Characteristics
- download of raw images using [mloader](https://github.com/hurlenko/mloader)
- EPUB / CBZ generation through [KCC](https://github.com/ciromattia/kcc/tree/master)
- PDF generation through Pillow (yeah, easy there)

### Deployed version
The application has been deployed onto:
- Google Cloud [https://manganloader-bjo3n53nda-uc.a.run.app/](https://manganloader-bjo3n53nda-uc.a.run.app/)
- Render [https://manganloader.onrender.com/](https://manganloader.onrender.com/)
- Render - light version [https://manganloader-simple.onrender.com/](https://manganloader-simple.onrender.com/) . The version does not rely on Selenium and Javascript to download mangas, hence its usage is restricted to those sources which do not require these tricks.
If you dare downloading mangas from these exotic sources, you will get an empty zip file - and you deserve it, I told you to not try!

Since I am poor and I cannot afford unlimited cloud resources, the websites may not generate documents due to memory issues.

Render has a timeout for poor users - then wait few minutes until it spins up again.
Workaround: try again.

## Docker Container
### Spin-up your whale
Everybody likes [Docker](https://www.docker.com/) 🐳.
I do, as well, then I provided a script to build an image 📦:
```bash
chmod +x docker_build.sh
sh docker_build.sh
```
... and a script to run it 💞:
```bash
chmod +x docker_run.sh
sh docker_run.sh
```
The Dockerfile fetches the latest version of the repo, prepares the environment for deployment, serves the app through [Gunicorn](https://gunicorn.org/).
### Usage
The application is usually served on [http://0.0.0.0:3000](http://0.0.0.0:3000) .
Just to be sure, check the Docker logs and you will see a nice sentence like:
```
Link to the project homepage: http://0.0.0.0:3000
```

## Local Installation
### Python dependencies
Use the `requirements.txt` file to load the high-level dependencies into a Python virtual environment - `env` in the following example:
```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
### KCC as submodule
Use git to download the [KCC](https://github.com/ciromattia/kcc/tree/master) source code:
```bash
git submodule update --init --recursive
```
KCC will be stored into the `kcc` folder - and invoked from there.
### Usage
If you just want your manga, run the [Flask](https://flask.palletsprojects.com) application with the command:
```bash
python3 flask_app.py
```
It is OS-agnostic, then you have no excuses for missing dependencies on your Windows machine.

If you are nerd, you can find examples of calls in the `test.py` and `download_colored.py` files.
It can be useful for people writing Telegram bots - we both now to whom this message should be delivered, right @ShadowTemplate ?

## In the next episodes... (a.k.a. "ToDo List")
- (front-end) Device selection if EPUB selected, we have KCC then we are powerful enough to generate device-specific files.
- Extend to other mangas, beucase HxH is not to be neglected.
- (back-end) Distinguish between SIMPLE (no Selenium) and NORMAL (with Selenium) version during deployment.
- (back-end) Use either Gunicorn or Flask to serve the application, can be changed with an environment variable.
