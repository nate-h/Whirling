# Delete all whirling track analysis files.
find data -name "*.p" -type f -delete

# Delete python cache files
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf