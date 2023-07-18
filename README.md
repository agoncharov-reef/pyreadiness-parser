# pyreadiness-parser
Parses https://pyreadiness.org

```sh
python parser
```

Sample output:
```
  rating  ready    name                url                                          languages
--------  -------  ------------------  -------------------------------------------  --------------------------------------------------------------
       0  +        boto3               https://pypi.org/project/boto3               Python:100.00%
       1  +        awscli              https://pypi.org/project/awscli              Python:99.92% Shell:0.04% Batchfile:0.04%
       2  +        botocore            https://pypi.org/project/botocore            Python:99.32% Gherkin:0.68%
       3  +        urllib3             https://pypi.org/project/urllib3             Python:99.97% Shell:0.03%
       4  +        requests            https://pypi.org/project/requests            Python:99.77% Makefile:0.23%
       5  +        charset-normalizer  https://pypi.org/project/charset-normalizer  Python:99.71% Shell:0.29%
       6  +        typing-extensions   https://pypi.org/project/typing-extensions   Python:100.00%
       7  -        setuptools          https://pypi.org/project/setuptools          Python:98.97% C:1.02% HTML:0.01% CMake:0.01%
       8  +        certifi             https://pypi.org/project/certifi             Python:97.78% Makefile:2.22%
       9  -        python-dateutil     https://pypi.org/project/python-dateutil     Python:99.62% Shell:0.32% Batchfile:0.06%
      10  +        google-api-core     https://pypi.org/project/google-api-core     Python:95.76% Shell:3.98% Dockerfile:0.27%
      11  +        s3transfer          https://pypi.org/project/s3transfer          Python:100.00%
      12  +        idna                https://pypi.org/project/idna                Python:100.00%
      13  -        six                 https://pypi.org/project/six                 Python:100.00%
      14  +        pyyaml              https://pypi.org/project/pyyaml              Python:81.44% Cython:18.05% Makefile:0.26% Shell:0.17% C:0.08%

```