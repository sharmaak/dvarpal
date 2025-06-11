#!/bin/bash
# ensure that build is installed using pip
# python3 -m pip install build

echo 'Deleting build directories ...'
rm -frv ./build ./doot.egg-info ./dist
python3 setup.py sdist bdist_wheel

if [ $? -eq 0 ]; then
  echo '===> Build completed successfully'
else
  echo '===> *** BUILD FAILED ***'
fi

if [ "$1" == "-i" ] || [ "$1" == "--install" ]; then
  pip install -U dist/doot-*
  if [ $? -ne 0 ]; then
    echo '===> *** INSTALL FAILED ***'
  else
    echo '===> Installation successful'
  fi

else
  echo "===> Package not installed. To install run 'build.sh -i'."
fi

echo "Checking twine validity ..."
twine check dist/*