"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  let csrfToken = "";
  let requestBusy = false;
  let session = null;
  const passwordInputs = () => document.querySelectorAll('input[autocomplete="current-password"], input[autocomplete="new-password"]');

  function clearPasswords() {
    passwordInputs().forEach((input) => { input.value = ""; input.type = "password"; input.removeAttribute("aria-invalid"); });
    document.querySelectorAll("[data-password-target]").forEach((button) => {
      button.textContent = "Hiện";
      button.setAttribute("aria-label", "Hiện mật khẩu");
      button.setAttribute("aria-pressed", "false");
    });
  }

  function message(id, text = "", kind = "error", focus = false) {
    const box = $(id);
    box.textContent = text;
    box.className = `message ${kind}`;
    box.hidden = !text;
    if (text && focus) box.focus();
  }

  function setBusy(busy, operation = "") {
    requestBusy = busy;
    ["login-submit", "password-submit", "logout-button", "connection-retry"].forEach((id) => { $(id).disabled = busy; });
    $("login-form").setAttribute("aria-busy", String(busy && operation === "login"));
    $("change-password-form").setAttribute("aria-busy", String(busy && operation === "password"));
    $("login-button-label").textContent = busy ? (operation === "login" ? "Đang đăng nhập…" : "Đang kết nối…") : "Đăng nhập";
    $("logout-button").textContent = busy && operation === "logout" ? "Đang đăng xuất…" : "Đăng xuất ↗";
    $("password-submit").textContent = busy && operation === "password" ? "Đang lưu…" : "Lưu mật khẩu mới →";
  }

  async function api(path, options = {}) {
    let response;
    try {
      response = await fetch(path, { credentials: "same-origin", cache: "no-store", ...options,
        headers: { "Accept": "application/json", ...options.headers } });
    } catch (_) {
      throw { status: 0, code: "CONNECTION_ERROR" };
    }
    if (response.status === 204) return null;
    let data = null;
    try { data = await response.json(); } catch (_) { /* A proxy may return a non-JSON error page. */ }
    if (!response.ok) throw { status: response.status, code: data?.error?.code || data?.code || "REQUEST_FAILED", data };
    if (!data || typeof data !== "object") throw { status: 502, code: "INVALID_RESPONSE" };
    if (path === "/api/v1/auth/session") data.password_change_required = response.headers.get("X-VDT-Password-Change-Required") === "true";
    return data;
  }

  async function refreshCsrf() {
    const data = await api("/api/v1/auth/csrf");
    if (typeof data.csrf_token !== "string" || !data.csrf_token) throw { status: 502, code: "INVALID_RESPONSE" };
    csrfToken = data.csrf_token;
  }

  async function mutate(path, method, body) {
    if (!csrfToken) await refreshCsrf();
    return api(path, { method, headers: { "X-CSRFToken": csrfToken, ...(body ? { "Content-Type": "application/json" } : {}) }, ...(body ? { body: JSON.stringify(body) } : {}) });
  }

  function errorText(error, context) {
    if (error.status === 0) return "Chưa kết nối được với ứng dụng. Hãy kiểm tra lab local đã chạy, rồi thử lại.";
    if (error.status === 429) return "Bạn đã thử quá nhiều lần. Vui lòng đợi một lúc trước khi thử lại.";
    if (error.status >= 500) return "Dịch vụ hiện chưa sẵn sàng. Vui lòng kiểm tra lab local và thử lại sau.";
    if (context === "login" && (error.status === 401 || error.status === 400 || error.status === 422)) return "Không thể đăng nhập. Hãy kiểm tra tên đăng nhập và mật khẩu.";
    if (error.status === 403) return "Yêu cầu chưa được xác nhận. Hãy tải lại trang và thực hiện lại thao tác.";
    if (context === "password" && error.code === "INVALID_CREDENTIALS") return "Mật khẩu hiện tại chưa đúng. Vui lòng nhập lại; bạn vẫn đang đăng nhập.";
    if (context === "password" && error.status === 422) return "Mật khẩu mới cần ít nhất 12 ký tự, không phổ biến, không chỉ gồm số và khác mật khẩu hiện tại. Vui lòng chọn mật khẩu khác.";
    if (context === "password" && error.status === 400) return "Chưa đổi được mật khẩu. Hãy kiểm tra mật khẩu hiện tại và chọn mật khẩu mới dài, khó đoán, khác mật khẩu cũ.";
    return "Chưa thực hiện được thao tác. Vui lòng thử lại.";
  }

  function readableTime(value) {
    if (typeof value !== "string") return "Chưa có thông tin";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Chưa có thông tin";
    return new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "medium" }).format(date);
  }

  function showLogin(text = "", kind = "notice", focus = false) {
    session = null;
    clearPasswords();
    $("session-view").hidden = true;
    $("login-view").hidden = false;
    $("display-name").textContent = "";
    $("permissions-list").replaceChildren();
    $("idle-expiry").textContent = "—";
    $("absolute-expiry").textContent = "—";
    $("admin-navigation").hidden = true;
    $("assessment-navigation").hidden = true;
    $("assessment-access-help").hidden = true;
    $("temporary-password-notice").hidden = true;
    message("session-message");
    message("password-message");
    message("login-message", text, kind, focus && Boolean(text));
    document.title = "Đăng nhập · VN Digital Trust";
    if (focus && !text) $("username").focus();
  }

  function showSession(data, focus = false) {
    if (typeof data.user_id !== "string" || !Array.isArray(data.permissions)) throw { status: 502, code: "INVALID_RESPONSE" };
    session = data;
    if (typeof data.csrf_token === "string" && data.csrf_token) csrfToken = data.csrf_token;
    clearPasswords();
    $("login-view").hidden = true;
    $("session-view").hidden = false;
    $("connection-retry").hidden = true;
    message("login-message");
    $("display-name").textContent = typeof data.display_name === "string" && data.display_name.trim() ? data.display_name : "bạn";
    $("idle-expiry").textContent = readableTime(data.idle_expires_at);
    $("absolute-expiry").textContent = readableTime(data.absolute_expires_at);
    const permissions = [...new Set(data.permissions.filter((item) => typeof item === "string"))].sort();
    $("permissions-list").replaceChildren(...permissions.map((permission) => {
      const item = document.createElement("li");
      item.textContent = permission;
      return item;
    }));
    $("permissions-empty").hidden = permissions.length > 0;
    $("admin-navigation").hidden = data.password_change_required || !["organization.manage", "users.manage", "roles.assign"].every((permission) => permissions.includes(permission));
    const canOpenAssessments = permissions.some((permission) => ["assessment.run", "assessment.review", "report.read"].includes(permission));
    $("assessment-navigation").hidden = data.password_change_required || !canOpenAssessments;
    $("assessment-access-help").hidden = data.password_change_required || canOpenAssessments;
    $("assessment-access-help").textContent = permissions.includes("roles.assign")
      ? "Để tạo đợt đánh giá, hãy vào Quản lý người dùng & phân quyền, cấp vai trò An toàn thông tin cho một tài khoản theo chi nhánh, rồi đăng nhập tài khoản đó. Vai trò Quản trị viên chỉ quản lý tài khoản và phân quyền."
      : "Tài khoản chưa có quyền mở đợt đánh giá. Quản trị viên cần cấp vai trò An toàn thông tin để tạo đợt, hoặc giao một đợt cụ thể cho Người thẩm định. Sau khi được cấp quyền, hãy tải lại trang.";
    $("temporary-password-notice").hidden = !data.password_change_required;
    document.title = "Tài khoản · VN Digital Trust";
    if (focus) $("session-title").focus();
  }

  async function connect() {
    if (requestBusy) return;
    setBusy(true, "connect");
    $("connection-retry").hidden = true;
    try {
      await refreshCsrf();
      try { showSession(await api("/api/v1/auth/session")); }
      catch (error) { if (error.status === 401) showLogin(); else throw error; }
    } catch (error) {
      showLogin(errorText(error, "connect"), "error");
      $("connection-retry").hidden = false;
    } finally { setBusy(false); }
  }

  $("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (requestBusy) return;
    if (!event.currentTarget.reportValidity()) return;
    const username = $("username").value.trim();
    const password = $("password").value;
    if (!username) { $("username").focus(); return; }
    setBusy(true, "login");
    message("login-message");
    try { showSession(await mutate("/api/v1/auth/session", "POST", { username, password }), true); }
    catch (error) {
      message("login-message", errorText(error, "login"), "error", true);
      if (error.status === 403) csrfToken = "";
      $("connection-retry").hidden = !(error.status === 0 || error.status >= 500);
    } finally { clearPasswords(); setBusy(false); }
  });

  $("logout-button").addEventListener("click", async () => {
    if (requestBusy) return;
    setBusy(true, "logout");
    message("session-message");
    clearPasswords();
    try {
      await mutate("/api/v1/auth/session", "DELETE");
      csrfToken = "";
      showLogin("Bạn đã đăng xuất an toàn.", "success", true);
    } catch (error) {
      if (error.status === 401) { csrfToken = ""; showLogin("Phiên đã kết thúc. Bạn có thể đăng nhập lại.", "notice", true); }
      else message("session-message", "Chưa xác nhận được đăng xuất. " + errorText(error, "logout"), "error", true);
    } finally { setBusy(false); }
  });

  $("change-password-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (requestBusy) return;
    if (!event.currentTarget.reportValidity()) return;
    message("password-message");
    if ($("new-password").value !== $("confirm-password").value) {
      clearPasswords();
      $("confirm-password").setAttribute("aria-invalid", "true");
      message("password-message", "Hai lần nhập mật khẩu mới chưa khớp. Vui lòng nhập lại.", "error", true);
      return;
    }
    const current_password = $("current-password").value;
    const new_password = $("new-password").value;
    setBusy(true, "password");
    let changed = false;
    try {
      await mutate("/api/v1/auth/password", "POST", { current_password, new_password });
      changed = true;
      clearPasswords();
      csrfToken = "";
      await refreshCsrf();
      showSession(await api("/api/v1/auth/session"));
      message("password-message", "Đã đổi mật khẩu. Hãy dùng mật khẩu mới cho lần đăng nhập tiếp theo.", "success", true);
    } catch (error) {
      if (error.status === 401 && error.code !== "INVALID_CREDENTIALS") {
        csrfToken = "";
        showLogin(changed ? "Đã đổi mật khẩu. Vui lòng đăng nhập lại bằng mật khẩu mới." : "Phiên đã hết hạn hoặc bị thu hồi. Vui lòng đăng nhập lại.", "notice", true);
      } else if (changed) {
        message("password-message", "Đã đổi mật khẩu, nhưng chưa tải lại được thông tin phiên. Hãy tải lại trang; dùng mật khẩu mới nếu được yêu cầu đăng nhập.", "notice", true);
      } else if (error.status === 0) {
        message("password-message", "Mất kết nối nên chưa xác nhận được việc đổi mật khẩu. Hãy kiểm tra kết nối và tải lại trang. Nếu cần đăng nhập lại, thử mật khẩu mới trước.", "notice", true);
      } else {
        message("password-message", errorText(error, "password"), "error", true);
        if (error.status === 403) csrfToken = "";
      }
    } finally { clearPasswords(); setBusy(false); }
  });

  document.querySelectorAll("[data-password-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = $(button.dataset.passwordTarget);
      const visible = input.type === "password";
      input.type = visible ? "text" : "password";
      button.textContent = visible ? "Ẩn" : "Hiện";
      button.setAttribute("aria-label", visible ? "Ẩn mật khẩu" : "Hiện mật khẩu");
      button.setAttribute("aria-pressed", String(visible));
    });
  });
  $("connection-retry").addEventListener("click", connect);
  window.addEventListener("pagehide", clearPasswords);
  window.addEventListener("pageshow", (event) => { if (event.persisted) window.location.reload(); });
  void connect();
})();
