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

  // ============================================================
  // 6. Công tắc chuyển Lưới / Kệ sách gỗ 3D (giữ lựa chọn qua localStorage)
  // ============================================================
  const viewButtons = document.querySelectorAll('.view-btn');
  const gridView = document.getElementById('view-grid');
  const shelfView = document.getElementById('view-shelf');

  if (viewButtons.length && gridView && shelfView) {
    const savedView = localStorage.getItem('libraryView') || 'grid';
    applyView(savedView);

    viewButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const target = btn.getAttribute('data-view');
        localStorage.setItem('libraryView', target);
        applyView(target);
      });
    });

    function applyView(target) {
      const isShelf = target === 'shelf';
      gridView.classList.toggle('is-hidden', isShelf);
      shelfView.classList.toggle('is-hidden', !isShelf);
      viewButtons.forEach(function (b) {
        b.classList.toggle('active', b.getAttribute('data-view') === target);
      });
    }
  }

  // ============================================================
  // 7. Reading Nook Mode — âm thanh nền (Web Audio API, không cần file)
  // ============================================================
  const nook = document.getElementById('nook');
  if (nook) {
    const nookToggle = document.getElementById('nookToggle');
    const nookPanel = document.getElementById('nookPanel');
    const nookClose = document.getElementById('nookClose');
    const nookVolume = document.getElementById('nookVolume');
    const nookFocus = document.getElementById('nookFocus');
    const fabDot = nook.querySelector('.nook-fab-dot');
    const trackButtons = nook.querySelectorAll('.nook-track');

    let audioCtx = null;
    let masterGain = null;
    let activeNodes = [];
    let activeTimers = [];
    let currentTrack = null;

    function ensureAudio() {
      if (!audioCtx) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return false;
        audioCtx = new Ctx();
        masterGain = audioCtx.createGain();
        masterGain.gain.value = (nookVolume ? nookVolume.value : 45) / 100 * 0.6;
        masterGain.connect(audioCtx.destination);
      }
      if (audioCtx.state === 'suspended') audioCtx.resume();
      return true;
    }

    function noiseBuffer(kind) {
      const len = Math.floor(audioCtx.sampleRate * 3);
      const buffer = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
      const data = buffer.getChannelData(0);
      let last = 0;
      for (let i = 0; i < len; i++) {
        const white = Math.random() * 2 - 1;
        if (kind === 'brown') {
          last = (last + 0.02 * white) / 1.02;
          data[i] = last * 3.2;
        } else {
          data[i] = white;
        }
      }
      return buffer;
    }

    function startLoopNoise(kind, filterType, freq, q, gainVal) {
      const src = audioCtx.createBufferSource();
      src.buffer = noiseBuffer(kind);
      src.loop = true;
      const filter = audioCtx.createBiquadFilter();
      filter.type = filterType;
      filter.frequency.value = freq;
      if (q) filter.Q.value = q;
      const gain = audioCtx.createGain();
      gain.gain.value = gainVal;
      src.connect(filter);
      filter.connect(gain);
      gain.connect(masterGain);
      src.start();
      activeNodes.push(src, filter, gain);
    }

    function scheduleTick(buildFn, minMs, maxMs) {
      function tick() {
        if (currentTrack === null) return;
        buildFn();
        activeTimers.push(setTimeout(tick, minMs + Math.random() * (maxMs - minMs)));
      }
      activeTimers.push(setTimeout(tick, 400 + Math.random() * 800));
    }

    function pageFlipSound() {
      const src = audioCtx.createBufferSource();
      const len = Math.floor(audioCtx.sampleRate * 0.18);
      const buf = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) {
        const env = Math.sin((i / len) * Math.PI);
        d[i] = (Math.random() * 2 - 1) * env * 0.5;
      }
      src.buffer = buf;
      const filter = audioCtx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.value = 2400 + Math.random() * 1600;
      filter.Q.value = 0.9;
      const gain = audioCtx.createGain();
      gain.gain.value = 0.5;
      src.connect(filter);
      filter.connect(gain);
      gain.connect(masterGain);
      src.start();
    }

    function cupClinkSound() {
      const osc = audioCtx.createOscillator();
      osc.type = 'sine';
      osc.frequency.value = 1400 + Math.random() * 900;
      const gain = audioCtx.createGain();
      gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.14, audioCtx.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.25);
      osc.connect(gain);
      gain.connect(masterGain);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.3);
    }

    const tracks = {
      rain: function () {
        // Mưa trên mái tôn: nhiễu trắng cao tần + nhiễu nâu làm rumble xa
        startLoopNoise('white', 'highpass', 900, 0.7, 0.16);
        startLoopNoise('white', 'bandpass', 3800, 0.5, 0.10);
        startLoopNoise('brown', 'lowpass', 320, 0.6, 0.22);
        scheduleTick(pageFlipSound, 900, 2400);
      },
      pages: function () {
        // Tiếng lật trang sách đều đặn, ấm
        startLoopNoise('brown', 'lowpass', 240, 0.5, 0.06);
        scheduleTick(pageFlipSound, 2200, 5200);
      },
      cafe: function () {
        // Quán cà phê ấm cúng: tiếng người xa (nhiễu nâu) + thỉnh thoảng ly tách
        startLoopNoise('brown', 'lowpass', 520, 0.6, 0.30);
        startLoopNoise('white', 'bandpass', 1500, 0.4, 0.035);
        scheduleTick(cupClinkSound, 3500, 9000);
      },
    };

    function stopAll() {
      activeTimers.forEach(clearTimeout);
      activeTimers = [];
      activeNodes.forEach(function (n) {
        try { if (n.stop) n.stop(); } catch (e) { /* đã dừng */ }
        try { n.disconnect(); } catch (e) { /* đã ngắt */ }
      });
      activeNodes = [];
    }

    function playTrack(name) {
      if (!ensureAudio()) return;
      stopAll();
      currentTrack = name;
      tracks[name]();
      nook.setAttribute('data-playing', name);
      if (fabDot) fabDot.hidden = false;
      trackButtons.forEach(function (b) {
        b.classList.toggle('active', b.getAttribute('data-track') === name);
      });
    }

    function pauseAll() {
      stopAll();
      currentTrack = null;
      nook.removeAttribute('data-playing');
      if (fabDot) fabDot.hidden = true;
      trackButtons.forEach(function (b) { b.classList.remove('active'); });
    }

    // Mở / đóng bảng điều khiển
    if (nookToggle) {
      nookToggle.addEventListener('click', function () {
        const open = nookPanel.hasAttribute('hidden');
        if (open) nookPanel.removeAttribute('hidden');
        else nookPanel.setAttribute('hidden', '');
        nookToggle.setAttribute('aria-expanded', String(open));
      });
    }
    if (nookClose) {
      nookClose.addEventListener('click', function () {
        nookPanel.setAttribute('hidden', '');
        nookToggle.setAttribute('aria-expanded', 'false');
      });
    }

    // Chọn / bỏ chọn track (bấm lại lần nữa để dừng)
    trackButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const name = btn.getAttribute('data-track');
        if (currentTrack === name) pauseAll();
        else playTrack(name);
      });
    });

    // Âm lượng
    if (nookVolume) {
      nookVolume.addEventListener('input', function () {
        if (masterGain) masterGain.gain.value = nookVolume.value / 100 * 0.6;
      });
    }

    // Focus Mode — giữ trạng thái qua sessionStorage
    function setFocusMode(on) {
      document.body.classList.toggle('focus-mode', on);
      if (nookFocus) {
        nookFocus.classList.toggle('active', on);
        nookFocus.setAttribute('aria-pressed', String(on));
        nookFocus.innerHTML = on
          ? '<i class="bi bi-check-circle-fill me-1"></i>Đang bật Chế độ Tập trung — bấm để tắt'
          : '<i class="bi bi-circle-square me-1"></i>Bật Chế độ Tập trung (Focus Mode)';
      }
      sessionStorage.setItem('libraryFocus', on ? '1' : '0');
    }
    if (sessionStorage.getItem('libraryFocus') === '1') setFocusMode(true);
    if (nookFocus) {
      nookFocus.addEventListener('click', function () {
        setFocusMode(!document.body.classList.contains('focus-mode'));
      });
    }

    // Tự dừng khi rời trang (tránh treo AudioContext)
    window.addEventListener('pagehide', pauseAll);
  }
});

