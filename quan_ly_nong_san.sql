-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th3 03, 2025 lúc 04:32 AM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `quan_ly_nong_san`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `danh_muc`
--

CREATE TABLE `danh_muc` (
  `ma_danh_muc` int(11) NOT NULL COMMENT 'Mã danh mục',
  `ten_danh_muc` varchar(100) NOT NULL COMMENT 'Tên danh mục sản phẩm'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `danh_muc`
--

INSERT INTO `danh_muc` (`ma_danh_muc`, `ten_danh_muc`) VALUES
(2, 'Hải sản'),
(1, 'Rau củ'),
(3, 'Trái cây');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `khach_hang`
--

CREATE TABLE `khach_hang` (
  `ma_kh` int(11) NOT NULL COMMENT 'Mã khách hàng',
  `ten_kh` varchar(50) NOT NULL COMMENT 'Tên đăng nhập',
  `email` varchar(100) NOT NULL COMMENT 'Địa chỉ email',
  `vai_tro` enum('khach_hang') DEFAULT 'khach_hang' COMMENT 'Vai trò người dùng',
  `ngay_tao` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Ngày tạo tài khoản'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `khach_hang`
--

INSERT INTO `khach_hang` (`ma_kh`, `ten_kh`, `email`, `vai_tro`, `ngay_tao`) VALUES
(1, 'qvh', 'qvh@gmail.com', 'khach_hang', '2025-02-16 18:30:10'),
(2, '123', '123@gmail.com', 'khach_hang', '2025-02-18 04:40:25'),
(3, 'hoàng', 'hoang@gmail.com', 'khach_hang', '2025-03-02 16:18:40'),
(4, 'việt anh', 'va@gmail.com', 'khach_hang', '2025-03-02 16:43:41');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `khuyen_mai`
--

CREATE TABLE `khuyen_mai` (
  `ma_km` int(11) NOT NULL COMMENT 'Mã khuyến mãi',
  `ten_ma_km` varchar(255) NOT NULL COMMENT 'Tên mã khuyến mãi',
  `phan_tram_giam` int(11) NOT NULL,
  `ngay_bat_dau_km` date NOT NULL COMMENT 'Ngày bắt đầu khuyến mãi',
  `ngay_ket_thuc_km` date NOT NULL COMMENT 'Ngày kết thúc khuyến mãi',
  `don_toi_thieu` decimal(10,2) NOT NULL COMMENT 'Đơn tối thiểu để áp dụng giảm giá',
  `ngay_tao` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Ngày tạo khuyến mãi'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `khuyen_mai`
--

INSERT INTO `khuyen_mai` (`ma_km`, `ten_ma_km`, `phan_tram_giam`, `ngay_bat_dau_km`, `ngay_ket_thuc_km`, `don_toi_thieu`, `ngay_tao`) VALUES
(1, 'GIAM10', 10, '2025-02-03', '2025-02-04', 100000.00, '2025-03-02 22:19:25'),
(2, 'GIAM20', 20, '2025-02-03', '2025-02-04', 100000.00, '2025-03-02 22:19:25'),
(3, 'GIAM50', 50, '2025-02-03', '2025-02-04', 100000.00, '2025-03-02 22:19:25'),
(4, 'GIAM10', 10, '2024-12-31', '2025-12-31', 100000.00, '2025-03-02 22:33:08'),
(5, 'GIAM20', 20, '2024-12-31', '2025-12-31', 100000.00, '2025-03-03 01:45:27'),
(6, 'GIAM50', 50, '2024-12-31', '2025-12-31', 100000.00, '2025-03-03 01:45:37');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nha_cung_cap`
--

CREATE TABLE `nha_cung_cap` (
  `ma_nha_cung_cap` int(11) NOT NULL COMMENT 'Mã nhà cung cấp',
  `ten_nha_cung_cap` varchar(100) NOT NULL COMMENT 'Tên nhà cung cấp',
  `so_dien_thoai` varchar(20) DEFAULT NULL COMMENT 'Số điện thoại nhà cung cấp',
  `dia_chi` varchar(255) DEFAULT NULL COMMENT 'Địa chỉ nhà cung cấp'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `nha_cung_cap`
--

INSERT INTO `nha_cung_cap` (`ma_nha_cung_cap`, `ten_nha_cung_cap`, `so_dien_thoai`, `dia_chi`) VALUES
(1, 'Công ty Rau Sạch ABC', '0123456789', 'Hà Nội'),
(2, 'Hải Sản Tươi Sống', '0765432198', 'Đà Nẵng'),
(3, 'Trái Cây Nhập Khẩu XYZ', '0987654321', 'TP.HCM'),
(4, 'Thịt Chuẩn Thế Giới', '0147852369', 'Sơn La');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `order`
--

CREATE TABLE `order` (
  `ma_order` int(11) NOT NULL,
  `ma_khach_hang` int(11) DEFAULT NULL,
  `ma_khuyen_mai` int(11) DEFAULT NULL,
  `ngay_tao` timestamp NOT NULL DEFAULT current_timestamp(),
  `tong_tien` decimal(15,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `order`
--

INSERT INTO `order` (`ma_order`, `ma_khach_hang`, `ma_khuyen_mai`, `ngay_tao`, `tong_tien`) VALUES
(43, 2, NULL, '2025-03-02 19:28:18', 15000.00),
(44, 2, NULL, '2025-03-02 19:28:22', 285000.00),
(45, 2, NULL, '2025-03-02 21:18:13', 63000.00),
(46, 2, NULL, '2025-03-02 21:19:21', 150000.00),
(47, 2, NULL, '2025-03-02 21:19:41', 400000.00),
(48, 1, NULL, '2025-03-02 21:25:35', 150000.00),
(49, 3, NULL, '2025-03-02 21:33:54', 3000000.00),
(50, 3, 1, '2025-03-02 22:21:07', 135000.00),
(51, 2, NULL, '2025-03-02 23:50:53', 150000.00),
(52, 1, 4, '2025-03-03 01:37:34', 90000.00),
(53, 1, NULL, '2025-03-03 01:38:51', 0.00),
(54, 1, NULL, '2025-03-03 01:39:31', 2900000.00);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `order_detail`
--

CREATE TABLE `order_detail` (
  `ma_order_detail` int(11) NOT NULL,
  `ma_order` int(11) NOT NULL,
  `ma_san_pham` int(11) NOT NULL,
  `so_luong` int(11) NOT NULL,
  `gia_ban` decimal(15,2) NOT NULL,
  `ma_khach_hang` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `order_detail`
--

INSERT INTO `order_detail` (`ma_order_detail`, `ma_order`, `ma_san_pham`, `so_luong`, `gia_ban`, `ma_khach_hang`) VALUES
(15, 43, 1, 3, 5000.00, NULL),
(16, 44, 1, 57, 5000.00, NULL),
(17, 45, 1, 13, 5000.00, NULL),
(18, 46, 2, 30, 5000.00, NULL),
(19, 47, 2, 80, 5000.00, NULL),
(20, 48, 2, 30, 5000.00, NULL),
(21, 49, 2, 300, 5000.00, NULL),
(22, 49, 1, 300, 5000.00, NULL),
(23, 50, 1, 30, 5000.00, NULL),
(24, 51, 1, 50, 3000.00, NULL),
(25, 52, 1, 10, 10000.00, NULL),
(26, 53, 1, 0, 10000.00, NULL),
(27, 54, 1, 290, 10000.00, NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `san_pham`
--

CREATE TABLE `san_pham` (
  `ma_san_pham` int(11) NOT NULL COMMENT 'Mã sản phẩm',
  `ten_san_pham` varchar(100) NOT NULL COMMENT 'Tên sản phẩm',
  `ma_danh_muc` int(11) NOT NULL COMMENT 'Mã danh mục (liên kết danh_muc)',
  `gia` decimal(10,2) NOT NULL COMMENT 'Giá sản phẩm',
  `so_luong_ton` float NOT NULL COMMENT 'Số lượng tồn kho',
  `mo_ta` text DEFAULT NULL COMMENT 'Mô tả sản phẩm',
  `ngay_them` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Ngày thêm sản phẩm',
  `ma_nha_cung_cap` int(11) DEFAULT NULL,
  `anh` varchar(255) DEFAULT '',
  `don_vi` enum('quả','con','kg') DEFAULT 'quả' COMMENT 'Đơn vị tính: quả, con, kg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `san_pham`
--

INSERT INTO `san_pham` (`ma_san_pham`, `ten_san_pham`, `ma_danh_muc`, `gia`, `so_luong_ton`, `mo_ta`, `ngay_them`, `ma_nha_cung_cap`, `anh`, `don_vi`) VALUES
(1, 'Cà tím', 2, 10000.00, 2990, NULL, '2025-03-02 19:28:03', 1, 'C:/xampp/htdocs/123/logo-nong-san-nha-que-compressed.jpg', 'kg'),
(2, 'Dưa Lê', 3, 3000.00, 300, NULL, '2025-03-02 21:19:10', 3, 'C:/xampp/htdocs/123/logo-nong-san-nha-que-compressed.jpg', 'quả'),
(3, 'Cá ngừ', 2, 30000.00, 50, NULL, '2025-03-02 23:49:25', 2, 'C:/xampp/htdocs/123/logo-nong-san-nha-que-compressed.jpg', 'kg'),
(4, 'Tôm Hùm', 2, 20000.00, 40, NULL, '2025-03-03 01:11:17', 2, 'C:/xampp/htdocs/123/logo-nong-san-nha-que-compressed.jpg', 'con');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `tai_khoan`
--

CREATE TABLE `tai_khoan` (
  `id_tk` int(11) NOT NULL,
  `ten_tk` varchar(255) NOT NULL,
  `mk_tk` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `tai_khoan`
--

INSERT INTO `tai_khoan` (`id_tk`, `ten_tk`, `mk_tk`, `email`, `created_at`) VALUES
(1, 'adm', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'adm@gmail.com', '2025-03-02 15:51:44');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `danh_muc`
--
ALTER TABLE `danh_muc`
  ADD PRIMARY KEY (`ma_danh_muc`),
  ADD UNIQUE KEY `ten_danh_muc` (`ten_danh_muc`);

--
-- Chỉ mục cho bảng `khach_hang`
--
ALTER TABLE `khach_hang`
  ADD PRIMARY KEY (`ma_kh`),
  ADD UNIQUE KEY `ten_kh` (`ten_kh`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Chỉ mục cho bảng `khuyen_mai`
--
ALTER TABLE `khuyen_mai`
  ADD PRIMARY KEY (`ma_km`);

--
-- Chỉ mục cho bảng `nha_cung_cap`
--
ALTER TABLE `nha_cung_cap`
  ADD PRIMARY KEY (`ma_nha_cung_cap`);

--
-- Chỉ mục cho bảng `order`
--
ALTER TABLE `order`
  ADD PRIMARY KEY (`ma_order`),
  ADD KEY `ma_khach_hang` (`ma_khach_hang`),
  ADD KEY `ma_khuyen_mai` (`ma_khuyen_mai`);

--
-- Chỉ mục cho bảng `order_detail`
--
ALTER TABLE `order_detail`
  ADD PRIMARY KEY (`ma_order_detail`),
  ADD KEY `ma_order` (`ma_order`),
  ADD KEY `ma_san_pham` (`ma_san_pham`),
  ADD KEY `ma_khach_hang` (`ma_khach_hang`);

--
-- Chỉ mục cho bảng `san_pham`
--
ALTER TABLE `san_pham`
  ADD PRIMARY KEY (`ma_san_pham`),
  ADD KEY `ma_danh_muc` (`ma_danh_muc`),
  ADD KEY `fk_ma_nha_cung_cap` (`ma_nha_cung_cap`);

--
-- Chỉ mục cho bảng `tai_khoan`
--
ALTER TABLE `tai_khoan`
  ADD PRIMARY KEY (`id_tk`),
  ADD UNIQUE KEY `ten_tk` (`ten_tk`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `danh_muc`
--
ALTER TABLE `danh_muc`
  MODIFY `ma_danh_muc` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã danh mục', AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT cho bảng `khach_hang`
--
ALTER TABLE `khach_hang`
  MODIFY `ma_kh` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã khách hàng', AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT cho bảng `khuyen_mai`
--
ALTER TABLE `khuyen_mai`
  MODIFY `ma_km` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã khuyến mãi', AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT cho bảng `nha_cung_cap`
--
ALTER TABLE `nha_cung_cap`
  MODIFY `ma_nha_cung_cap` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã nhà cung cấp', AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT cho bảng `order`
--
ALTER TABLE `order`
  MODIFY `ma_order` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- AUTO_INCREMENT cho bảng `order_detail`
--
ALTER TABLE `order_detail`
  MODIFY `ma_order_detail` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT cho bảng `san_pham`
--
ALTER TABLE `san_pham`
  MODIFY `ma_san_pham` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Mã sản phẩm', AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT cho bảng `tai_khoan`
--
ALTER TABLE `tai_khoan`
  MODIFY `id_tk` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `order`
--
ALTER TABLE `order`
  ADD CONSTRAINT `order_ibfk_1` FOREIGN KEY (`ma_khach_hang`) REFERENCES `khach_hang` (`ma_kh`),
  ADD CONSTRAINT `order_ibfk_2` FOREIGN KEY (`ma_khuyen_mai`) REFERENCES `khuyen_mai` (`ma_km`);

--
-- Các ràng buộc cho bảng `order_detail`
--
ALTER TABLE `order_detail`
  ADD CONSTRAINT `order_detail_ibfk_1` FOREIGN KEY (`ma_order`) REFERENCES `order` (`ma_order`),
  ADD CONSTRAINT `order_detail_ibfk_2` FOREIGN KEY (`ma_san_pham`) REFERENCES `san_pham` (`ma_san_pham`),
  ADD CONSTRAINT `order_detail_ibfk_3` FOREIGN KEY (`ma_khach_hang`) REFERENCES `khach_hang` (`ma_kh`);

--
-- Các ràng buộc cho bảng `san_pham`
--
ALTER TABLE `san_pham`
  ADD CONSTRAINT `fk_ma_nha_cung_cap` FOREIGN KEY (`ma_nha_cung_cap`) REFERENCES `nha_cung_cap` (`ma_nha_cung_cap`),
  ADD CONSTRAINT `san_pham_ibfk_1` FOREIGN KEY (`ma_danh_muc`) REFERENCES `danh_muc` (`ma_danh_muc`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
