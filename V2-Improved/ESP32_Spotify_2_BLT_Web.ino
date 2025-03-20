#include <Arduino.h>
#include "BluetoothA2DPSink.h"
#include <WiFi.h>
#include <WebServer.h>
#include <math.h>

BluetoothA2DPSink a2dp_sink;
const int LEDS[] = {15, 2, 4}; // LED pins
volatile int max_loudness = 1;  // declared volatile because updated in callback
int led_color[3] = {255, 255, 255};
float brightness = 0.0, alpha = 0.5;

const char *ssid = "ESP32_LED_Control";
const char *password = "password123";
WebServer server(80);

// Flag to control loudness decay (enabled by default)
bool loudnessDecayEnabled = true;

// Optimized audio callback using pointer arithmetic and pre-computed pair count
void audio_data_callback(const uint8_t *data, uint32_t length) {
  int32_t sum = 0;
  const int16_t *samples = reinterpret_cast<const int16_t*>(data);
  uint32_t numPairs = (length / sizeof(int16_t)) / 2;  // only process one channel (left)
  for (uint32_t i = 0; i < numPairs; i++) {
    sum += abs(samples[i * 2]);
  }
  int avg = numPairs ? sum / numPairs : 0;
  
  // Update max loudness and apply smoothing to brightness
  max_loudness = (avg > max_loudness ? avg : max_loudness);
  brightness = alpha * ((float)avg / max_loudness) + (1 - alpha) * brightness;
  
  // Perceptual scaling by squaring brightness and limiting to 255
  int led_brightness = constrain((int)(brightness * brightness * 255), 0, 255);
  
  // Loop through each LED channel
  for (uint8_t i = 0; i < 3; i++) {
    analogWrite(LEDS[i], (led_brightness * led_color[i]) / 255);
  }
}

// HTML page stored in flash memory (PROGMEM) to reduce RAM usage
const char PAGE_COLOR_WHEEL[] PROGMEM = R"rawliteral(
<html>
  <head>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
      body { font-family: Arial, sans-serif; text-align: center; margin: 20px; }
      #colorWheel { border: 1px solid #000; touch-action: none; }
      #colorPreview { width: 100px; height: 100px; margin: 20px auto; border: 2px solid #000; }
      .toggle-container { margin: 20px; }
    </style>
  </head>
  <body>
    <h1>ESP32 Color Picker</h1>
    <canvas id='colorWheel' width='300' height='300'></canvas><br>
    <label for='brightness'>Brightness:</label>
    <input type='range' id='brightness' min='0' max='255' value='255'><br>
    <div id='colorPreview'></div>
    <p>Current Color: <span id='colorValue'>rgb(255,255,255)</span></p>
    
    <!-- Toggle for loudness decay -->
    <div class="toggle-container">
      <label for="loudnessDecayToggle">Enable Loudness Decay:</label>
      <input type="checkbox" id="loudnessDecayToggle" checked>
    </div>

    <script>
      function hsvToRgb(h, s, v) {
        var r, g, b, i, f, p, q, t;
        i = Math.floor(h * 6);
        f = h * 6 - i;
        p = v * (1 - s);
        q = v * (1 - f * s);
        t = v * (1 - (1 - f) * s);
        switch(i % 6) {
          case 0: r = v; g = t; b = p; break;
          case 1: r = q; g = v; b = p; break;
          case 2: r = p; g = v; b = t; break;
          case 3: r = p; g = q; b = v; break;
          case 4: r = t; g = p; b = v; break;
          case 5: r = v; g = p; b = q; break;
        }
        return [Math.round(r*255), Math.round(g*255), Math.round(b*255)];
      }

      var canvas = document.getElementById('colorWheel');
      var ctx = canvas.getContext('2d');
      var wheelRadius = canvas.width / 2;
      var currentHue = 0, currentSat = 0, currentBright = 1;
      
      function drawColorWheel() {
        var width = canvas.width, height = canvas.height;
        var imageData = ctx.createImageData(width, height);
        var data = imageData.data;
        var cx = wheelRadius, cy = wheelRadius;
        for (var y = 0; y < height; y++) {
          for (var x = 0; x < width; x++) {
            var dx = x - cx, dy = y - cy;
            var r = Math.sqrt(dx*dx + dy*dy);
            var index = (y * width + x) * 4;
            if (r > wheelRadius) {
              data[index+3] = 0;
            } else {
              var angle = Math.atan2(dy, dx);
              if (angle < 0) angle += 2*Math.PI;
              var hue = angle / (2*Math.PI);
              var sat = r / wheelRadius;
              var rgb = hsvToRgb(hue, sat, 1);
              data[index] = rgb[0];
              data[index+1] = rgb[1];
              data[index+2] = rgb[2];
              data[index+3] = 255;
            }
          }
        }
        ctx.putImageData(imageData, 0, 0);
      }

      function pickColor(e) {
        var rect = canvas.getBoundingClientRect();
        var x = (e.clientX || e.touches[0].clientX) - rect.left;
        var y = (e.clientY || e.touches[0].clientY) - rect.top;
        var cx = canvas.width / 2, cy = canvas.height / 2;
        var dx = x - cx, dy = y - cy;
        var r = Math.sqrt(dx*dx + dy*dy);
        if (r > wheelRadius) return;
        var angle = Math.atan2(dy, dx);
        if (angle < 0) angle += 2*Math.PI;
        currentHue = angle / (2*Math.PI);
        currentSat = r / wheelRadius;
        currentBright = document.getElementById('brightness').value / 255;
        var rgb = hsvToRgb(currentHue, currentSat, currentBright);
        updateColor(rgb);
      }

      function updateColor(rgb) {
        var color = 'rgb(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ')';
        document.getElementById('colorPreview').style.backgroundColor = color;
        document.getElementById('colorValue').textContent = color;
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/setcolor?r=' + rgb[0] + '&g=' + rgb[1] + '&b=' + rgb[2], true);
        xhr.send();
      }

      function brightnessChanged() {
        currentBright = document.getElementById('brightness').value / 255;
        var rgb = hsvToRgb(currentHue, currentSat, currentBright);
        updateColor(rgb);
      }

      // Function to handle loudness decay toggle
      function toggleLoudnessDecay() {
        var isChecked = document.getElementById('loudnessDecayToggle').checked;
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/setLoudnessDecay?enabled=' + isChecked, true);
        xhr.send();
      }

      drawColorWheel();
      canvas.addEventListener('click', pickColor);
      canvas.addEventListener('touchstart', function(e) { pickColor(e); });
      document.getElementById('brightness').addEventListener('input', brightnessChanged);
      document.getElementById('loudnessDecayToggle').addEventListener('change', toggleLoudnessDecay);
    </script>
  </body>
</html>
)rawliteral";

// Serve the color picker page
void handleRoot() {
  server.send(200, "text/html", PAGE_COLOR_WHEEL);
}

// Update the LED color based on GET parameters
void handleSetColor() {
  if (server.hasArg("r")) led_color[0] = server.arg("r").toInt();
  if (server.hasArg("g")) led_color[1] = server.arg("g").toInt();
  if (server.hasArg("b")) led_color[2] = server.arg("b").toInt();
  server.send(200, "text/plain", "Color Updated");
}

// Handle toggling loudness decay
void handleSetLoudnessDecay() {
  if (server.hasArg("enabled")) {
    loudnessDecayEnabled = server.arg("enabled") == "true";
  }
  server.send(200, "text/plain", "Loudness Decay Updated");
}

void reconnect() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Reconnecting to WiFi...");
    WiFi.reconnect();
  }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 3; i++) {
    pinMode(LEDS[i], OUTPUT);
  }
  WiFi.softAP(ssid, password);
  server.on("/", handleRoot);
  server.on("/setcolor", handleSetColor);
  server.on("/setLoudnessDecay", handleSetLoudnessDecay);
  server.begin();
  
  // I2S configuration: declared as static const for potential optimization
  static const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX | I2S_MODE_DAC_BUILT_IN),
    .sample_rate = 44100,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_MSB,
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 64,
    .use_apll = false
  };
  a2dp_sink.set_i2s_config(i2s_config);
  a2dp_sink.set_stream_reader(audio_data_callback);
  a2dp_sink.start("ESP32_Bluetooth");
}

void loop() {
  reconnect();  // Ensure the device is connected to WiFi
  server.handleClient();
  
  // Gradually decay max_loudness if decay is enabled
  if (loudnessDecayEnabled) {
    max_loudness = (max_loudness > 1) ? (max_loudness - 1) : 1;
  }
}
