travis:
	python setup.py test --coverage \
		--coverage-package-name=irtokz
	flake8 irtokz
clean:
	find . -iname "*.pyc" -exec rm -vf {} \;
	find . -iname "__pycache__" -delete
