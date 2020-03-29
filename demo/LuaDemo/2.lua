local socket = require("socket")
local host = "a.xuhang.ink"
local port = 18888
local sock = assert(socket.connect(host, port))  -- 创建一个 TCP 连接，连接到 HTTP 连接的标准 80 
local json = require "json"

function recvData()
    chunk, status, partial = sock:receive(4) -- 以 1K 的字节块来接收数据，并把接收到字节块输出来
    l = 0
    for i = 4, 1, -1 do
        l = l * 256 + string.byte(chunk, i)
    end
    chunk, status, partial = sock:receive(l) -- 以 1K 的字节块来接收数据，并把接收到字节块输出来
    -- chunk = string.gsub(chunk,"\"","?");
    -- chunk = string.gsub(chunk,"\'","\"");
    -- chunk = string.gsub(chunk,"?","\'");
    return json.decode(chunk)
end
function sendData(data)
    print(data)
    data = json.encode(data)
    l = string.len(data)
    len_string = ""
    for i = 1, 4, 1 do
        len_string = len_string .. string.char(l % 256) 
        l = math.floor(l / 256)
    end
    sock:send(len_string)
    sock:send(data)    
end
function is_include(value, tab)
    for k,v in ipairs(tab) do
      if v == value then
          return true
      end
    end
    return false
end
sendData({info="connect", room_id=1, name="Alice", room_number=2, bots={"RandomAgent"}})
data = recvData()
print(data)
sendData({info="start"})
while (true) do
    data = recvData()
    print(data)
    if (data["info"] == "state" and data["position"] == data["action_position"]) then
        if (is_include('call', data["legal_actions"])) then
            action = "call"
        else
            action = "check"
        end
        sendData({info="action", action=action})
    end
    if (data["info"] == "result") then
        break
        sendData({info="start"})
    end
end