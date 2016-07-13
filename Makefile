travis:
	python setup.py test --coverage \
		--coverage-package-name=irtokz
	flake8 --max-complexity 10 irtokz
clean:
	find . -iname "*.pyc" -exec rm -vf {} \;
	find . -iname "__pycache__" -delete
