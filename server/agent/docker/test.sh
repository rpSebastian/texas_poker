for ((room_id=1;room_id<=10; room_id+=1));
do
nohup docker run --rm --network=host registry.cn-hangzhou.aliyuncs.com/xuhang/agent:CallAgent python CallAgent.py --room_id=$room_id --room_number=2 --game_number=2 --server_ip=127.0.0.1 &
nohup docker run --rm --network=host registry.cn-hangzhou.aliyuncs.com/xuhang/agent:CallAgent python CallAgent.py --room_id=$room_id --room_number=2 --game_number=2 --server_ip=127.0.0.1 &
done