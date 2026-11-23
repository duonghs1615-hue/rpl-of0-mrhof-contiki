# RPL OF0 vs MRHOF — Contiki-NG

[![Tiếng Việt](https://img.shields.io/badge/Ti%E1%BA%BFng_Vi%E1%BB%87t-2ea44f?style=for-the-badge)](#vietnamese) [![English](https://img.shields.io/badge/English-0969da?style=for-the-badge)](#english)

---

## Vietnamese

### Tổng quan

So sánh **RPL OF0** và **MRHOF** trên **Contiki-NG/Cooja** và kiểm chứng trên **FIT IoT-LAB**.

- **Cooja:** 15 node (1 root, 14 client), 3 topology (**Line, Grid, Random**), 5 seed mỗi cấu hình (**101, 202, 303, 404, 123456**).
- **Đánh giá:** PDR, Delay, Hop Count và Parent Changes trong **300 giây đầu** của mỗi log.
- **FIT IoT-LAB:** 15 node M3 tại Grenoble; log lưu riêng, không được script Cooja phân tích.

### Chạy phân tích log

Từ thư mục gốc dự án trên Ubuntu:

```bash
cd ~/rpl-of0-mrhof-contiki
python3 scripts/analyze_logs.py
```

Script tự đọc toàn bộ `.log` trong `logs/cooja/` và dùng khoảng thời gian **[0, 300) giây** (mặc định, không cần thêm tham số). **Lệnh này chỉ phân tích log có sẵn, không chạy lại Cooja.**

Kết quả được ghi vào:

- `results/cooja_runs.csv`: từng file log/seed, có tên file và các cột **Sent, Raw Rx, Unique Rx, Dup Rx, PDR, Delay, Hop Count, Parent Changes**.
- `results/cooja_summary.csv`: **trung bình và độ lệch chuẩn** qua 5 seed của từng topology và OF.

Mở bằng LibreOffice Calc:

```bash
libreoffice --calc results/cooja_runs.csv
libreoffice --calc results/cooja_summary.csv
```

**Giải thích:** `Raw Rx` = tổng sự kiện nhận ghi trong log; `Unique Rx` = gói nhận ghép được với gói gửi (không tính trùng); `Dup Rx` = bản ghi nhận trùng. **PDR = Unique Rx / Sent × 100%**. `OCP 0` = OF0; `OCP 1` = MRHOF. Seed được lấy từ **tên file log**. Hop Count là **ước lượng từ sự kiện chuyển tiếp RPL**, không phải số hop đã xác minh tuyệt đối cho mọi gói. Các dòng `NOTE/WARNING` chỉ ra bản ghi trùng, gói nhận sau 300 giây hoặc sự kiện chuyển tiếp lặp, cần xem khi diễn giải số liệu.

### Chạy lại mô phỏng Cooja (nếu cần)

1. Chép `Makefile`, `project-conf.h`, `udp-client.c`, `udp-server.c` từ `cooja/OF0/` vào `contiki-ng/examples/rpl-of0/`; làm tương tự từ `cooja/MRHOF/` vào `contiki-ng/examples/rpl-mrhof/`.
2. Mở file `.csc` trong `cooja/topology/`. Hai dòng `<source>` đang trỏ tới `examples/rpl-udp/` cần được đổi thành **`examples/rpl-of0/`** hoặc **`examples/rpl-mrhof/`** cho cả `udp-client.c` và `udp-server.c`. Giữ nguyên biến `[CONTIKI_DIR]`. Nên lưu `.csc` riêng cho từng OF.
3. Mở Cooja bằng `cd ~/contiki-ng/tools/cooja && ./gradlew run`, nạp mô phỏng và biên dịch lại mote nếu cần. Kiểm tra OCP trong log để xác nhận OF.

### Kiểm chứng trên FIT IoT-LAB (phần cứng thật)

- **Nền tảng:** 15 node **M3 tại Grenoble**; `m3-207` là RPL Root, `m3-208` đến `m3-221` là 14 UDP client.
- **Cấu hình:** hai bộ mã nguồn riêng tại `fit-iotlab/OF0/` và `fit-iotlab/MRHOF/` (khác nhau ở `RPL_CONF_OF_OCP` trong `project-conf.h`). Firmware `.iotlab` đã lưu tại `logs/fit-iotlab/OF0/` và `logs/fit-iotlab/MRHOF/`.
- **Thực hiện:** nạp firmware server cho Root, firmware client cho 14 node còn lại bằng FIT IoT-LAB; thu log serial cho từng OF trong khoảng **300 giây**. Ví dụ lệnh thu log: `timeout 300 serial_aggregator -i <experiment_id> | tee rpl-of0.log` (thay tên file cho MRHOF).

| Chỉ số | OF0 | MRHOF |
|---|---:|---:|
| Gói gửi / Root nhận | 420 / 420 | 417 / 417 |
| PDR uplink | 100% | 100% |
| Hop Count | 1 | 1 |
| Parent Changes | 0 | 0 |

Log gốc: `logs/fit-iotlab/OF0/iotlab-of0.log` và `logs/fit-iotlab/MRHOF/iotlab-mrhof.log`. **Script `scripts/analyze_logs.py` chỉ xử lý log Cooja**, không phân tích log FIT IoT-LAB. Không so sánh Delay của FIT IoT-LAB vì timestamp thu qua `serial_aggregator` không phải phép đo trễ đầu cuối đáng tin cậy. Trong thử nghiệm này, các node gần Root nên đường uplink chủ yếu trực tiếp **1 hop**; kết quả phần cứng giúp kiểm chứng hoạt động nhưng chưa thể hiện ưu thế định tuyến nhiều hop của thuật toán nào.

### Kết quả và hạn chế

| Topology | OF | PDR TB (%) | Delay TB (ms) | Hop TB* | Đổi parent TB |
|---|---|---:|---:|---:|---:|
| Line | OF0 | 99.817 | 100.383 | 3.738 | 5.4 |
| Line | MRHOF | 100.000 | 99.511 | 3.733 | 0.0 |
| Grid | OF0 | 99.942 | 81.845 | 3.086 | 3.8 |
| Grid | MRHOF | 99.943 | 81.028 | 3.084 | 0.0 |
| Random | OF0 | 99.941 | 94.954 | 3.497 | 5.4 |
| Random | MRHOF | 100.000 | 94.467 | 3.477 | 0.0 |

*Trung bình của 5 seed; độ lệch chuẩn có trong `cooja_summary.csv`. Hop Count là giá trị ước lượng.*

**Hạn chế:** chỉ 15 node và 300 giây; radio mô phỏng cấu hình xác suất thành công truyền/nhận bằng 1.0; 5 seed cùng topology giữ nguyên vị trí node; chưa đánh giá suy hao mạnh, tải cao, năng lượng hay độ ổn định dài hạn. **MRHOF ít đổi parent hơn trong các thử nghiệm này**, nhưng không có cơ sở kết luận luôn tốt hơn OF0.


[🇬🇧 English](#english) · [⬆ Chọn ngôn ngữ](#rpl-of0-vs-mrhof--contiki-ng)

---

## English

### Overview

Comparison of **RPL OF0** and **MRHOF** using **Contiki-NG/Cooja**, with additional **FIT IoT-LAB** validation.

- **Cooja:** 15 nodes (1 root, 14 clients), 3 topologies (**Line, Grid, Random**), 5 seeds per configuration (**101, 202, 303, 404, 123456**).
- **Metrics:** PDR, delay, hop count, and preferred-parent changes within the **first 300 seconds** of each log.
- **FIT IoT-LAB:** 15 M3 nodes in Grenoble; hardware logs are stored separately and are not processed by the Cooja analyzer.

### Analyze existing logs

Run from the repository root on Ubuntu:

```bash
cd ~/rpl-of0-mrhof-contiki
python3 scripts/analyze_logs.py
```

The script reads `.log` files under `logs/cooja/` and analyzes the **[0, 300)-second** window by default. **It processes existing logs; it does not start a Cooja simulation.**

Outputs:

- `results/cooja_runs.csv`: per-run and per-seed data, including file name, **Sent, Raw Rx, Unique Rx, Dup Rx, PDR, Delay, Hop Count, and Parent Changes**.
- `results/cooja_summary.csv`: **mean and standard deviation** across five seeds for each topology/objective function.

Open in LibreOffice Calc:

```bash
libreoffice --calc results/cooja_runs.csv
libreoffice --calc results/cooja_summary.csv
```

**Definitions:** `Raw Rx` counts all reception log events; `Unique Rx` counts matched deliveries excluding duplicates; `Dup Rx` counts duplicate receptions. **PDR = Unique Rx / Sent × 100%**. `OCP 0` identifies OF0; `OCP 1` identifies MRHOF. Seeds are parsed from **log filenames**. Hop count is an **estimate from RPL forwarding events**, not a verified exact path length for every packet. `NOTE/WARNING` messages flag duplicates, receptions after 300 seconds, or repeated forwarding events.

### Rerun Cooja simulations (optional)

1. Copy `Makefile`, `project-conf.h`, `udp-client.c`, and `udp-server.c` from `cooja/OF0/` into `contiki-ng/examples/rpl-of0/`; copy the MRHOF counterparts into `contiki-ng/examples/rpl-mrhof/`.
2. Open a `.csc` file under `cooja/topology/`. Change the two `<source>` entries for `udp-client.c` and `udp-server.c` from `examples/rpl-udp/` to **`examples/rpl-of0/`** or **`examples/rpl-mrhof/`**, matching the OF. Keep `[CONTIKI_DIR]` unchanged. Separate `.csc` copies are recommended.
3. Start Cooja with `cd ~/contiki-ng/tools/cooja && ./gradlew run`, load the simulation, and recompile motes if required. Verify the OCP in the logs.

### FIT IoT-LAB validation (real hardware)

- **Platform:** 15 **M3 nodes at Grenoble**; `m3-207` is the RPL root and `m3-208`–`m3-221` are 14 UDP clients.
- **Configuration:** separate sources in `fit-iotlab/OF0/` and `fit-iotlab/MRHOF/` (selected through `RPL_CONF_OF_OCP` in `project-conf.h`). Built `.iotlab` firmware is included in `logs/fit-iotlab/OF0/` and `logs/fit-iotlab/MRHOF/`.
- **Procedure:** flash server firmware to the root and client firmware to the other 14 nodes through FIT IoT-LAB; capture serial logs for each OF for **300 seconds**. Example capture command: `timeout 300 serial_aggregator -i <experiment_id> | tee rpl-of0.log` (change output name for MRHOF).

| Metric | OF0 | MRHOF |
|---|---:|---:|
| Sent / received at root | 420 / 420 | 417 / 417 |
| Uplink PDR | 100% | 100% |
| Hop count | 1 | 1 |
| Parent changes | 0 | 0 |

Raw logs: `logs/fit-iotlab/OF0/iotlab-of0.log` and `logs/fit-iotlab/MRHOF/iotlab-mrhof.log`. **`scripts/analyze_logs.py` processes Cooja logs only**, not FIT IoT-LAB data. FIT IoT-LAB delay is not compared because timestamps collected by `serial_aggregator` do not reliably measure end-to-end delay. The nodes were close enough to the root for mainly **single-hop uplink** routes; the hardware experiment validates operation but does not establish which OF performs better in multi-hop conditions.

### Results and limitations

| Topology | OF | Mean PDR (%) | Mean delay (ms) | Mean hops* | Mean parent changes |
|---|---|---:|---:|---:|---:|
| Line | OF0 | 99.817 | 100.383 | 3.738 | 5.4 |
| Line | MRHOF | 100.000 | 99.511 | 3.733 | 0.0 |
| Grid | OF0 | 99.942 | 81.845 | 3.086 | 3.8 |
| Grid | MRHOF | 99.943 | 81.028 | 3.084 | 0.0 |
| Random | OF0 | 99.941 | 94.954 | 3.497 | 5.4 |
| Random | MRHOF | 100.000 | 94.467 | 3.477 | 0.0 |

*Means across five seeds; standard deviations are available in `cooja_summary.csv`. Hop count is estimated.*

**Limitations:** 15 nodes and a 300-second window; radio transmission/reception success probabilities configured to 1.0; identical node positions across seeds within each topology; degraded links, heavy traffic, energy use, and long-term stability were not evaluated. **MRHOF showed fewer parent changes in these runs**, but these results do not establish universal superiority over OF0.


[🇻🇳 Tiếng Việt](#vietnamese) · [⬆ Language selection](#rpl-of0-vs-mrhof--contiki-ng)
