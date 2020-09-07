from os.path import isdir, dirname
from os import getenv
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
cached_folder_assets : Optional[str] = None



def path_folder_assets() -> str:
    # finds the path of the folder that contans the assets
    # will use :
    # if defined in environment variable, what is defined in environment variable
    # Else, will look for an folder name assets in ./ then in ../ 
    # As soon as it will have located an assets folder, it will use it for any purpose
    global cached_folder_assets
    if cached_folder_assets is None:
        path_env : Optional[str] = getenv("ASSETS_PATH") 
        if path_env is not None:
            if not isdir(path_env):
                logging.error("The specified environment variable ASSETS_PATH is not a valid directory. Remove it or include a valid path to the assets folder.")
                raise FileNotFoundError
            cached_folder_assets = path_env
        elif isdir(dirname(__file__) + "/../assets"):
            # Will work when app is launched from home folder and folder is ./assets (with make run, or in circleCI) 
            # AND when app is launched with the command in Procfile (and folder is ../assets)
            # (for example in Scalingo)
            cached_folder_assets = dirname(__file__) + "/../assets"
        else:
            logging.error("A valid assets folder could not be found. Please include explicit link to path in ASSETS_PATH environment variable.")
            raise FileNotFoundError

    return cached_folder_assets
