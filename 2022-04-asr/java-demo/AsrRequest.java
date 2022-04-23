import com.alibaba.fastjson.JSON;
import lombok.Builder;
import lombok.Data;

import java.util.HashMap;
import java.util.Map;

@Data
@Builder
public class AsrRequest {
    String sid;
    int pid;
    String devid;
    String protocol;
    int lang;
    String user_semantics;

    public static void main(String[] args) {
        AsrRequest request = AsrRequest.builder()
                .sid("63235c5f-3442-4a11-80f1-0a0e3f42d325")
                .pid(7061)
                .devid("abcd")
                .protocol("0")
                .audio_type(0)
                .lang(1)
                .user_semantics("{\"client_id\":\"orion.ovs.client.1508751991541\",\"cookies\":{\"personality_name\":\"小雅\",\"character_type\":\"0\"},\"version\":\"1.9.07\",\"device_type\":\"2\",\"deviceid\":\"XY77C0033E\",\"user_id\":\"19481402\",\"imei\":\"012345678912345\",\"ip\":\"61.135.33.58\",\"is_ask_free\":\"false\",\"lat\":\"39.932453\",\"lng\":\"116.459253\",\"os_type\":\"android\",\"union_access_token\":\"eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vYXBpLmNoaWxkLmNtY20uY29tIiwiaWF0IjoxNTQwMjY3MTIzLCJ1c2VySWQiOjI1fQ.M5oje9vQ4RjknL23f5j-GYGFRjZRxbEnv8vKv41KgHA\",\"ovs_sdk_os\":\"android\",\"ovs_sdk_version\":\"96\",\"ovs_sdk_version_name\":\"1.3.96\",\"date\":1541733815643,\"dt\":1541733815643,\"os_version\":19}u0026sign=105fb7541e1c9678081804ba7eb72f80\",\"ver\":\"2.1.0.2\"}")
                .build();

        System.out.println(request.toString());
        System.out.println(JSON.toJSONString(request));
    }
}
