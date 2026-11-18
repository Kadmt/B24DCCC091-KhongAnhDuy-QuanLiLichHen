"""Build an editable Vietnamese report from verified source and emulator screenshots."""
from pathlib import Path
import re, json, textwrap
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUT=Path(__file__).resolve().parent
PROJECT=OUT.parent
JAVA=PROJECT/'app/src/main/java/com/example/myapplication'
doc=Document()
sec=doc.sections[0]
sec.page_width=Cm(21); sec.page_height=Cm(29.7)
sec.top_margin=Cm(2); sec.bottom_margin=Cm(2)
sec.left_margin=Cm(2.5); sec.right_margin=Cm(2)
sec.header_distance=Cm(0.8); sec.footer_distance=Cm(0.8)
sec.different_first_page_header_footer=True
normal=doc.styles['Normal']
normal.font.name='Calibri'; normal.font.size=Pt(11)
normal.font.color.rgb=RGBColor(0,0,0)
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.line_spacing=1.12
for name,size in [('Title',24),('Subtitle',13),('Heading 1',17),('Heading 2',13),('Heading 3',11),('Caption',10)]:
    style=doc.styles[name]
    style.font.name='Calibri'; style.font.size=Pt(size); style.font.color.rgb=RGBColor(0,0,0)
    style.paragraph_format.space_before=Pt(12 if 'Heading' in name else 4)
    style.paragraph_format.space_after=Pt(7)
    if 'Heading' in name: style.font.bold=True
for s in doc.styles:
    if s.type==1 and s.name.startswith('TOC'):
        s.font.name='Calibri'; s.font.size=Pt(11); s.font.color.rgb=RGBColor(0,0,0)

def p(text='',style=None): return doc.add_paragraph(text,style)
def h(text,level=1): return doc.add_heading(text,level)
def page(): doc.add_page_break()
def steps(items):
    for i,text in enumerate(items,1): p(f'{i}. {text}')
def field(paragraph,instruction):
    run=paragraph.add_run(); start=OxmlElement('w:fldChar'); start.set(qn('w:fldCharType'),'begin')
    code=OxmlElement('w:instrText'); code.set(qn('xml:space'),'preserve'); code.text=' '+instruction+' '
    sep=OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'),'separate')
    end=OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'),'end')
    run._r.extend([start,code,sep,end])

footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field(footer,'PAGE')
settings=doc.settings.element
update=OxmlElement('w:updateFields'); update.set(qn('w:val'),'true'); settings.append(update)

table_number=0
def table(headers,rows,widths,caption=None):
    global table_number
    table_number+=1
    if caption: p(f'Bảng {table_number}. {caption}','Caption')
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    for col,w in zip(t.columns,widths): col.width=Cm(w)
    pr=t._tbl.tblPr; borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        b=OxmlElement('w:'+side); b.set(qn('w:val'),'single'); b.set(qn('w:sz'),'4'); b.set(qn('w:color'),'D9D9D9'); borders.append(b)
    pr.append(borders)
    margins=OxmlElement('w:tblCellMar')
    for side,value in [('top','90'),('bottom','90'),('left','100'),('right','100')]:
        e=OxmlElement('w:'+side); e.set(qn('w:w'),value); e.set(qn('w:type'),'dxa'); margins.append(e)
    pr.append(margins)
    for cell,text,w in zip(t.rows[0].cells,headers,widths):
        cell.width=Cm(w); cell.text=text
        shade=OxmlElement('w:shd'); shade.set(qn('w:fill'),'24435A'); cell._tc.get_or_add_tcPr().append(shade)
        for run in cell.paragraphs[0].runs: run.font.bold=True; run.font.color.rgb=RGBColor(255,255,255)
    repeat=OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for index,row in enumerate(rows):
        cells=t.add_row().cells
        for cell,text,w in zip(cells,row,widths):
            cell.width=Cm(w); cell.text=str(text)
            if index%2:
                sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'F2F5F7'); cell._tc.get_or_add_tcPr().append(sh)
    for row in t.rows:
        cant=OxmlElement('w:cantSplit'); row._tr.get_or_add_trPr().append(cant)
        for cell in row.cells:
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after=Pt(2); paragraph.paragraph_format.line_spacing=1.05
                for run in paragraph.runs: run.font.name='Calibri'; run.font.size=Pt(10)
    p().paragraph_format.space_after=Pt(0)
    return t

figures=[]
def images(items):
    t=doc.add_table(rows=1,cols=len(items)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+side); e.set(qn('w:val'),'nil'); borders.append(e)
    t._tbl.tblPr.append(borders)
    for cell,(name,caption) in zip(t.rows[0].cells,items):
        cell.width=Cm(8.2 if len(items)==2 else 16.4)
        paragraph=cell.paragraphs[0]; paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
        width=6.5 if len(items)==2 else (15.8 if 'ngang' in name else 6.5)
        run=paragraph.add_run(); run.add_picture(str(OUT/'screenshots'/name),width=Cm(width))
        paragraph.paragraph_format.space_after=Pt(5)
        props=run._r.xpath('.//wp:docPr')
        if props: props[0].set('descr',caption)
        number=len(figures)+1; figures.append((number,name,caption))
        c=cell.add_paragraph(f'Hình 4.{number}: {caption}','Caption'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.keep_with_next=False
        for run in c.runs: run.font.size=Pt(9.5)
    for row in t.rows:
        no=OxmlElement('w:cantSplit'); row._tr.get_or_add_trPr().append(no)

def source(file): return (JAVA/file).read_text(encoding='utf-8').splitlines()
def line(file,method):
    for i,text in enumerate(source(file),1):
        if re.search(r'\b(?:public|protected|private)\s+(?:static\s+)?[\w<>]+\s+'+re.escape(method)+r'\s*\(',text): return i
    raise ValueError((file,method))
def funcs(file,rows,caption):
    cls=Path(file).stem
    p(f'File nguồn: app/src/main/java/com/example/myapplication/{file}.')
    data=[]
    for method,args,result,description in rows:
        data.append((method+'()',cls+'.java\nDòng '+str(line(file,method)),args,result,description))
    table(['Hàm','File và class','Tham số','Kết quả','Mô tả và thời điểm gọi'],data,[2.8,3.1,2.4,1.6,6.6],caption)
def snippet(file,start,end,title):
    p(f'{title} — {Path(file).name}, dòng {start}–{end}.','Caption')
    lines=textwrap.dedent('\n'.join(source(file)[start-1:end])).splitlines()
    for n,text in enumerate(lines,start):
        para=p(); para.paragraph_format.space_after=Pt(0); para.paragraph_format.line_spacing=1
        para.paragraph_format.keep_with_next=n<end
        run=para.add_run(f'{n:>3}  '+text if text.strip() else f'{n:>3}')
        run.font.name='Consolas'; run.font.size=Pt(9)
    p()

# Cover and editable TOC.
p().paragraph_format.space_after=Pt(55)
cover=p('BÁO CÁO KỸ THUẬT VÀ HƯỚNG DẪN SỬ DỤNG','Title'); cover.alignment=WD_ALIGN_PARAGRAPH.CENTER
cover=p('ỨNG DỤNG QUẢN LÝ LỊCH HẸN','Title'); cover.alignment=WD_ALIGN_PARAGRAPH.CENTER
p().paragraph_format.space_after=Pt(35)
for text in ['Tác giả: Khổng Anh Duy','Mã sinh viên: B24DCCC091','Phiên bản ứng dụng: 1.0','Nền tảng: Android native Java và XML','Ngày thực hiện: 18 tháng 11 năm 2026']:
    q=p(text); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
p().paragraph_format.space_after=Pt(30)
p('Tài liệu mô tả cách chạy và sử dụng ứng dụng, kết quả kiểm tra các thao tác trên Android Emulator và vai trò của các hàm Java chính. Nội dung, bảng, đoạn code và chú thích trong tài liệu đều có thể chỉnh sửa trong Microsoft Word.')
page()
h('Mục lục')
field(p(),'TOC \\o "1-2" \\h \\z \\u')
p('Trong Word, nhấp phải mục lục và chọn Update Field để cập nhật toàn bộ sau khi chỉnh sửa. Các ảnh được chèn riêng, có thể thay thế hoặc đổi kích thước.')
page()
h('1 Giới thiệu')
p('Quản lý Lịch hẹn là ứng dụng Android cá nhân giúp người dùng ghi lại tên cuộc hẹn, địa điểm, ngày giờ và tùy chọn nhắc. Ứng dụng dùng SQLite trên thiết bị, không có backend và không cần gọi dịch vụ mạng để thực hiện các chức năng được khảo sát.')
p('Luồng chính gồm đăng nhập, xem danh sách và thống kê, thêm lịch, xem chi tiết, đổi trạng thái nhắc và xóa lịch. Người dùng thông thường có thể theo phần hướng dẫn bằng ảnh; lập trình viên tiếp nhận dự án có thể tra cấu trúc dữ liệu và các hàm chính ở phần giải thích source.')
p('Trong lần chạy này, lịch QA_Report_091 đã được thêm, tắt nhắc, giữ lại sau force-stop và mở lại app, rồi xóa. Thống kê trở về mốc 3 lịch và 3 lịch có nhắc sau khi hoàn tất. Các lịch có sẵn không bị xóa.')
p('Nhắc nhở trong phiên bản 1.0 là một trạng thái được lưu trong SQLite. Source hiện chưa lập lịch AlarmManager hoặc gửi thông báo hệ thống; vì vậy không nên hiểu nút bật nhắc là đã có thông báo tự động.')
h('2 Môi trường và cách chạy')
table(['Thành phần','Giá trị đã kiểm tra'],[
('Hệ điều hành máy chủ','Windows; WHPX 10.0.22631 đã cài và sử dụng được'),
('Android Studio','2026.1.3; build AI-261.26222.65.2613.16025427'),
('JDK chạy Gradle','Java 24.0.2 tại D:/JDK'),('Java của source','sourceCompatibility và targetCompatibility: Java 11'),
('Gradle và AGP','Gradle 9.5.0; Android Gradle Plugin 9.3.3'),
('Android SDK','D:/Android/Sdk; platform android-37.0; build-tools 36.0.0'),
('SDK của ứng dụng','compileSdk 37; targetSdk 37; minSdk 24'),
('Emulator thực tế','AVD Pixel_8a; emulator-5554; Android 17, API 37'),
('Package và phiên bản','com.example.myapplication; versionName 1.0; versionCode 1')
],[4.2,12.3],'Môi trường thực tế')
page()
h('2 1 Kiểm tra và build',2)
p('Máy đã có sẵn JDK, Android Studio, SDK và emulator. Không cài lại SDK, không bật thêm tính năng Windows và không sửa biến môi trường hệ thống. ANDROID_HOME hiện trỏ C:/Android/sdk, khác SDK của project; local.properties trỏ D:/Android/Sdk. Các lệnh khảo sát dùng đường dẫn đầy đủ để tránh nhầm SDK.')
steps(['Mở PowerShell tại thư mục MyApplication2, nơi có settings.gradle.kts và gradlew.bat.','Kiểm tra JDK bằng D:/JDK/bin/java.exe -version.','Đặt GRADLE_USER_HOME trong phiên PowerShell về cache hiện có nếu môi trường không tìm đúng cache.','Chạy .\\gradlew.bat assembleDebug --offline. Lần thực hiện báo cáo trả về BUILD SUCCESSFUL in 3s; 35 task up-to-date.'])
h('2 2 Cài và mở ứng dụng',2)
for text in [r'& D:/Android/Sdk/platform-tools/adb.exe devices',r'& D:/Android/Sdk/platform-tools/adb.exe -s emulator-5554 install -r app/build/outputs/apk/debug/app-debug.apk',r'& D:/Android/Sdk/platform-tools/adb.exe -s emulator-5554 shell am start -n com.example.myapplication/.activity.LoginActivity']:
    para=p(text); para.paragraph_format.line_spacing=1
    for run in para.runs: run.font.name='Consolas'; run.font.size=Pt(9)
p('Cài bằng -r giữ dữ liệu hiện có. adb devices đã nhận emulator-5554 ở trạng thái device và sys.boot_completed trả về 1. Launcher được khai báo là LoginActivity; các Activity còn lại không exported.')
h('3 Cấu trúc project')
tree='app/src/main/\n  AndroidManifest.xml\n  java/com/example/myapplication/\n    activity/  LoginActivity, MainActivity\n               AddAppointmentActivity, AppointmentDetailActivity\n               AppointmentActivity\n    adapter/   AppointmentAdapter\n    database/  DatabaseHelper\n    model/     Appointment\n    util/      AppointmentDateTime\n  res/layout/ activity_login, activity_main\n              activity_add_appointment\n              activity_appointment_detail, item_appointment'
for text in tree.splitlines():
    para=p(); para.paragraph_format.space_after=Pt(0); run=para.add_run(text); run.font.name='Consolas'; run.font.size=Pt(9.5)
page()
h('3 1 Vai trò các lớp',2)
table(['Nhóm','Trách nhiệm'],[
('activity','Dựng giao diện bằng View Binding, nhận thao tác, kiểm tra đầu vào và điều hướng.'),
('AppointmentActivity','Lớp cơ sở áp dụng khoảng đệm thanh hệ thống, display cutout và bàn phím.'),
('adapter','Đưa kết quả truy vấn vào ListView; định dạng và đặt lại nhãn trạng thái khi tái sử dụng dòng.'),
('database','Tạo schema, chèn dữ liệu mẫu và thực hiện truy vấn SQLite có tham số.'),
('model','Appointment chứa 6 thuộc tính của một lịch hẹn.'),('util','Chuyển ngày giờ lưu trữ sang dạng hiển thị.')],[4.2,12.3],'Phân chia trách nhiệm')
h('3 2 Dữ liệu và luồng lưu trữ',2)
p('DatabaseHelper kế thừa SQLiteOpenHelper, mở appointments.db ở version 1. onCreate() tạo hai bảng và chèn admin/123456 cùng ba lịch mẫu chỉ khi DB được tạo lần đầu. Danh sách trên emulator có thể khác dữ liệu mẫu vì đã được người dùng thay đổi trước đợt báo cáo.')
table(['Bảng','Các cột và ràng buộc'],[
('users','id INTEGER PRIMARY KEY AUTOINCREMENT; username TEXT NOT NULL UNIQUE; password TEXT NOT NULL.'),
('appointments','id INTEGER PRIMARY KEY AUTOINCREMENT; title, location, date, time đều TEXT NOT NULL; reminder INTEGER NOT NULL, chỉ nhận 0 hoặc 1.')],[3,13.5],'Schema đọc từ DatabaseHelper.onCreate')
p('Ngày lưu theo yyyy-MM-dd, giờ theo HH:mm nên ORDER BY date ASC, time ASC, id ASC cho thứ tự ổn định. Trên giao diện, AppointmentDateTime.format() chuyển thành dd/MM/yyyy · HH:mm. ArrayList chỉ là kết quả truy vấn phục vụ adapter, không phải nơi lưu trữ chính.')
p('Khi lưu lịch, Activity tạo Appointment rồi gọi insertAppointment(). Khi mở danh sách, onResume() truy vấn lại và cập nhật thống kê. Chi tiết chỉ nhận appointment_id qua Intent, sau đó đọc bản ghi mới nhất. Bật/tắt nhắc gọi updateReminder(); xóa gọi deleteAppointment(). Các Cursor đọc thủ công đều được đóng bằng try-with-resources.')
p('Mật khẩu trong schema demo được lưu dạng TEXT và tài khoản mẫu hiển thị trên màn hình đăng nhập. Cơ chế này phù hợp phạm vi bài demo, chưa có băm mật khẩu hay quản lý phiên đăng nhập. onUpgrade() hiện xóa và tạo lại hai bảng; khi nâng version thực tế cần thiết kế migration giữ dữ liệu.')
page()
h('4 Hướng dẫn sử dụng')
h('4 1 Mở ứng dụng và kiểm tra trường bắt buộc',2)
steps(['Mở ứng dụng để đến màn hình đăng nhập.','Để trống tên đăng nhập và mật khẩu, nhấn Đăng nhập.','Quan sát biểu tượng lỗi ở cả hai ô; ứng dụng vẫn ở màn hình đăng nhập.'])
images([('01_dang_nhap.png','Màn hình đăng nhập ban đầu'),('02_dang_nhap_thieu_thong_tin.png','Trạng thái lỗi khi bỏ trống tài khoản')])
p('Tài khoản dùng cho bài demo là admin / 123456. Không cần tạo tài khoản mới để thực hiện các bước tiếp theo.')
page()
h('4 2 Đăng nhập và xem danh sách',2)
steps(['Nhập admin và một mật khẩu sai, nhấn Đăng nhập để kiểm tra thông báo lỗi.','Thay mật khẩu bằng 123456 rồi đăng nhập lại.','Quan sát danh sách theo ngày giờ và dòng thống kê. Mốc khảo sát ban đầu là Tổng: 3 | Có nhắc: 3.'])
images([('03_dang_nhap_sai.png','Thông báo sai tên đăng nhập hoặc mật khẩu'),('04_danh_sach.png','Danh sách và thống kê ban đầu')])
page()
h('4 3 Mở form và kiểm tra dữ liệu thiếu',2)
steps(['Từ danh sách, nhấn Thêm lịch hẹn.','Cuộn tới nút Lưu lịch hẹn rồi nhấn khi chưa điền thông tin.','Cuộn về đầu form: hai ô tên và địa điểm có biểu tượng lỗi; lịch chưa được lưu.'])
images([('05_form_them.png','Form thêm lịch hẹn mới'),('06_them_thieu_thong_tin.png','Lỗi trường tên và địa điểm bắt buộc')])
p('Form có chiều dài lớn hơn màn hình; cần cuộn dọc để đến bộ chọn thời gian, công tắc nhắc và nút lưu. Khi cuộn bằng thao tác tự động, vuốt ở mép form để tránh thay đổi spinner ngoài ý muốn.')
page()
h('4 4 Chọn thời gian và nhắc nhở',2)
steps(['Điền QA_Report_091 và Phong Demo.','Chọn 01/11/2026, 16:00 rồi lưu. Tại ngày thực hiện 18/11/2026, thời gian này đã qua; ứng dụng từ chối và hiện Toast.','Đổi năm sang 2027, giữ ngày 01/11 và giờ 16:00, giữ công tắc nhắc đang bật.'])
images([('07_thoi_gian_khong_hop_le.png','Toast từ chối thời gian không ở tương lai'),('08_chon_thoi_gian_va_nhac.png','Thời gian hợp lệ và tùy chọn nhắc đang bật')])
p('Bộ chọn trên emulator dùng ngôn ngữ hệ thống tiếng Anh nên tháng hiện là Nov. Phần hướng dẫn và nhãn ứng dụng vẫn hiển thị tiếng Việt.')
page()
h('4 5 Lưu lịch và mở chi tiết',2)
steps(['Nhấn Lưu lịch hẹn với thời gian hợp lệ.','Ứng dụng quay về danh sách; cuộn để thấy QA_Report_091. Thống kê tăng thành Tổng: 4 | Có nhắc: 4.','Nhấn lịch vừa thêm để xem địa điểm, ngày giờ và trạng thái nhắc.'])
images([('09_them_thanh_cong.png','Lịch thử đã được thêm và thống kê tăng'),('10_chi_tiet.png','Chi tiết QA_Report_091 với nhắc đang bật')])
page()
h('4 6 Tắt nhắc và kiểm tra thống kê',2)
steps(['Trong chi tiết QA_Report_091, tắt công tắc Nhắc nhở.','Quan sát dòng Đang tắt; thay đổi được lưu ngay.','Nhấn Quay lại: tổng số lịch vẫn là 4, số có nhắc giảm còn 3.'])
images([('11_tat_nhac.png','Trạng thái nhắc chuyển sang Đang tắt'),('12_thong_ke_sau_tat_nhac.png','Danh sách cập nhật thành 4 lịch và 3 lịch có nhắc')])
p('Đổi công tắc không cần nhấn Lưu. Đây là cập nhật cờ reminder trong SQLite, chưa phải thao tác đăng ký thông báo hệ thống.')
page()
h('4 7 Kiểm tra dữ liệu sau khi mở lại và hủy xóa',2)
steps(['Force-stop ứng dụng bằng adb, mở lại launcher và đăng nhập bằng tài khoản mẫu.','Cuộn danh sách: QA_Report_091 vẫn tồn tại, có nhãn Không nhắc; thống kê vẫn là 4/3.','Mở chi tiết, nhấn Xóa lịch hẹn rồi chọn Hủy. Chi tiết vẫn hiện lịch thử, chứng tỏ thao tác hủy chưa xóa bản ghi.'])
images([('13_du_lieu_sau_mo_lai.png','Lịch và trạng thái nhắc được giữ sau force-stop'),('17_huy_xoa.png','Chi tiết còn nguyên sau khi hủy xác nhận xóa')])
page()
h('4 8 Xác nhận xóa lịch thử',2)
steps(['Mở lại hộp thoại bằng nút Xóa lịch hẹn.','Đọc tên QA_Report_091 trong nội dung xác nhận rồi nhấn Xóa.','Ứng dụng quay về danh sách; thống kê trở về Tổng: 3 | Có nhắc: 3. Chỉ bản ghi thử được xóa.'])
images([('14_xac_nhan_xoa.png','Hộp thoại xác nhận nêu rõ tên lịch cần xóa'),('15_sau_khi_xoa.png','Danh sách sau khi xóa lịch thử')])
page()
h('4 9 Giao diện khi xoay ngang',2)
p('Danh sách được mở khi khóa hướng tạm thời sang ngang. Sau khi chụp, cài đặt xoay ban đầu của emulator được khôi phục. Ảnh dưới ghi lại bố cục thực tế, không phải bản dựng hoặc ảnh thiết kế.')
p('Kết quả cần cải thiện: trên viewport ngang 2400 × 1080, chỉ nhìn thấy phần tiêu đề, thống kê và tiêu đề danh sách; các dòng lịch và nút thêm không xuất hiện trong vùng màn hình. Vì vậy chưa thể coi màn hình danh sách đã hỗ trợ đầy đủ hướng ngang.')
images([('16_giao_dien_ngang.png','Bố cục danh sách ở hướng ngang')])
h('4 10 Đối chiếu thống kê',2)
table(['Thời điểm','Tổng lịch','Có nhắc','Kết quả'],[
('Trước thêm lịch QA_Report','3','3','Mốc ban đầu'),('Sau thêm, nhắc bật','4','4','Tăng đúng'),
('Sau tắt nhắc','4','3','Tổng giữ nguyên'),('Sau force-stop và đăng nhập lại','4','3','Dữ liệu còn'),('Sau xác nhận xóa QA_Report','3','3','Trở về mốc đầu')],[7.3,2.2,2.2,4.8],'Các giá trị đọc trực tiếp từ giao diện')
p('Danh sách rỗng không được tạo trong đợt này vì cần giữ các lịch có sẵn. Cơ chế setEmptyView() đã được đọc trong source, nhưng trạng thái đó chưa được kiểm thử bằng ảnh trong báo cáo.')
page()
h('5 Giải thích các hàm chính')
p('Số dòng dưới đây tham chiếu source đã được lưu tại thời điểm làm báo cáo. Các thao tác giao diện ở chương 4 đã chạy trực tiếp; phần khởi tạo schema, nâng version hoặc thêm tài khoản được mô tả theo code, không được coi là đã kiểm thử riêng chỉ vì có mặt trong bảng.')
h('5 1 Đăng nhập',2)
funcs('activity/LoginActivity.java',[
('onCreate','Bundle savedInstanceState','void','Khi màn hình được tạo: inflate binding, setScreen(), mở DatabaseHelper và gắn nút đăng nhập với login().'),
('login','Không có','void','Khi nhấn Đăng nhập: bỏ lỗi cũ, kiểm tra trường trống, gọi checkLogin(); đúng thì mở MainActivity rồi finish().'),
('showError','int message','void','Hiện tvError với chuỗi lỗi đăng nhập hoặc truy cập DB. Được login() gọi khi có lỗi.'),
('onDestroy','Không có','void','Đóng DatabaseHelper khi Activity bị hủy.')],'Các hàm của LoginActivity')
snippet('activity/LoginActivity.java',29,42,'Đoạn kiểm tra đăng nhập thực tế')
h('5 2 Danh sách và thống kê',2)
funcs('activity/MainActivity.java',[
('onCreate','Bundle savedInstanceState','void','Tạo adapter, gắn ListView/empty view; nút thêm mở AddAppointmentActivity; nhấn dòng truyền appointment_id sang chi tiết.'),
('onResume','Không có','void','Mỗi lần trở lại: getAllAppointments(), updateData(), countAll() và countReminders() để cập nhật danh sách/thống kê.')],'Các hàm của MainActivity')
page()
h('5 3 Thêm lịch hẹn',2)
funcs('activity/AddAppointmentActivity.java',[
('onCreate','Bundle savedInstanceState','void','Dựng form, đặt giờ 24h; lần tạo đầu gợi ý thời gian sau hiện tại một giờ; gắn nút lưu/quay lại.'),
('save','Không có','void','Khi nhấn Lưu: commit spinner, trim tên/địa điểm, kiểm tra bắt buộc và tương lai. Tạo Appointment, insertAppointment(), thông báo rồi finish().')],'Các hàm của AddAppointmentActivity')
p('save() không mở MainActivity mới. finish() quay về Activity có sẵn, khiến MainActivity.onResume() tự tải lại SQLite. Nếu thời gian không sau Calendar.getInstance(), hàm hiển thị Toast và return trước khi ghi DB.')
snippet('activity/AddAppointmentActivity.java',50,61,'Kiểm tra thời gian và tạo model')
p('Trong ảnh kiểm thử, 01/11/2026 bị từ chối, trong khi 01/11/2027 được chấp nhận. Quy tắc phụ thuộc đồng hồ thiết bị tại lúc nhấn Lưu; không phải một ngày cố định được viết trong Activity.')
h('5 4 Điều hướng và khoảng đệm hệ thống',2)
funcs('activity/AppointmentActivity.java',[
('setScreen','View root','void','Được onCreate() của các màn hình gọi: setContentView(), lấy padding gốc và cộng insets thanh hệ thống/cutout/IME qua ViewCompat.')],'Hàm dùng chung của các màn hình')
p('LoginActivity gọi finish() sau đăng nhập đúng. Các Activity con cũng dùng finish() khi quay lại hoặc khi thao tác thành công. Không truyền toàn bộ model qua Intent, chỉ truyền ID số nguyên để đọc lại DB.')
page()
h('5 5 Chi tiết và thao tác nhắc hoặc xóa',2)
funcs('activity/AppointmentDetailActivity.java',[
('onCreate','Bundle savedInstanceState','void','Tạo binding/DB, gắn Quay lại và dựng AlertDialog khi nhấn Xóa. Hủy không gọi delete(); Xóa gọi delete().'),
('onResume','Không có','void','Đọc appointment_id, lấy lịch theo ID, điền chi tiết. Thiết lập công tắc từ DB rồi gắn listener cập nhật reminder.'),
('updateReminderStatus','Không có','void','Đặt tvReminderStatus thành Đang bật/Đang tắt từ model hiện tại.'),
('delete','Không có','void','Gọi database.deleteAppointment(id), hiện Toast rồi finish(); lỗi SQLite thì thông báo và giữ màn hình.')],'Các hàm của AppointmentDetailActivity')
p('Listener công tắc nằm trong onResume(). Nó bỏ qua trường hợp checked bằng trạng thái model, cập nhật SQLite rồi cập nhật model và chữ trạng thái. Nếu ghi DB lỗi, công tắc được trả về trạng thái trước đó. Khi ID không tồn tại, Activity thông báo và kết thúc thay vì hiển thị dữ liệu rỗng.')
snippet('activity/AppointmentDetailActivity.java',51,63,'Listener cập nhật reminder trong source')
page()
h('5 6 DatabaseHelper và truy vấn SQLite',2)
funcs('database/DatabaseHelper.java',[
('onCreate','SQLiteDatabase db','void','SQLiteOpenHelper gọi khi DB chưa có: tạo hai bảng, chèn tài khoản mẫu và ba lịch mẫu.'),
('onUpgrade','db, oldVersion, newVersion','void','Khi tăng version: DROP hai bảng rồi onCreate(). Chưa được kích hoạt trong đợt khảo sát.'),
('checkLogin','String username, password','boolean','LoginActivity.login() gọi; query users với hai tham số ? và giới hạn một dòng.'),
('insertUser','String username, password','void','Ghi user bằng ContentValues; insertOrThrow có thể báo trùng username. Không có màn hình đăng ký trong app hiện tại.'),
('insertAppointment','Appointment appointment','long','Ghi các thuộc tính; trả row ID từ insertOrThrow. Được save() của form gọi.'),
('getAllAppointments','Không có','ArrayList','Query theo date, time, id; readAppointment() chuyển Cursor sang model. MainActivity.onResume() gọi.'),
('getAppointmentById','int id','Appointment hoặc null','Query id = ?; dùng khi mở chi tiết, null nếu không có bản ghi.')],'Các hàm tạo và đọc dữ liệu')
page()
h('5 7 Cập nhật xóa và thống kê trong SQLite',2)
funcs('database/DatabaseHelper.java',[
('updateReminder','int id, boolean on','void','Ghi reminder thành 0/1 theo id = ? khi đổi công tắc ở chi tiết.'),
('deleteAppointment','int id','void','DELETE theo id = ? sau khi người dùng xác nhận xóa.'),
('countAll','Không có','int','COUNT(*) của toàn bảng appointments, dùng cho thống kê.'),
('countReminders','Không có','int','COUNT(*) WHERE reminder = ?, tham số 1; dùng cho số lịch bật nhắc.'),
('valuesOf','Appointment appointment','ContentValues','Ánh xạ title/location/date/time/reminder để insert.'),
('readAppointment','Cursor cursor','Appointment','Đọc từng cột bằng getColumnIndexOrThrow(), chuyển reminder = 1 sang boolean.')],'Các hàm ghi thay đổi và đếm dữ liệu')
snippet('database/DatabaseHelper.java',86,91,'Truy vấn theo ID và đóng Cursor tự động')
p('Các giá trị do người dùng cung cấp đi qua selectionArgs hoặc ContentValues. Tên bảng và mệnh đề SQL là hằng trong source; không nối trực tiếp tên lịch, tài khoản hoặc mật khẩu vào câu SQL. Các truy vấn đếm dùng DatabaseUtils.longForQuery().')
page()
h('5 8 Adapter model và định dạng ngày giờ',2)
funcs('adapter/AppointmentAdapter.java',[
('updateData','ArrayList appointments','void','Thay dữ liệu sau query và notifyDataSetChanged() để ListView vẽ lại.'),
('getView','position, convertView, parent','View','ListView gọi cho từng dòng: tái sử dụng ItemAppointmentBinding qua tag, điền 4 nhãn và đặt màu/trạng thái nhắc.')],'Các hàm của AppointmentAdapter')
funcs('util/AppointmentDateTime.java',[
('format','String date, time','String','Parse yyyy-MM-dd HH:mm không lenient, format dd/MM/yyyy · HH:mm. Nếu parse lỗi, trả chuỗi gốc nối dấu chấm giữa để tránh crash.')],'Định dạng ngày giờ')
p('Appointment.java chứa id (int), title/location/date/time (String), reminder (boolean). Constructor không ID dùng khi thêm, constructor có ID dùng khi đọc Cursor. Getter/setter là các phương thức truy cập dữ liệu, không tự ghi SQLite.')
snippet('adapter/AppointmentAdapter.java',45,58,'Binding dữ liệu vào dòng lịch hẹn')
page()
h('6 Kết quả kiểm tra và các điểm cần lưu ý')
p('Các luồng đăng nhập, thêm lịch, kiểm tra trường trống/thời gian, xem chi tiết, tắt nhắc, lưu qua force-stop, hủy và xác nhận xóa đã được thao tác trên emulator. Kết quả thống kê ở Bảng đối chiếu khớp với các thay đổi. Các ảnh chụp gốc được giữ trong thư mục screenshots để đối chiếu.')
table(['Tình huống','Quan sát hoặc căn cứ','Cách xử lý hoặc lưu ý'],[
('Thông tin đăng nhập trống','Hai ô có biểu tượng lỗi; login() kiểm tra isEmpty().','Điền đủ tên đăng nhập và mật khẩu.'),
('Mật khẩu sai','Thông báo Sai tên đăng nhập hoặc mật khẩu trên ảnh.','Dùng đúng tài khoản mẫu admin/123456.'),
('Thiếu tên hoặc địa điểm','Biểu tượng lỗi và không lưu lịch.','Điền cả hai trường trước khi lưu.'),
('Thời gian đã qua','Toast Thời gian phải sau thời điểm hiện tại.','Chọn thời gian ở tương lai theo đồng hồ thiết bị.'),
('Cuộn tự động vào spinner','Một lần vuốt tại giữa form làm đổi ngày thay vì cuộn trang.','Công cụ khảo sát đổi sang vuốt ở mép; đây là lưu ý thao tác, không phải sửa source.'),
('UTF-8 trong công cụ khảo sát','PowerShell/Python stdout mặc định cp1252 không in được tiếng Việt.','qa_capture.py cấu hình stdout UTF-8; lỗi thuộc công cụ báo cáo, không thuộc app.'),
('Vùng thanh trạng thái khi cuộn','Một số ảnh form cho thấy nội dung cuộn nằm phía dưới biểu tượng thanh trạng thái.','Ghi nhận để cải thiện insets/clipToPadding trong lần sửa giao diện sau; không sửa trong đợt QA.'),
('Danh sách ở hướng ngang','Ảnh 16_giao_dien_ngang.png và UI dump chỉ thấy phần đầu trang, không thấy danh sách hoặc nút thêm.','Cần điều chỉnh bố cục responsive hoặc thu gọn phần đầu khi hỗ trợ ngang; chưa sửa source.'),
('Lỗi SQLite theo source','Activity có catch SQLiteException; chưa cố tình gây lỗi DB.','App hiện thông báo lỗi truy cập dữ liệu; chưa kết luận về phục hồi dữ liệu khi lỗi thực tế.')],[3.4,6.3,6.8],'Lỗi và tình huống thực tế hoặc được chỉ rõ trong source')
p('Không xóa các lịch có sẵn để tạo danh sách rỗng; không kiểm thử nâng version DB hoặc thông báo hệ thống. Đợt báo cáo này tập trung kiểm tra bằng thao tác ADB, không chạy lại bộ Espresso trên emulator API 37.')
page()
h('7 Phụ lục')
h('7 1 Danh mục ảnh',2)
table(['Hình','File ảnh','Nội dung'],[(f'4.{n}',name,cap) for n,name,cap in figures],[1.4,7.6,7.5],'Ảnh chụp gốc từ emulator')
page()
h('7 2 Nhật ký lệnh chính',2)
commands=[
('Kiểm tra Java',r'D:/JDK/bin/java.exe -version'),
('Kiểm tra máy ảo',r'adb devices; emulator -list-avds; emulator -accel-check'),
('Chờ boot',r'adb -s emulator-5554 shell getprop sys.boot_completed'),
('Build',r'.\gradlew.bat assembleDebug --offline'),
('Cài APK',r'adb -s emulator-5554 install -r app/build/outputs/apk/debug/app-debug.apk'),
('Mở launcher',r'adb -s emulator-5554 shell am start -n com.example.myapplication/.activity.LoginActivity'),
('Đọc cấu trúc UI',r'adb shell uiautomator dump /sdcard/report_ui.xml; adb pull /sdcard/report_ui.xml <file.xml>'),
('Thao tác',r'adb shell input tap x y; input swipe x1 y1 x2 y2 500; input text QA_Report_091'),
('Chụp an toàn',r'adb shell screencap -p /sdcard/report_screen.png; adb pull /sdcard/report_screen.png <anh.png>'),
('Kiểm tra lưu trữ',r'adb shell am force-stop com.example.myapplication; mở launcher và đăng nhập lại'),
('Đổi hướng tạm',r'adb shell settings put system user_rotation 1; khôi phục giá trị đã lưu')]
table(['Mục đích','Lệnh hoặc chuỗi thao tác'],commands,[3.6,12.9],'Các lệnh đã dùng trong khảo sát')
p('Đường dẫn adb/emulator đầy đủ nằm dưới D:/Android/Sdk. Nhật ký chi tiết từng lệnh, mã trả về và thời điểm lưu tại evidence/adb_commands.jsonl. Các placeholder x, y và <file> trong bảng là mẫu cú pháp; giá trị thực tế được lấy từ bounds của UI dump và ghi trong nhật ký.')
h('7 3 Hồ sơ bàn giao',2)
p('report.docx là bản Word chỉnh sửa được. screenshots chứa ảnh chụp gốc; work_log.md chứa nhật ký các giai đoạn; kich_ban_chup.md lưu kịch bản đã duyệt. evidence lưu log build, XML UI, bản source có số dòng và SHA256 để chứng minh source không bị thay đổi trong đợt làm báo cáo.')
p('Để cập nhật tài liệu, thay ảnh hoặc nội dung trực tiếp trong Word rồi cập nhật mục lục. Khi thay đổi source, cần kiểm tra lại số dòng trong các bảng hàm và chạy lại các thao tác liên quan để ảnh và mô tả cùng khớp một phiên bản.')

doc.core_properties.author='Khổng Anh Duy'
doc.core_properties.title='Báo cáo kỹ thuật và hướng dẫn sử dụng ứng dụng Quản lý Lịch hẹn'
doc.core_properties.subject='Android Java XML SQLite'
doc.core_properties.keywords='B24DCCC091; Android; lịch hẹn; QA'
doc.core_properties.comments=''
doc.save(OUT/'report.docx')
(OUT/'evidence/figure_manifest.json').write_text(json.dumps([{'number':f'4.{n}','file':name,'caption':cap} for n,name,cap in figures],ensure_ascii=False,indent=2),encoding='utf-8')
print('Created report.docx; figures:',len(figures))
