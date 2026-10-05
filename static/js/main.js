// ===== Thư viện Số — Client Interaction Scripts =====
document.addEventListener('DOMContentLoaded', function () {
  // 1. Tự động đóng thông báo flash sau 5 giây với fade mượt mà
  document.querySelectorAll('.flash-alert').forEach(function (el) {
    setTimeout(function () {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
        if (bsAlert) bsAlert.close();
      } catch (e) {
        el.style.opacity = '0';
        el.style.transition = 'opacity 0.4s ease';
        setTimeout(() => el.remove(), 400);
      }
    }, 5000);
  });

  // 2. Xác nhận trước khi gửi các form thao tác (xóa, khóa, từ chối...)
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const promptText = form.dataset.confirm || 'Bạn có chắc chắn muốn thực hiện thao tác này?';
      if (!window.confirm(promptText)) {
        e.preventDefault();
      }
    });
  });

  // 3. Ẩn / Hiện mật khẩu (Password visibility toggler)
  document.querySelectorAll('.pwd-toggle-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      
      const icon = btn.querySelector('i');
      if (icon) {
        icon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
      }
      btn.setAttribute('aria-label', isPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
    });
  });

  // 4. Chọn nhanh tài khoản dùng thử trên trang Đăng nhập (Demo Account Switcher)
  const demoCards = document.querySelectorAll('.demo-card');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');

  if (demoCards.length > 0 && usernameInput && passwordInput) {
    demoCards.forEach(function (card) {
      card.addEventListener('click', function () {
        const user = card.getAttribute('data-user');
        const pass = card.getAttribute('data-pass');

        // Điền vào form
        usernameInput.value = user;
        passwordInput.value = pass;

        // Cập nhật trạng thái active
        demoCards.forEach(c => c.classList.remove('active'));
        card.classList.add('active');

        // Hiệu ứng phản hồi nhẹ
        usernameInput.classList.add('is-valid');
        passwordInput.classList.add('is-valid');
        setTimeout(() => {
          usernameInput.classList.remove('is-valid');
          passwordInput.classList.remove('is-valid');
        }, 1200);

        // Focus vào nút đăng nhập
        const submitBtn = document.querySelector('.auth-form-pane form button[type="submit"]');
        if (submitBtn) submitBtn.focus();
      });
    });
  }

  // 5. Thanh đo độ mạnh mật khẩu (Password Strength Meter) trên trang Đăng ký
  const registerPwd = document.getElementById('reg-password');
  const strengthWrap = document.getElementById('password-strength');

  if (registerPwd && strengthWrap) {
    const bars = strengthWrap.querySelectorAll('.strength-segment');
    const label = document.getElementById('strength-label');

    registerPwd.addEventListener('input', function () {
      const val = registerPwd.value;
      let score = 0;

      if (val.length >= 6) score++;
      if (val.length >= 9) score++;
      if (/[A-Z]/.test(val) || /[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;

      // Cập nhật màu các vạch
      bars.forEach((bar, idx) => {
        if (idx < score) {
          if (score === 1) bar.style.backgroundColor = 'var(--bad)';
          else if (score === 2) bar.style.backgroundColor = 'var(--warn)';
          else bar.style.backgroundColor = 'var(--ok)';
        } else {
          bar.style.backgroundColor = 'var(--line)';
        }
      });

      if (label) {
        if (val.length === 0) {
          label.textContent = '';
        } else if (score <= 1) {
          label.textContent = 'Mật khẩu yếu (nên thêm số hoặc ký tự đặc biệt)';
          label.style.color = 'var(--bad)';
        } else if (score === 2) {
          label.textContent = 'Mật khẩu trung bình';
          label.style.color = 'var(--warn)';
        } else {
          label.textContent = 'Mật khẩu mạnh & an toàn';
          label.style.color = 'var(--ok)';
        }
      }
    });
  }
});
