#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SPI.h>
#include <DW1000Ranging.h>
#include <WiFi.h>
#include "link.h"

#define TAG_ADDR "7D:00:22:EA:82:60:3B:9C"

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define UWB_RST 27 // reset pin
#define UWB_IRQ 34 // irq pin
#define UWB_SS 21  // spi select pin

#define I2C_SDA 4
#define I2C_SCL 5

const char *ssid = "OPPO_Reno7"; //wifi帳號
const char *password = "12345678";//wifi密碼
const char *host = "192.168.46.135";//連線的主機IP
// const char *ssid = "HITRON-6h_EXT"; //wifi帳號
// const char *password = "0989887781";//wifi密碼
// const char *host = "192.168.0.11";//連線的主機IP
// const char *ssid = "Lab519_5G"; //wifi帳號
// const char *password = "lab519wifi";//wifi密碼
// const char *host = "192.168.0.145";//連線的主機IP
const int port = 80;

WiFiClient client;

struct MyLink *uwb_data;
int index_num = 0;
long runtime = 0;
String all_json = "";

Adafruit_SSD1306 display(128, 64, &Wire, -1);

// 儲存每個設備距離的全局變量
#define MAX_DEVICES 10
float ranges[MAX_DEVICES] = {0};
uint16_t addresses[MAX_DEVICES] = {0};
int num_devices = 0;

void setup() {
    Serial.begin(115200);

    Wire.begin(I2C_SDA, I2C_SCL);
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println(F("SSD1306 allocation failed"));
        for (;;);
    }
    display.clearDisplay();

    logoshow();

    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);

    // UWB init
    DW1000Ranging.initCommunication(UWB_RST, UWB_SS, UWB_IRQ); // Reset, CS, IRQ pin
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);
    DW1000Ranging.startAsTag(TAG_ADDR, DW1000.MODE_LONGDATA_RANGE_LOWPOWER);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected");
    Serial.print("IP Address:");
    Serial.println(WiFi.localIP());

    if (client.connect(host, port)) {
        Serial.println("Success");
        client.print(String("GET /") + " HTTP/1.1\r\n" +
                     "Host: " + host + "\r\n" +
                     "Connection: close\r\n" +
                     "\r\n");
    }

    uwb_data = init_link();
}

void loop() {
    DW1000Ranging.loop();
    if ((millis() - runtime) > 1000) {
        if (num_devices == 0) {
            display_no_anchor();
        } else {
            display_uwb();
        }
        make_link_json(ranges, addresses, num_devices, &all_json);
        send_udp(&all_json);
        runtime = millis();
    }
}

void newRange() {
    char c[30];
    DW1000Device* device = DW1000Ranging.getDistantDevice();
    uint16_t address = device->getShortAddress();
    float range = device->getRange();

    Serial.print("from: ");
    Serial.print(address, HEX);
    Serial.print("\t Range: ");
    Serial.print(range);
    Serial.print(" m");
    Serial.print("\t RX power: ");
    Serial.print(device->getRXPower());
    Serial.println(" dBm");

    fresh_link(uwb_data, address, range, device->getRXPower());

    // 更新全局變量中的距離數據
    bool found = false;
    for (int i = 0; i < num_devices; i++) {
        if (addresses[i] == address) {
            ranges[i] = range;
            found = true;
            break;
        }
    }
    if (!found && num_devices < MAX_DEVICES) {
        addresses[num_devices] = address;
        ranges[num_devices] = range;
        num_devices++;
    }
}

void newDevice(DW1000Device *device) {
    Serial.print("ranging init; 1 device added ! -> ");
    Serial.print(" short:");
    Serial.println(device->getShortAddress(), HEX);

    add_link(uwb_data, device->getShortAddress());
}

void inactiveDevice(DW1000Device *device) {
    Serial.print("delete inactive device: ");
    Serial.println(device->getShortAddress(), HEX);

    delete_link(uwb_data, device->getShortAddress());

    // 當設備變得不活躍時，從全局變量中移除對應的數據
    for (int i = 0; i < num_devices; i++) {
        if (addresses[i] == device->getShortAddress()) {
            // 將最後一個設備覆蓋到這個位置，並減少設備數量
            addresses[i] = addresses[num_devices - 1];
            ranges[i] = ranges[num_devices - 1];
            num_devices--;
            break;
        }
    }
}

void send_udp(String *msg_json) {
    if (client.connected()) {
        client.print(*msg_json);
        Serial.println("UDP send");
    }
}

// LCD display
void logoshow(void) {
    display.clearDisplay();

    display.setTextSize(2);              // Normal 1:1 pixel scale
    display.setTextColor(SSD1306_WHITE); // Draw white text
    display.setCursor(0, 0);             // Start at top-left corner
    display.println(F("Makerfabs"));

    display.setTextSize(1);
    display.setCursor(0, 20); // Start at top-left corner
    display.println(F("DW1000 DEMO"));
    display.display();
    delay(2000);
}

void display_uwb() {
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);

    for (int i = 0; i < num_devices; i++) {
        char c[30];
        sprintf(c, "%.1fm %x", ranges[i], addresses[i]);
        display.setTextSize(2);
        display.setCursor(0, i * 32); // Start at top-left corner
        display.println(c);

        if (i >= 1) // 只顯示最多兩個模組
        {
            break;
        }
    }
    display.display();
}

void display_no_anchor() {
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("No Anchor");
    display.display();
}

void make_link_json(float ranges[], uint16_t addresses[], int num_devices, String *s) {
#ifdef SERIAL_DEBUG
    Serial.println("make_link_json");
#endif
    *s = "{\"links\":[";
    for (int i = 0; i < num_devices; i++) {
        char link_json[50];
        sprintf(link_json, "{\"A\":\"%X\",\"R\":\"%.1f\"}", addresses[i], ranges[i]);
        *s += link_json;
        if (i < num_devices - 1) {
            *s += ",";
        }
    }
    *s += "]}";
    Serial.println(*s);
}