package sample;

import javafx.beans.binding.Bindings;
import javafx.beans.property.DoubleProperty;
import javafx.fxml.FXML;
import javafx.scene.control.Label;
import javafx.scene.layout.Background;
import javafx.scene.layout.BackgroundFill;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;
import javafx.scene.media.MediaView;

import java.awt.*;
import java.io.File;

public class Controller {
    public VBox camera;
    public Pane video;
    private String video_path = "/mnt/E/Hack/l_05_persons_0_smoke_1_01.mp4";
    private CamInfo camInfo = new CamInfo("/mnt/E/Hack/l_05_persons_0_smoke_1_01.log");
    public Label info;

    @FXML
    protected void initialize() {
        final File f = new File(video_path);
        final Media m = new Media(f.toURI().toString());
        final MediaPlayer mp = new MediaPlayer(m);
        final MediaView mv = new MediaView(mp);
        mv.setFitWidth(500);
        video.getChildren().add(mv);

        info.textProperty().bind(camInfo.getStringLog());
        camInfo.getAlert().addListener((observable, oldValue, newValue) -> {
            if(newValue.isEmpty())
                video.setStyle("-fx-background-color: rgba(0,0,0,0.41);");
            else
                video.setStyle("-fx-background-color: rgba(255,0,0,0.76);");
        });

        mp.play();
        camInfo.start();
    }
}
