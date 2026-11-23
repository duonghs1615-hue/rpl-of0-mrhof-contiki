# RPL OF0 vs MRHOF — Contiki-NG

[![Tiếng Việt](https://img.shields.io/badge/Ti%E1%BA%BFng_Vi%E1%BB%87t-2ea44f?style=for-the-badge)](#vietnamese) [![English](https://img.shields.io/badge/English-0969da?style=for-the-badge)](#english)

> Chọn ngôn ngữ ở trên để chuyển nhanh đến nội dung tương ứng. / Select a language above to jump to its section.
>
> **⚠️ Trước khi chạy:** Cần sửa 2 đường dẫn mã nguồn trong file `.csc` theo mục 3 bên dưới. / **Before running:** Update the 2 source paths in each `.csc` file as described in Section 3.

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

### 3. Cách chạy mô phỏng (lưu ý: phải sửa đường dẫn)

1. Chép **đầy đủ 4 file** (`Makefile`, `project-conf.h`, `udp-server.c`, `udp-client.c`) từ `cooja/OF0/` vào `contiki-ng/examples/rpl-of0/`; làm tương tự với `cooja/MRHOF/` vào `contiki-ng/examples/rpl-mrhof/`.
2. Mở file mô phỏng cần chạy trong **`cooja/topology/*.csc`** bằng trình soạn thảo văn bản. Tìm **2 dòng `<source>`** đang có:
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-udp/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-udp/udp-client.c</source>
   ```
   **Đổi thành một trong hai cặp sau, tùy thuật toán muốn chạy:**

   **OF0:**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-client.c</source>
   ```
   **MRHOF:**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-client.c</source>
   ```
   **Lưu ý:** Giữ nguyên `[CONTIKI_DIR]` vì Cooja dùng ký hiệu này để tham chiếu thư mục cài Contiki-NG. Chỉ cần đổi `rpl-udp` thành `rpl-of0` hoặc `rpl-mrhof` **nếu đã chép mã nguồn vào đúng các thư mục ở bước 1**. Nên lưu thành 2 bản `.csc` riêng để khỏi sửa lại khi đổi thuật toán.
3. Chạy Cooja: `cd ~/contiki-ng/tools/cooja && ./gradlew run`, chọn **File → Open simulation**, mở `.csc` và biên dịch lại mote nếu cần.
4. Kiểm tra log: **OCP 0 = OF0**, **OCP 1 = MRHOF**.
5. Phân tích lại log (chạy tại thư mục gốc dự án):
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

### 3. Run Cooja simulations (important: update source paths)

1. Copy **all four files** (`Makefile`, `project-conf.h`, `udp-server.c`, `udp-client.c`) from `cooja/OF0/` to `contiki-ng/examples/rpl-of0/`; likewise, copy the MRHOF files to `contiki-ng/examples/rpl-mrhof/`.
2. Open the simulation file in **`cooja/topology/*.csc`** with a text editor. Find the **two `<source>` entries**:
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-udp/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-udp/udp-client.c</source>
   ```
   **Replace them with the matching pair for the algorithm:**

   **OF0:**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-of0/udp-client.c</source>
   ```
   **MRHOF:**
   ```xml
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-server.c</source>
   <source>[CONTIKI_DIR]/examples/rpl-mrhof/udp-client.c</source>
   ```
   **Note:** Keep `[CONTIKI_DIR]` unchanged; Cooja uses it as a reference to the Contiki-NG installation. Only change `rpl-udp` to `rpl-of0` or `rpl-mrhof` **after copying the respective source files as in Step 1**. Save separate `.csc` copies for OF0 and MRHOF to avoid switching paths repeatedly.
3. Start Cooja: `cd ~/contiki-ng/tools/cooja && ./gradlew run`, select **File → Open simulation**, load the `.csc` file, and recompile motes if necessary.
4. Verify logs: **OCP 0 = OF0**, **OCP 1 = MRHOF**.
5. Regenerate CSV results from the project root:
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
