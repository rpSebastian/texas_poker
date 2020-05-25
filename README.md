## Setup

1.  安装环境

```
pip install -r requirements.txt  
```

2. 单机部署服务器

```
bash scripts/main.sh
```

3. 多机部署服务器

* 一台机器上执行

```
bash scripts/main.sh
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=root -e RABBITMQ_DEFAULT_PASS=root rabbitmq:3-management
```

* 其他机器上执行

```
bash scripts/other.sh
```

4. 停止服务器执行

```
bash scripts/stop.sh
```
