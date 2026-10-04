// ===== Thư viện Số — script chính =====
document.addEventListener('DOMContentLoaded', function () {
  // Tự động đóng thông báo flash sau 4 giây
  document.querySelectorAll('.flash-alert').forEach(function (el) {
    setTimeout(function () {
      try {
        new bootstrap.Alert(el).close();
      } catch (e) {
        el.style.display = 'none';
      }
    }, 4000);
  });

  // Xác nhận trước khi gửi các form nguy hiểm (xóa, từ chối...)
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!window.confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });
});
