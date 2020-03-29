## Setup

1.  安装环境

```
pip install Django==2.2.7 dwebsocket pyyaml==5.1.2 pymysql requests numpy better-exceptions loguru twisted
```

2. 在一个终端下运行

```
cd website
python manage.py runserver
```

3. 在另一个终端下运行

```
cd server
python main.py
```

4. 三种连接方式

   * 在浏览器中输入127.0.0.1:8000/poker/login 

   * 使用python连接服务器

     ```
     cd demo/PyDemo
     python demo.py
     ```

   * 使用C++连接服务器

     ```
     cd demo/CppDemo
     make
     ./main
     make clean
     ```

 