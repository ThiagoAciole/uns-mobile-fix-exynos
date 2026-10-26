package org.aciolabs.narutovulkanprobe;

import android.app.Activity;
import android.os.Bundle;
import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.WindowManager;

public final class ProbeActivity extends Activity implements SurfaceHolder.Callback {
    static { System.loadLibrary("vulkanprobe"); }

    private boolean inspected;
    private native void inspect(Surface surface);

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        SurfaceView view = new SurfaceView(this);
        view.getHolder().addCallback(this);
        setContentView(view);
    }

    @Override public void surfaceCreated(SurfaceHolder holder) {
        if (inspected) return;
        inspected = true;
        inspect(holder.getSurface());
        finish();
    }

    @Override public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) { }
    @Override public void surfaceDestroyed(SurfaceHolder holder) { }
}
