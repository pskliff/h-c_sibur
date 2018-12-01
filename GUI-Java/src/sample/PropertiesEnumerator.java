package sample;

import org.json.*;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class PropertiesEnumerator implements Enumeration<Map<String, Object>> {
    private JSONArray arr;
    private int i = 0;
    public PropertiesEnumerator(String path) {
        try {
            arr = new JSONArray(readFile(path, StandardCharsets.UTF_8));
            System.out.println("OK");
        } catch (Exception e) {
            arr = null;
        }
    }

    @Override
    public boolean hasMoreElements() {
        return arr != null && i < arr.length();
    }

    @Override
    public Map<String, Object> nextElement() {
        Map<String, Object> res = new HashMap<String, Object>();
        try {
            JSONObject obj = arr.getJSONObject(i);
            Iterator keys = obj.keys();
            while (keys.hasNext()) {
                String key = (String) keys.next();
                if(key.equals("alert"))
                    res.put(key, obj.getString(key));
                else
                    res.put(key, obj.getInt(key));
            }
        } catch (Exception ignored) {
            res = new HashMap<String, Object>();
        } finally {
            ++i;
        }
        return res;

    }

    private static String readFile(String path, Charset encoding) throws IOException
    {
        byte[] encoded = Files.readAllBytes(Paths.get(path));
        return new String(encoded, encoding);
    }
}
