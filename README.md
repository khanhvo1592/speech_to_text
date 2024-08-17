# Flask Audio Transcription Service

Flask Audio Transcription Service là một ứng dụng web đơn giản cho phép người dùng tải lên các tệp âm thanh (`mp3`, `wav`, `m4a`) và chuyển đổi chúng thành văn bản bằng cách sử dụng API nhận diện giọng nói của Viettel AI. Ứng dụng cũng hỗ trợ cấu hình API token và lưu lịch sử các bản chuyển đổi gần nhất.

## Các tính năng

- **Tải lên tệp âm thanh**: Cho phép người dùng tải lên các tệp âm thanh định dạng `mp3`, `wav`, và `m4a`.
- **Chuyển đổi âm thanh thành văn bản**: Sử dụng API của Viettel AI để nhận diện giọng nói và chuyển đổi âm thanh thành văn bản.
- **Lịch sử chuyển đổi**: Lưu lại lịch sử 10 bản chuyển đổi gần nhất và hiển thị chúng.
- **Cấu hình API Token**: Người dùng có thể cấu hình và lưu API token để sử dụng API của Viettel AI.

## Cấu trúc dự án
├── app.py # Tập tin chính chạy ứng dụng Flask
├── config.json # Lưu trữ API token
├── history.json # Lưu trữ lịch sử các bản chuyển đổi
├── templates # Thư mục chứa các tệp HTML
│ ├── upload.html # Trang tải lên và hiển thị kết quả
│ └── config.html # Trang cấu hình API token
└── uploads # Thư mục lưu trữ các tệp âm thanh được tải lên

## Hướng dẫn cài đặt và chạy ứng dụng

### 1. Clone dự án

```bash
git clone <repository-url>
cd <repository-directory>

Ứng dụng này yêu cầu Python 3 và các gói phụ thuộc được liệt kê trong requirements.txt. Bạn có thể cài đặt chúng bằng lệnh sau:

bash

Copy
pip install -r requirements.txt

3. Cấu hình API Token
Truy cập /config để nhập và lưu API token do Viettel AI cung cấp.
4. Chạy ứng dụng
Khởi chạy ứng dụng Flask bằng lệnh:

bash

Copy
python app.py
Ứng dụng sẽ chạy trên http://127.0.0.1:5000/.

Sử dụng ứng dụng
Trang tải lên
Truy cập trang chủ của ứng dụng tại http://127.0.0.1:5000/.
Tải lên một tệp âm thanh hợp lệ (.mp3, .wav, .m4a).
Nhấn "Xử lý" để chuyển đổi âm thanh thành văn bản.
Kết quả sẽ được hiển thị bên dưới, cùng với lịch sử 10 bản chuyển đổi gần nhất.
Cấu hình API Token
Truy cập trang cấu hình tại http://127.0.0.1:5000/config.
Nhập và lưu API token của bạn.
Yêu cầu hệ thống
Python 3.x
Các gói Python: Flask, requests, v.v. (được cài đặt thông qua requirements.txt)
Giấy phép
Dự án này được phát hành dưới giấy phép MIT.