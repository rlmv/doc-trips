This is the DOC First Year trips website.

## Installation

To get a local development version running, [install Python 3.4](https://www.python.org/downloads/) and run `make install`. This sets up a virtual environment and installs all dependencies.

You must also set up some environment variables:

    DEBUG="True"
    SECRET_KEY="some secret key"

    AWS_ACCESS_KEY_ID="your key id"
    AWS_SECRET_ACCESS_KEY="your secret key"
    AWS_STORAGE_BUCKET_NAME="a bucket name"

    GOOGLE_MAPS_KEY="your google maps key"
    GOOGLE_MAPS_BROWSER_KEY="your google maps browser key"

You only need the AWS keys if you are going to be messing with Leader and Croo applications. Likewise, Google Maps is only used by the transportation app.

Finally, run `make` and visit `localhost:8000`.

(For convenience I put the environment variables in a local `config.sh` file that looks like
    
    export DEBUG="True"
    ...

and run `source venv/bin/activate && source config.sh` when I start work.)


## Documentation

The latest version of the docs are hosted at <http://doc-trips.rtfd.org>. Run `make docs` to build a local copy.





