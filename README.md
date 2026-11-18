# Quản lý Lịch hẹn

Ứng dụng Android Java + XML, lưu dữ liệu bằng SQLiteOpenHelper trong
appointments.db (version 1), theo plan_quan_ly_lich_hen.md.

- Đăng nhập bằng tài khoản lưu trong bảng users. Tài khoản mẫu: admin / 123456.
- Danh sách sắp xếp theo ngày, giờ; thống kê tổng số và số lịch có nhắc.
- Thêm lịch bằng DatePicker và TimePicker 24 giờ; tên, địa điểm bắt buộc;
  thời gian phải sau thời điểm hiện tại.
- Chi tiết: bật/tắt nhắc lưu ngay vào SQLite; xóa có xác nhận.
- Các màn hình truyền ID qua Intent; danh sách tải lại trong onResume().

Package chính: model, database, adapter, activity, util.
ArrayList chỉ chứa kết quả truy vấn; SQLite là nguồn lưu trữ chính.
Ba lịch mẫu giữ nguyên ngày tháng trong kế hoạch, kể cả khi đã qua hiện tại.
Nhắc nhở là trạng thái bật/tắt được lưu trong DB; chưa lập lịch thông báo hệ thống.
onUpgrade() đặt lại hai bảng theo kế hoạch; khi tăng version cho sản phẩm thực tế
cần thay bằng migration giữ dữ liệu.

Build và kiểm tra (JDK 17 trở lên, Android SDK theo cấu hình dự án):

```powershell
.\gradlew.bat assembleDebug testDebugUnitTest lintDebug
# Cần thiết bị hoặc emulator đang kết nối:
.\gradlew.bat connectedDebugAndroidTest
```

Kiểm thử: định dạng ngày, đăng nhập/SQL có tham số, dữ liệu mẫu, CRUD/thống kê,
mở lại DB, sắp xếp và luồng đăng nhập → thêm → bật/tắt → xóa.
DatabaseHelperTest dùng file DB riêng, không xóa database ứng dụng.

Nếu Gradle thiếu thư viện UTP khi chạy offline, có thể chạy APK kiểm thử trực tiếp:

```powershell
.\gradlew.bat assembleDebug assembleDebugAndroidTest testDebugUnitTest lintDebug --offline
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb shell am instrument -w com.example.myapplication.test/androidx.test.runner.AndroidJUnitRunner
```

Bộ Espresso 3.5.1 hiện có của dự án nên chạy trên emulator API 34;
trên emulator API 37, thư viện này lỗi InputManager.getInstance trước khi thao tác UI.
"# B24DCCC091-KhongAnhDuy-QuanLiLichHen" 
"# B24DCCC091-KhongAnhDuy-QuanLiLichHen" 
