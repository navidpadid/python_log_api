# Log Viewer Application

## V 1.1
Single server and front end client working with stream support and acceptable performance.

### Pre-requisite
- Have docker installed on the host.

- Tested host: Ubuntu 24.04, Docker 27.4.1

### How to run:
1) Build and start the log servers as containers:
```bash
cd Server 
bash run.sh
```

2) Open the client application to query log servers located at:
```
Client/index.html
```

3) Example input and output:

![Example Usage](Docs/sample.png)

### Project Structure
```
Docs
├── doc.pdf
├── sample.png
│
Client
│
├── css
│   └── styles.css
│
├── js
│   └── scripts.js
│
└── index.html
Server
│
│
├── lib
│   ├── __init__.py
│   └── log_viewer.py
|
├── app_test.py
├── app.py
├── Dockerfile
├── log_generator.py
├── requirements.txt
└── run.sh
.dockerignore
.gitignore
README.md

```
