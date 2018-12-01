package sample;

import javafx.application.Platform;
import javafx.beans.property.*;

import java.text.SimpleDateFormat;
import java.util.*;

public class CamInfo {
    private Property<Map<String, Object>> log;
    private StringProperty stringLog;
    private StringProperty alert;
    private long period = 200;
    private String path;

    CamInfo(String path) {
        log = new SimpleObjectProperty<>();
        stringLog = new SimpleStringProperty();
        alert = new SimpleStringProperty();
        this.path = path;
    }

    void start() {
        PropertiesEnumerator pe = new PropertiesEnumerator(path);
        new Timer(true).schedule(
                new TimerTask() {
                    @Override
                    public void run() {
                        if(pe.hasMoreElements()) {
                            Map<String, Object> log_alert = pe.nextElement();
                            alert.setValue((String) log_alert.get("alert"));
                            log_alert.remove("alert");
                            log.setValue(log_alert);
                            Platform.runLater(new Runnable() {
                                @Override
                                public void run() {
                                    stringLog.setValue(logString(log_alert));
                                }
                            });
                        } else
                            cancel();
                    }
                },
                0,
                period
        );
    }

    private String logString(Map<String, Object> log) {
        StringBuilder stringLog = new StringBuilder();
        for(Map.Entry<String, Object> entry : log.entrySet()) {
            stringLog.append(String.format("\n%s: %s", entry.getKey(), entry.getValue().toString()));
        }
        return stringLog.toString();
    }

    Property<Map<String, Object>> getLog() {
        return log;
    }

    StringProperty getStringLog() {
        return stringLog;
    }

    StringProperty getAlert() {
        return alert;
    }
}
