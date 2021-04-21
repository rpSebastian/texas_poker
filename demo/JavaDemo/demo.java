package demo;

import java.io.*;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import com.alibaba.fastjson.*;

public class demo {
	public String get_action(JSONObject data)
	{
		String action;
		JSONArray legal_actions = (JSONArray)data.get("legal_actions");
		if (legal_actions.contains("check"))
			action = "check";
		else
			action = "call";
		return action;
	}
	public void run(Socket socket, int room_id, int room_number, String name, int game_number, ArrayList<String> bots) throws IOException
	{
		os = socket.getOutputStream();
		is = socket.getInputStream();
		sendJson(connectMessage(room_id, room_number, name, game_number, bots));
		JSONObject data;
		int position = 0;
		while (true)
		{
			data = recvJson();
			String info = (String)data.get("info");
			if (info.equals("state"))
			{
				position = (Integer)data.get("position");
				int action_position = (Integer)data.get("action_position");
				if (position == action_position)
				{
					sendJson(actionMessage(get_action(data)));
				}
			}
			else if (info.equals("result"))
			{
				JSONArray players = (JSONArray)(data.get("players"));
				JSONObject player_info = (JSONObject)(players.get(position));
				double win_money = Double.parseDouble(player_info.get("win_money").toString());
				
				JSONArray player_card = (JSONArray)(data.get("player_card"));
				JSONArray your_card = (JSONArray) player_card.get(position);
				JSONArray opp_card = (JSONArray)player_card.get(1 - position);
				JSONArray public_card = (JSONArray)data.get("public_card");
				System.out.println("win_money: " + win_money);
				System.out.println("your card: " + your_card);
				System.out.println("opp_card: " + opp_card);
				System.out.println("public_card: " + public_card);
				sendJson(startMessage());
			}
			else
			{
				System.out.println(data.toString());
				break;
			}
		}
	}
	public JSONObject connectMessage(int room_id, int room_number, String name, int game_number, ArrayList <String> bots)
	{
		JSONObject message = new JSONObject();
		message.put("info", "connect");
		message.put("room_id", room_id);
		message.put("name", name);
		message.put("game_number", game_number);
		message.put("room_number", room_number);
		JSONArray m_bots = new JSONArray();
		for (int i = 0; i < bots.size(); ++i)
			m_bots.add(bots.get(i));
		message.put("bots", m_bots);
		return message;
	}
	public JSONObject actionMessage(String action)
	{
		JSONObject message = new JSONObject();
		message.put("info", "action");
		message.put("action", action);
		return message;
	}
	public JSONObject startMessage()
	{
		JSONObject message = new JSONObject();
		message.put("info", "ready");
		message.put("status", "start");
		return message;
	}
	
	private OutputStream os;
	private InputStream is;
	public void reverse_buf(byte[] buf)
	{
		byte mid = buf[0]; buf[0] = buf[3]; buf[3] = mid; mid = buf[1]; buf[1] = buf[2]; buf[2] = mid;
	}
	public void sendJson(JSONObject jsonData) throws IOException
	{
		String data = jsonData.toJSONString();
		int dataLength = data.length();
		ByteBuffer buffer = ByteBuffer.allocate(4);
		buffer.putInt(dataLength);
		byte[] buf = buffer.array();
		reverse_buf(buf);
		os.write(buf);
		os.flush();
        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(os));
        bw.write(data);
        bw.flush();
	}
	public JSONObject recvJson() throws IOException
	{
		byte[] buf = new byte[4];
        is.read(buf);
        reverse_buf(buf);
        ByteBuffer data = ByteBuffer.wrap(buf);
        int len = data.getInt();
        buf = new byte[len];
        is.read(buf);
        String str = new String(buf);
        JSONObject jsonData = JSONObject.parseObject(str);
        return jsonData;
	}
	public static void main(String [] args) {

		String server_ip = "holdem.ia.ac.cn";
		int server_port = 18888;
		int room_id = Integer.parseInt(args[0]);
		int room_number = Integer.parseInt(args[1]);
		String name = args[2];
		int game_number = Integer.parseInt(args[3]);
		ArrayList<String> bots = new ArrayList<String> ();
		for (int i = 4; i < args.length; i++)
			bots.add(args[i]);
		demo demo_obj = new demo();
		Socket socket;
		try {
			socket = new Socket(server_ip, server_port);
			OutputStream os = socket.getOutputStream();
			InputStream is = socket.getInputStream();	        
			demo_obj.run(socket, room_id, room_number, name, game_number, bots);
		} catch (UnknownHostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
