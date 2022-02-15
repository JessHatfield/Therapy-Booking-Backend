if
python3.9 -m unittest tests/route_integration_tests.py&&\
python3.9 -m unittest tests/model_tests.py

then
  echo "API Integration Tests Ran Without Errors"
else
  echo "API Integration Tests Ran With 1 Or More Errors"
  exit 1
fi