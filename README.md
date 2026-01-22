# wix-youtube-playlist-automation
Scan youtube playlist each hour and import if a youtube video is released

### 1. install packages
``` pip install -r requirements.txt ``` 

### 2. create a .env file
  ```
WIX_ACCESS_TOKEN=
WIX_SITE_ID=
 ```

### 3.a run main at the background
```
nohup python main.py &
```
### 3.b run a container
```
docker build -t wix_automation .
docker run --env-file .env wix_automation:latest 
```
