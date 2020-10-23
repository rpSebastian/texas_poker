## Setup

1.  安装环境

```
pip install -r requirements.txt  
```

2. 运行

```
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=root -e RABBITMQ_DEFAULT_PASS=root rabbitmq:3-management
bash scripts/main.sh
```

4. 停止

```
bash scripts/stop.sh
```
