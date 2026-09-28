# Pymini — Hướng Dẫn Ngôn Ngữ

Ngôn ngữ biên dịch thẳng sang hợp ngữ nX-U8/100, chạy trên ML620909 (CW/CWX). Biên dịch bằng `pymini2.py`, đóng gói máy nạp được bằng `build.py`.

Tài liệu này chỉ ghi những gì **đã chạy thật, đã test**. Phần chưa xong ghi rõ ở cuối — không giấu.

---

## 1. Cú pháp cơ bản

- Thụt đầu dòng **bắt buộc là bội số của 4 dấu cách**. Tab không dùng được.
- Comment bắt đầu bằng `;`
- Không có dấu `;` cuối dòng lệnh

```
; day la comment
x = 5
if x == 5:
    print("Hello")
```

## 2. Từ khóa

| Pymini | Nghĩa | Ghi chú |
|---|---|---|
| `if` | if | |
| `elf` | elif | |
| `eles` | else | |
| `wh` | while | |
| `def` | def | `def ten():` hoặc `def ten(a, b):` |
| `brk` | break | Thoát vòng `wh` trong cùng |
| `cont` | continue | Nhảy về đầu vòng `wh` trong cùng |

Ví dụ đầy đủ:

```
if x == 1:
    print("mot")
elf x == 2:
    print("hai")
eles:
    print("khac")
```

## 3. Biểu thức và toán tử

Độ ưu tiên như Python: `*` `/` trước `+` `-`, ngoặc `()` ưu tiên cao nhất.

| Toán tử | Ý nghĩa | Ghi chú |
|---|---|---|
| `+` `-` `*` | Cộng, trừ, nhân | Nhân tràn nếu tích > 255 (8-bit) |
| `/` | Chia | **CHIA NGUYÊN**, làm tròn về 0 — không phải chia thực kiểu Python |
| `==` `!=` `<` `>` `<=` `>=` | So sánh | **Chỉ dùng được ngay sau `if`/`elf`/`wh`**, không dùng giữa biểu thức thường |

```
x = (5 + 3) * 2      ; = 16
y = 7 / 2              ; = 3 (chia nguyên, khong phai 3.5)
```

Số thực thật (có phần thập phân) **chưa hỗ trợ** — xem mục 8.

## 4. Biến

Gán biến bằng `=`. Kiểu duy nhất là số nguyên 8-bit (0-255).

```
diem = 0
diem = diem + 10
```

Tên biến bắt đầu bằng chữ hoặc `_`, theo sau là chữ/số/`_`.

## 5. Vẽ hình

Toạ độ màn hình: `x` từ 0-191, `y` từ 0-63.

### `print(chuoi)` / `print(chuoi, x, y)` / `print(chuoi, x, y, cao, dai)`

In chữ dùng font 5x7 gốc, có thể phóng to/thu nhỏ qua `cao`/`dai`.

```
print("Hello")                    ; mac dinh x=10 y=10 cao=7 dai=5
print("Hello", 50, 30)
print("Hello", 50, 30, 14, 10)    ; gap doi kich thuoc
```

Chỉ hỗ trợ ký tự có trong font: chữ hoa A-Z, số 0-9, một số chữ thường và ký hiệu (`. , : ? ! -`). Ký tự lạ báo lỗi biên dịch, không im lặng bỏ qua.

### `circle(x, y, r)` / `rect(x, y, h, w)` / `line(x1, y1, x2, y2)`

Vẽ hình một lần, cố định. **Toạ độ bắt buộc là hằng số** — tính sẵn lúc biên dịch, không nhận biến.

```
circle(96, 32, 20)
rect(10, 10, 20, 30)
line(0, 0, 191, 63)
```

### `render(cao, dai, x, y, ten_hex)`

Vẽ ảnh bitmap từ chuỗi hex đã gán trước bằng biến hex.

```
tron = 187E7EFF        ; gan chuoi hex (khong phai bien so thuong)
render(8, 4, 50, 20, tron)
```

`cao` tối đa 8 (1 byte = 8 hàng). Hình cao hơn phải tách nhiều lần `render()` chồng nhau. Độ dài chuỗi hex phải khớp đúng `dai * 2` ký tự.

## 6. Vật thể di chuyển được: `rect`/`circle` gán vào biến

`rect()`, `circle()` và `line()` có thể gán vào tên biến để di chuyển sau này. (`render()` thì chưa.)

```
box = rect(50, 20, 10, 15)   ; ve ngay luc gan
bong = circle(100, 40, 8)
duong = line(10, 10, 50, 40)
```

### `move(ten, dx, dy)`

Di chuyển vật thể theo độ lệch `dx`, `dy` so với vị trí hiện tại. Tự xoá vị trí cũ, vẽ lại vị trí mới.

```
move(box, 5, 0)      ; sang phai 5px
move(box, -5, 0)     ; sang trai 5px
```

### `moveto(ten, x, y)`

Đặt vật thể vào toạ độ tuyệt đối `x, y`. Với `line`, `x, y` là toạ độ đầu thứ nhất, đầu thứ hai đi theo và độ dài/hướng đoạn thẳng giữ nguyên.

```
moveto(box, 100, 30)
```

### `erase(ten)`

Xoá vật thể khỏi màn hình (không xoá biến, vẫn giữ vị trí trong bộ nhớ).

```
erase(box)
```

`dx`/`dy`/`x`/`y` trong `move`/`moveto` **được phép là biến**, khác với `rect()`/`circle()`/`line()` khi tạo lần đầu (bắt buộc hằng số).

**Lưu ý:** chưa có cắt biên. Toạ độ là số 8-bit không dấu nên đi quá mép trái/trên sẽ quay vòng (`0 - 5 = 251`) và vẽ ra ngoài màn hình. Tự giữ vật thể trong `x` 0-191, `y` 0-63.

## 7. Bàn phím: `key()`

Trả về mã phím đang nhấn, hoặc `"NONE"` nếu không phím nào.

```
if key() == "OK":
    print("Ban da nhan OK")
elf key() == "1":
    print("So 1")
elf key() == "UP":
    move(box, 0, -5)
```

Dùng được trực tiếp trong `if`/`elf`/`wh`, so sánh bằng chuỗi tên phím (không phải mã số).

**Bảng tên phím đầy đủ:**

Số: `"0"`–`"9"`
Chữ: `"A"`–`"Z"`
Đặc biệt: `"HOME"` `"UP"` `"DOWN"` `"LEFT"` `"RIGHT"` `"OK"` `"BACK"` `"SHIFT"` `"VAR"` `"FUNC"` `"CATALOG"` `"TOOLS"` `"SETTINGS"` `"PGUP"` `"PGDOWN"` `"X"` `"FRAC"` `"SQRT"` `"POWER"` `"SQUARED"` `"LOGAB"` `"ANS"` `"SIN"` `"COS"` `"TAN"` `"LEFT_PAREN"` `"RIGHT_PAREN"` `"DEL"` `"AC"` `"MUL"` `"DIV"` `"PLUS"` `"MINUS"` `"DOT"` `"SCI"` `"FORMAT"` `"EXE"` `"NONE"`

`key()` không debounce — gọi liên tục trong vòng `wh` sẽ tự nhiên có hiệu ứng giữ phím. Muốn bắt "chỉ 1 lần nhấn", tự so sánh với biến lưu trạng thái trước đó trong code pymini.

## 8. Chờ: `wait(so_mili_giay)`

Chờ chính xác `so_mili_giây` mili giây, dùng Timer0 phần cứng thật — không phải vòng lặp đếm lệnh đoán chừng.

```
wait(50)      ; cho 50ms
wait(1000)    ; cho 1 giay
```

Giới hạn: `0`–`8000` ms mỗi lần gọi. Cần chờ lâu hơn, gọi `wait()` nhiều lần liên tiếp.

## 9. Hàm: `def`

```
box = rect(50, 20, 10, 15)

def dich(dx, dy):
    move(box, dx, dy)

def ve_khung():
    rect(0, 0, 64, 192)

dich(5, 0)
dich(0, -5)
```

- Tham số là biến riêng của hàm, không đè biến toàn cục trùng tên.
- Hàm gọi hàm, hàm gọi `move()`/`key()`/vẽ hình đều an toàn.
- Số tham số truyền vào phải đúng số tham số khai báo, sai thì báo lỗi biên dịch.
- Hàm **chưa trả giá trị** (không có `return`), chỉ dùng để làm việc.

## 10. Vòng lặp và điều kiện

```
i = 0
wh i < 10:
    print("dem", 10, i * 6)
    i = i + 1
```

`brk` thoát vòng `wh` trong cùng, `cont` nhảy về đầu vòng:

```
i = 0
wh i < 100:
    i = i + 1
    if i == 5:
        cont
    if i == 10:
        brk
```

Vòng lồng nhau: `brk`/`cont` chỉ tác động vòng chứa nó gần nhất. Dùng ngoài `wh` báo lỗi biên dịch.

## 11. Ví dụ đầy đủ: nhấn phím di chuyển ô vuông

```
box = rect(50, 20, 10, 15)
wh 1 == 1:
    if key() == "RIGHT":
        move(box, 5, 0)
    elf key() == "LEFT":
        move(box, -5, 0)
    elf key() == "DOWN":
        move(box, 0, 5)
    elf key() == "UP":
        move(box, 0, -5)
    wait(50)
```

## 12. Biên dịch và nạp máy

```
python3 pymini2.py chuongtrinh.pymini -o out.bin    ; chi sinh .gen.asm + assemble rieng
python3 build.py chuongtrinh.pymini -o out.bin       ; DUNG CAI NAY - ghep boot + clear screen + code
```

Luôn dùng `build.py`, không dùng `pymini2.py` một mình để nạp máy — `pymini2.py` không có phần khởi động chip (boot header), file `.bin` ra sẽ không tự chạy được khi nạp thẳng.

---

## Chưa hỗ trợ — báo lỗi biên dịch rõ ràng, không giả vờ

| Thứ | Ghi chú |
|---|---|
| `print()` số/biến | `print()` chỉ nhận chuỗi chữ cố định và toạ độ hằng số. **Chưa hiện được giá trị biến** (điểm số, toạ độ...). Đây là thiếu sót lớn nhất |
| Số thực (`3.5`, `/` chia thực) | `/` là chia nguyên. Số thực thật cần thiết kế fixed-point riêng |
| Số nguyên lớn | Mọi biến là 8-bit không dấu (0-255). Nhân/cộng tràn thì quay vòng |
| `and` / `or` / `not` | Điều kiện `if`/`wh` chỉ nhận **một** phép so sánh. Muốn kết hợp thì lồng `if` |
| `return` | Hàm `def` không trả giá trị |
| `%`, số ngẫu nhiên, mảng | Chưa có |
| `render()` di chuyển được | Cần nhúng dữ liệu hex vào ROM lúc chạy |
| Cắt biên màn hình | `move()` ra ngoài 0-191 / 0-63 sẽ vẽ ra ngoài vùng hiển thị |
| Debounce phím | `key()` trả trạng thái thô, tự xử lý "1 lần nhấn" bằng biến trạng thái |
| **Dòng CWX** (đen trắng 1 bitplane) | Build hiện tại nhắm dòng **CW** (2 bitplane). Xem mục dưới |

## Dòng máy: CW và CWX

Theo `libcw.h`, hai dòng khác nhau ở phần cứng hiển thị và bộ nhớ:

| | CW (build hiện tại) | CWX |
|---|---|---|
| Màn hình | 2 bitplane, chọn qua `0xF037` (giá trị 0 và 4) | 1 bitplane, không có `0xF037` |
| RAM đồ hoạ (`VRAM`) | `0x9000` | `0xD000` |
| Bàn phím `0xF040`/`0xF046`, Timer0 | dùng chung | dùng chung |

`pymini2.py` hiện ghi cả hai bitplane và đặt biến từ `0x9000`, nên **chưa dùng được cho CWX**. Muốn hỗ trợ cần thêm file khởi động (startup) và bản đồ bộ nhớ (linker map) của CWX.


-# co the co loi nen hay bao t ben discord
