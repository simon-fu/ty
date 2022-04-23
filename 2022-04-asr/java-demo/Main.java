import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft_6455;
import org.java_websocket.handshake.ServerHandshake;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashMap;

import static java.lang.Math.min;

public class Main {

    private static final int ONE_HUNDRED_MILLISECOND = 3200;

    public static void sendData(WebSocketClient client) {

        Path path = Paths.get("C:\\Users\\Orion\\Documents\\soundai\\alarm.pcm");
        byte[] data = new byte[0];
        try {
            data = Files.readAllBytes(path);
        } catch (IOException e) {
            e.printStackTrace();
        }

        AsrRequest request = AsrRequest.builder()
                .sid("63235c5f-3442-4a11-80f1-0a0e3f42d325")
                .pid(7001)
                .devid("abcd")
                .protocol("307")
                .lang(1)
                .user_semantics("{\"client_id\":\"c_00000001\",\"user_id\":\"skd_test_uid\",\"device_type\":\"2\",\"deviceid\":\"sdk_test_did\",\"imei\":\"012345678912345\",\"lat\":\"30.678124\",\"lng\":\"104.09434\",\"os_type\":\"android\",\"union_access_token\":\"sdk_test_token\",\"os_version\":19,\"date\":1496282827061,\"version\":10509}&sign=ab93f1311453f8eade25a9733d25013c")
                .build();

        String config = JSON.toJSONString(request);
        System.out.println("send asr config: " + config);
        client.send(config);

        byte[] dest = new byte[ONE_HUNDRED_MILLISECOND];
        for (int i = 0; i * ONE_HUNDRED_MILLISECOND < data.length; i++) {
            Arrays.fill(dest, (byte) 0);
            System.arraycopy(data, i * ONE_HUNDRED_MILLISECOND, dest, 0,
                    min(ONE_HUNDRED_MILLISECOND, data.length - i * ONE_HUNDRED_MILLISECOND));

            System.out.println("send data:" + i);
            client.send(dest);
        }
        System.out.println("send asr end");
        client.send("asr end");
    }

    public static void main(String[] args) throws URISyntaxException, IOException {

        String token = "B9FE23BC761CDD9FF44143024BD5616ECCC266D90914114F58B49655DF41B59932287C4B04920311B855A7B6D5763362DD4354F8A8315D81CCD26BD01A358E14";
        HashMap<String, String> headers = new HashMap<>();
        headers.put("Authorization", "Bearer "+token);

        WebSocketClient webSocketClient = new WebSocketClient(new URI("ws" +
                "://10.100.38.186:8081/ws/streaming-asr"), new Draft_6455(), headers, 0) {
            @Override
            public void onOpen(ServerHandshake serverHandshake) {
                System.out.println("websocket open");
                sendData(this);
            }

            @Override
            public void onMessage(String s) {
                System.out.println("on message:" + s);
                try {
                    JSONObject obj = JSON.parseObject(s);
                    int eof = obj.getInteger("eof");
                    if (eof == 1) {
                        String ret = obj.getString("result");
                        System.out.println(ret);
                    }
                } catch (Exception e) {
                    System.out.println(e);
                }
            }

            @Override
            public void onClose(int i, String s, boolean b) {
                System.out.println("on close:" + s);
            }

            @Override
            public void onError(Exception e) {
                System.out.println("on error:" + e);
            }
        };

        webSocketClient.connect();
    }
}
