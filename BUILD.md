
## Build
* Before you build, please ensure you update the project version in `{project-root}/setup.py`
  * The field is `setup -> version`
* To build, run the script `./build.sh` from **project root directory**
  * The build script will automatically delete the following build directories in project root
    * build/
    * dist/
    * candlestix.egg-info/
  * Next, it builds the project using `python3 -m build --wheel`

## Build and Local Install
* To install run `./build.sh -i` or `./build.sh --install`
* To verify, run `pip list | grep doot`

## Uninstall 
- To uninstall, run `pip uninstall doot`
- Verify `pip list | grep doot` 

## Upload a new Dist
1. `./build.sh`
2. `twine upload dist/*`

To upload dists, you should have file `.pypirc` in your home directory. 
