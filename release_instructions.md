# Pip Release

Here is a brief instruction how to make pip release.

Install requirements 

    sudo apt-get install pandoc
    pip install pypandoc
    pip install twine    
    
Create source distributions
    
    python setup.py sdist
    
Test release first by uploading it to test.pypi.org      
    
    twine upload -–repository-url https://test.pypi.org/legacy/ dist/*
    
Or    
    
    twine upload --repository testpypi dist/dcase_util-0.2.X.tar.gz
        
You can test the release by installing it from test.pypi.org

    pip install –index-url https://test.pypi.org/simple/ dcase_util
        
Release package    

    twine upload dist/*
    
Or    
    
    twine upload dist/dcase_util-0.2.X.tar.gz
    
After the pip release, create release tag in Github. 