# manganloader

## Characteristics
- download of raw images using [mloader](https://github.com/hurlenko/mloader)
- EPUB / CBZ generation through [KCC](https://github.com/ciromattia/kcc/tree/master)
- PDF generation through Pillow (yeah, easy there)

## Installation
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

### Deployed version
The application has been deployed onto Render:
[https://manganloader.onrender.com/][https://manganloader.onrender.com/]
Since I am poor, the website sometimes does not load as stuck - Render has a timeout for poor users - then wait few minutes until it spins up again.
Ah, there are some memory constraints in the host machine on Render, then the application sometimes does not generate the files (if they are too big). Workaround: try again. I told you.
