# RPL OF0 vs MRHOF — Contiki-NG

[![Tiếng Việt](https://img.shields.io/badge/Ti%E1%BA%BFng_Vi%E1%BB%87t-2ea44f?style=for-the-badge)](#vietnamese) [![English](https://img.shields.io/badge/English-0969da?style=for-the-badge)](#english)

> Chọn ngôn ngữ ở trên để chuyển nhanh đến nội dung tương ứng. / Select a language above to jump to its section.

---

## Vietnamese

### 1. Tổng quan

So sánh hai hàm mục tiêu của giao thức định tuyến RPL: **OF0** và **MRHOF** trên **Cooja (Contiki-NG)** và **FIT IoT-LAB**.

- **Cooja:** 15 nút (1 root, 14 client); 3 topology (Line, Grid, Random); 5 lần chạy/trường hợp; cửa sổ phân tích 300 giây.
- **FIT IoT-LAB:** 15 nút M3 tại Grenoble (`m3-207` là root; `m3-208`–`m3-221` là client); lưu log riêng.
- **Chỉ số:** PDR, độ trễ một chiều (client → root), số hop ước lượng, số lần đổi preferred parent (không tính lần chọn ban đầu).

### 2. Cấu trúc thư mục

- `cooja/OF0/`, `cooja/MRHOF/`: mã nguồn và cấu hình hai thuật toán.
- `cooja/topology/`: các file mô phỏng `.csc`.
- `fit-iotlab/`: mã nguồn cho M3; `logs/`: log Cooja và IoT-LAB.
- `scripts/analyze_logs.py`: script xử lý log; `results/`: kết quả CSV của Cooja.

### 3. Cách chạy mô phỏng

1. Chép `cooja/OF0/` vào `contiki-ng/examples/rpl-of0/` và `cooja/MRHOF/` vào `contiki-ng/examples/rpl-mrhof/`.
2. Trong file `.csc`, sửa **hai dòng `<source>`** để trỏ tới đúng mã nguồn server và client (thay `[CONTIKI_DIR]` bằng đường dẫn Contiki-NG trên máy):

   **OF0**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-client.c</source>
   ```
   **MRHOF**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-client.c</source>
   ```
3. Chạy Cooja: `cd ~/contiki-ng/tools/cooja && ./gradlew run`, chọn **File → Open simulation**, mở file `.csc` và biên dịch lại mote khi cần.
4. Kiểm tra log: **OCP 0 = OF0**, **OCP 1 = MRHOF**.
5. Tạo lại CSV từ log (chạy ở thư mục gốc dự án):
   ```bash
   python3 scripts/analyze_logs.py --logs logs/cooja --out results --window-seconds 300
   ```

### 4. Kết quả Cooja

Giá trị trung bình qua 5 lần chạy mỗi trường hợp:

| Topology | OF | PDR (%) | Delay (ms) | Hops* | Đổi parent |
|---|---|---:|---:|---:|---:|
| Line | OF0 | 99.817 | 100.383 | 3.738 | 5.4 |
| Line | MRHOF | 100.000 | 99.511 | 3.733 | 0.0 |
| Grid | OF0 | 99.942 | 81.845 | 3.086 | 3.8 |
| Grid | MRHOF | 99.943 | 81.028 | 3.084 | 0.0 |
| Random | OF0 | 99.941 | 94.954 | 3.497 | 5.4 |
| Random | MRHOF | 100.000 | 94.467 | 3.477 | 0.0 |

*Hop Count được ước lượng từ log. Cả hai có PDR gần 100%; MRHOF ít đổi parent hơn trong các trường hợp đã thử, nhưng chênh lệch Delay/Hops nhỏ.*

### 5. Hạn chế và hướng phát triển

- Chỉ 15 nút và 300 giây phân tích; chưa đánh giá khả năng mở rộng và ổn định dài hạn.
- Radio Cooja đặt `success_ratio_tx = 1.0`, `success_ratio_rx = 1.0`; chưa thử liên kết suy hao đáng kể.
- Năm lần chạy của cùng topology có **vị trí nút giống nhau**; chưa thử nhiều bố trí độc lập, tải cao hoặc nút di chuyển.
- Hop Count chỉ là **ước lượng từ log**; MRHOF không đổi parent trong log hiện tại **không có nghĩa** thuật toán luôn không đổi parent.
- Chưa đo tiêu thụ năng lượng, routing overhead, network lifetime; chưa đối chiếu định lượng trực tiếp với kết quả FIT IoT-LAB.

**Kết luận:** Với các điều kiện đã mô phỏng, OF0 và MRHOF có PDR tương đương; MRHOF có Delay thấp hơn đôi chút và ít đổi parent hơn. **Không thể kết luận MRHOF luôn tốt hơn OF0.** Nên mở rộng số nút, thời gian, chất lượng liên kết và tải mạng, đồng thời bổ sung chỉ số năng lượng.

**[🇬🇧 Switch to English](#english) · [⬆ Back to language selection](#rpl-of0-vs-mrhof--contiki-ng)**

---

## English

### 1. Overview

This project compares two RPL objective functions, **Objective Function Zero (OF0)** and **Minimum Rank with Hysteresis Objective Function (MRHOF)**, using **Cooja (Contiki-NG)** and **FIT IoT-LAB**.

- **Cooja:** 15 nodes (1 root, 14 clients); 3 topologies (Line, Grid, Random); 5 runs per case; 300-second analysis window.
- **FIT IoT-LAB:** 15 M3 nodes at Grenoble (`m3-207` as root; `m3-208`–`m3-221` as clients), with separately stored logs.
- **Metrics:** PDR, one-way delay (client → root), estimated hop count, and preferred-parent changes (excluding initial selection).

### 2. Project structure

- `cooja/OF0/`, `cooja/MRHOF/`: source code and configurations for each objective function.
- `cooja/topology/`: Cooja simulation files (`.csc`).
- `fit-iotlab/`: M3 source code; `logs/`: Cooja and IoT-LAB logs.
- `scripts/analyze_logs.py`: log analysis script; `results/`: Cooja CSV results.

### 3. Run Cooja simulations

1. Copy `cooja/OF0/` into `contiki-ng/examples/rpl-of0/` and `cooja/MRHOF/` into `contiki-ng/examples/rpl-mrhof/`.
2. Edit **both `<source>` entries** (server and client) in each `.csc` file. Replace `[CONTIKI_DIR]` with the local Contiki-NG path:

   **OF0**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-client.c</source>
   ```
   **MRHOF**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-client.c</source>
   ```
3. Start Cooja with `cd ~/contiki-ng/tools/cooja && ./gradlew run`. Select **File → Open simulation**, load a `.csc` file, and recompile motes if needed.
4. Verify logs: **OCP 0 = OF0**, **OCP 1 = MRHOF**.
5. Regenerate the CSV results from the project root:
   ```bash
   python3 scripts/analyze_logs.py --logs logs/cooja --out results --window-seconds 300
   ```

### 4. Cooja results

Mean values across five runs per case:

| Topology | OF | PDR (%) | Delay (ms) | Hops* | Parent changes |
|---|---|---:|---:|---:|---:|
| Line | OF0 | 99.817 | 100.383 | 3.738 | 5.4 |
| Line | MRHOF | 100.000 | 99.511 | 3.733 | 0.0 |
| Grid | OF0 | 99.942 | 81.845 | 3.086 | 3.8 |
| Grid | MRHOF | 99.943 | 81.028 | 3.084 | 0.0 |
| Random | OF0 | 99.941 | 94.954 | 3.497 | 5.4 |
| Random | MRHOF | 100.000 | 94.467 | 3.477 | 0.0 |

*Hop Count is estimated from RPL logs. Both functions achieved nearly 100% PDR. MRHOF showed fewer parent changes in these runs, while differences in delay and hop count were small.*

### 5. Limitations and future work

- Only 15 nodes and a 300-second analysis window; scalability and long-term stability remain untested.
- Cooja used `success_ratio_tx = 1.0` and `success_ratio_rx = 1.0`; substantially degraded links were not evaluated.
- The five runs within each topology used **identical node positions**; independent layouts, heavy traffic, and mobility were not examined.
- Hop count is **estimated from logs**. Zero parent changes for MRHOF in these runs **does not mean** MRHOF never changes parents.
- Energy consumption, routing overhead, and network lifetime were not measured; Cooja and FIT IoT-LAB results were not directly compared quantitatively.

**Conclusion:** Under the tested conditions, OF0 and MRHOF achieved similar PDR. MRHOF showed slightly lower delay and fewer parent changes. **These results do not prove MRHOF is always better than OF0.** Future work should test larger and longer-running networks, degraded links, different traffic loads, and energy-related metrics.

**[🇻🇳 Chuyển sang Tiếng Việt](#vietnamese) · [⬆ Back to language selection](#rpl-of0-vs-mrhof--contiki-ng)**
