"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  const API = "/api/v1/";
  const state = { session: null, organization: null, users: [], branches: [], roles: [], permissions: [], grants: [], assessments: [], audit: [], auditCursor: null, selected: null, revoked: null, busy: false, stale: false, csrf: "" };
  // Only a request fingerprint and key are retained in this page's memory.
  // Passwords, request bodies and credentials never enter browser storage.
  const attempts = new Map();
  const roleNames = { VDT_ADMIN: "Quản trị viên", VDT_SECURITY: "An toàn thông tin", VDT_RISK_OWNER: "Chủ sở hữu rủi ro", VDT_REVIEWER: "Người thẩm định" };
  const roleDescriptions = { VDT_ADMIN: "Quản lý tài khoản và phân quyền.", VDT_SECURITY: "Làm việc với bằng chứng trong phạm vi được cấp.", VDT_RISK_OWNER: "Đánh giá và chốt ưu tiên rủi ro.", VDT_REVIEWER: "Thẩm định theo đợt đánh giá được giao." };
  const actions = { "user.create": "Tạo tài khoản", "user.update": "Cập nhật tài khoản", "user.credential_reset": "Đặt mật khẩu tạm", "role_assignment.grant": "Cấp vai trò", "role_assignment.revoke": "Thu hồi vai trò", "auth.login": "Đăng nhập", "auth.logout": "Đăng xuất", "auth.password": "Đổi mật khẩu", "auth.session.invalidate": "Kết thúc phiên không còn hợp lệ" };
  const time = (value) => { const d = new Date(value); return value && !Number.isNaN(d.getTime()) ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short" }).format(d) : "—"; };
  const localTime = (date) => new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  const node = (tag, text, className) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (className) n.className = className; return n; };
  const userName = (id) => { const u = state.users.find((x) => x.id === id); return u ? u.display_name || u.username : "Tài khoản không có trong danh sách"; };
  const roleName = (id) => { const role = state.roles.find((x) => x.id === id); return role ? roleNames[role.code] || role.code : "Vai trò"; };

  function message(id, text = "", kind = "error", focus = false) {
    const box = $(id); box.textContent = text; box.className = `message ${kind}`; box.hidden = !text;
    if (text && focus) box.focus();
  }
  function clearPasswords() { $("temporary-password").value = ""; $("temporary-confirm").value = ""; }
  function busy(value) {
    state.busy = value;
    document.querySelectorAll("form").forEach((form) => form.setAttribute("aria-busy", String(value)));
    document.querySelectorAll("button, input, select, textarea").forEach((control) => { control.disabled = value; });
    if (!value) {
      $("user-active").disabled = state.selected?.id === state.session?.user_id;
      $("save-user-button").disabled = state.stale;
      $("credential-submit").disabled = state.stale;
      $("audit-more").disabled = !state.auditCursor;
      document.querySelectorAll("[data-permanent-disabled]").forEach((control) => { control.disabled = true; });
    }
  }
  async function api(path, options = {}) {
    let response;
    try { response = await fetch(path, { credentials: "same-origin", cache: "no-store", ...options, headers: { Accept: "application/json", ...options.headers } }); }
    catch (_) { throw { status: 0, code: "CONNECTION_ERROR" }; }
    let data = null;
    if (response.status !== 204) { try { data = await response.json(); } catch (_) { /* Proxy errors may not be JSON. */ } }
    if (!response.ok) {
      const error = { status: response.status, code: data?.code || data?.error?.code || "REQUEST_FAILED", detail: data?.detail };
      if (response.status === 401 || error.code === "PASSWORD_CHANGE_REQUIRED") {
        clearPasswords(); window.location.replace("/");
      }
      throw error;
    }
    if (path === API + "auth/session" && data) data.password_change_required = response.headers.get("X-VDT-Password-Change-Required") === "true";
    if (response.status !== 204 && (!data || typeof data !== "object")) throw { status: 502, code: "INVALID_RESPONSE" };
    return data;
  }
  async function csrf() { state.csrf = (await api(API + "auth/csrf")).csrf_token; }
  function errorText(error) {
    if (error.status === 0) return "Mất kết nối nên chưa xác nhận được thao tác. Kiểm tra kết nối rồi gửi lại cùng nội dung để tránh tạo trùng.";
    if (error.status === 401) return "Phiên đã kết thúc. Đang chuyển về trang đăng nhập…";
    if (error.code === "PASSWORD_CHANGE_REQUIRED") return "Bạn cần đổi mật khẩu tạm. Đang chuyển về trang tài khoản…";
    if (error.code === "SELF_LOCKOUT") return "Bạn không thể khóa chính tài khoản đang dùng.";
    if (error.code === "LAST_ADMIN" || error.code === "LAST_ADMIN_REQUIRED") return "Cần giữ ít nhất một quản trị viên có thể đăng nhập. Hãy chuẩn bị tài khoản quản trị khác trước.";
    if (error.code === "DELEGATION_EXPIRES") return "Thời hạn cấp quyền vượt quá thời hạn quản trị của bạn. Hãy chọn ngày hết hạn sớm hơn.";
    if (error.status === 403) return "Bạn không còn quyền thực hiện thao tác này, hoặc yêu cầu chưa được xác nhận. Hãy tải lại trang để kiểm tra.";
    if (error.status === 404) return "Không tìm thấy dữ liệu trong phạm vi của bạn. Hãy làm mới danh sách.";
    if ([409, 412, 428].includes(error.status)) return "Dữ liệu đã thay đổi hoặc cần đọc lại trước khi lưu. Danh sách đã được làm mới; hãy kiểm tra lại nội dung trước khi gửi.";
    if (error.status === 422 || error.status === 400) return error.detail || "Nội dung chưa hợp lệ. Hãy kiểm tra tên đăng nhập, phạm vi, thời hạn và lý do.";
    if (error.status === 429) return "Có quá nhiều yêu cầu. Vui lòng đợi một lúc rồi thử lại.";
    if (error.status >= 500) return "Dịch vụ chưa sẵn sàng; chưa xác nhận được thao tác. Thử lại cùng nội dung sau khi lab hoạt động bình thường.";
    return "Chưa thực hiện được thao tác. Hãy kiểm tra và thử lại.";
  }
  async function collection(name) {
    const rows = [], seen = new Set(); let cursor = null;
    do {
      const page = await api(API + name + "?limit=200" + (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""));
      if (!Array.isArray(page.items)) throw { status: 502, code: "INVALID_RESPONSE" };
      rows.push(...page.items); cursor = page.next_cursor;
      if (cursor && seen.has(cursor)) throw { status: 502, code: "INVALID_RESPONSE" };
      if (cursor) seen.add(cursor);
    } while (cursor);
    return rows;
  }
  function context(reason, user) {
    const dependencies = [{ resource_type: "organization", id: state.organization.id, version: state.organization.version }];
    if (user) dependencies.push({ resource_type: "user", id: user.id, version: user.version });
    return { dependencies, reason: reason.trim() };
  }
  async function mutate(form, path, method, body, version) {
    if (!state.csrf) await csrf();
    const text = JSON.stringify(body);
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(path + "\n" + method + "\n" + String(version ?? "") + "\n" + text));
    const signature = Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
    let attempt = attempts.get(form);
    if (!attempt || attempt.signature !== signature) { attempt = { signature, key: crypto.randomUUID() }; attempts.set(form, attempt); }
    const result = await api(path, { method, headers: { "Content-Type": "application/json", "X-CSRFToken": state.csrf, "Idempotency-Key": attempt.key, ...(version === undefined ? {} : { "If-Match": `"${version}"` }) }, body: text });
    attempts.delete(form); return result;
  }
  function selectedBranches(id) { return [...$(id).querySelectorAll("input:checked")].map((input) => input.value).sort(); }
  function branchChecks(id, selected = []) {
    const items = state.branches.filter((branch) => branch.active || selected.includes(branch.id));
    $(id).replaceChildren(...items.map((branch) => {
      const label = node("label", undefined, "check-line"), input = node("input"); input.type = "checkbox"; input.value = branch.id; input.checked = selected.includes(branch.id);
      if (!branch.active) { input.disabled = true; input.dataset.permanentDisabled = "true"; }
      label.append(input, node("span", `${branch.name} (${branch.code})${branch.active ? "" : " · không hoạt động"}`)); return label;
    }));
    if (!items.length) $(id).append(node("p", "Chưa có chi nhánh hoạt động.", "field-help"));
  }
  function renderUsers() {
    const query = $("user-search").value.trim().toLocaleLowerCase("vi");
    const users = [...state.users].sort((a, b) => a.display_name.localeCompare(b.display_name, "vi")).filter((u) => !query || `${u.username} ${u.display_name}`.toLocaleLowerCase("vi").includes(query));
    $("users-count").textContent = String(state.users.length);
    $("users-body").replaceChildren(...users.map((user) => {
      const tr = node("tr"); tr.classList.toggle("selected", state.selected?.id === user.id);
      const name = node("td"); name.append(node("span", user.display_name, "cell-main"), node("span", `${user.username}${user.id === state.session.user_id ? " · bạn" : ""}`, "cell-sub"));
      const branches = node("td", user.branch_ids.map((id) => state.branches.find((b) => b.id === id)?.name || "Chi nhánh không còn hoạt động").join(", ") || "Chưa gắn chi nhánh");
      const status = node("td"); status.append(node("span", user.active ? "Hoạt động" : "Đã khóa", `status-badge${user.active ? "" : " off"}`));
      const cell = node("td"), button = node("button", "Chỉnh sửa", "row-button"); button.type = "button"; button.setAttribute("aria-label", "Chỉnh sửa " + user.display_name); button.addEventListener("click", () => { if (!state.busy) selectUser(user); }); cell.append(button);
      tr.append(name, branches, status, cell); return tr;
    }));
    $("users-empty").hidden = users.length > 0;
    const choice = $("grant-user").value;
    $("grant-user").replaceChildren(node("option", "Chọn người dùng"), ...state.users.filter((u) => u.active).sort((a,b) => a.display_name.localeCompare(b.display_name,"vi")).map((u) => { const option = node("option", `${u.display_name} (${u.username})`); option.value = u.id; return option; }));
    $("grant-user").firstElementChild.value = ""; $("grant-user").value = choice;
  }
  function selectUser(user, focus = true) {
    state.selected = user || null; state.stale = false; attempts.delete("user"); attempts.delete("credential"); clearPasswords();
    $("user-form").reset(); $("credential-form").reset();
    $("user-username").value = user?.username || ""; $("user-display").value = user?.display_name || ""; $("user-active").checked = user ? user.active : true;
    const self = user?.id === state.session.user_id;
    $("user-active").disabled = self; $("self-help").hidden = !self; $("credential-card").hidden = !user || self;
    $("editor-eyebrow").textContent = user ? "HỒ SƠ TÀI KHOẢN" : "TẠO TÀI KHOẢN"; $("editor-title").textContent = user ? user.display_name : "Người dùng mới";
    $("editor-help").textContent = user ? "Thay đổi hồ sơ hoặc trạng thái đăng nhập. Ghi lý do để lưu vào nhật ký." : "Tạo tài khoản, sau đó đặt mật khẩu tạm và cấp vai trò phù hợp.";
    $("save-user-button").textContent = user ? "Lưu thay đổi" : "Tạo tài khoản"; $("save-user-button").disabled = false; $("credential-submit").disabled = false;
    $("reload-user-button").hidden = true; branchChecks("user-branches", user?.branch_ids || []); message("user-message"); message("credential-message"); renderUsers();
    if (focus) $("user-username").focus();
  }
  function renderRoles() {
    $("role-catalog").replaceChildren(...state.roles.map((role) => {
      const card = node("section", undefined, "role-card"); card.append(node("h3", roleNames[role.code] || role.code), node("p", roleDescriptions[role.code] || "Vai trò trong VDT."));
      const details = node("details"), list = node("ul"); details.append(node("summary", `${role.permission_codes.length} quyền trong danh mục`));
      role.permission_codes.forEach((code) => { const item = node("li"), label = node("code", code); item.append(label); const description = state.permissions.find((p) => p.code === code)?.description; if (description) item.append(document.createTextNode(" — " + description)); list.append(item); });
      details.append(list); card.append(details); return card;
    }));
    const selected = $("grant-role").value;
    $("grant-role").replaceChildren(node("option", "Chọn vai trò"), ...state.roles.map((role) => { const option = node("option", roleNames[role.code] || role.code); option.value = role.id; return option; }));
    $("grant-role").firstElementChild.value = ""; $("grant-role").value = selected; grantScope();
  }
  function grantScope() { const code = state.roles.find((r) => r.id === $("grant-role").value)?.code; $("admin-scope-note").hidden = code !== "VDT_ADMIN"; $("grant-branch-field").hidden = code === "VDT_ADMIN" || code === "VDT_REVIEWER"; $("grant-assessment-field").hidden = code !== "VDT_REVIEWER"; $("grant-end").required = code === "VDT_REVIEWER"; $("grant-assessment").required = code === "VDT_REVIEWER"; }
  function renderGrants() {
    const grants = [...state.grants].sort((a, b) => new Date(b.effective_at) - new Date(a.effective_at));
    $("grants-body").replaceChildren(...grants.map((grant) => {
      const row = node("tr"), person = node("td"); person.append(node("span", userName(grant.user_id), "cell-main"), node("span", roleName(grant.role_id), "cell-sub"));
      const selectors = grant.scope;
      const labels = selectors.branch_ids.map((id) => state.branches.find((branch) => branch.id === id)?.name || "Chi nhánh");
      const otherCount = ["system_ids", "asset_ids", "data_asset_ids", "scenario_ids", "assessment_ids"].reduce((sum, key) => sum + (selectors[key]?.length || 0), 0);
      if (otherCount) labels.push(`${otherCount} đối tượng được chọn`);
      const scope = node("td", labels.join(", ") || "Quản trị tổ chức");
      const validity = node("td"); const expired = grant.access_expires_at && new Date(grant.access_expires_at) <= new Date(); const future = new Date(grant.effective_at) > new Date();
      validity.append(node("span", grant.revoked_at ? "Đã thu hồi" : expired ? "Đã hết hạn" : future ? "Chưa hiệu lực" : "Đang hiệu lực", `status-badge${grant.revoked_at || expired ? " off" : future ? " soon" : ""}`), node("span", `Từ ${time(grant.effective_at)}`, "cell-sub"), node("span", grant.access_expires_at ? `Đến ${time(grant.access_expires_at)}` : "Không ấn định ngày hết hạn", "cell-sub"));
      const action = node("td");
      if (!grant.revoked_at) { const button = node("button", "Thu hồi", "row-button danger"); button.type = "button"; button.setAttribute("aria-label", `Thu hồi ${roleName(grant.role_id)} của ${userName(grant.user_id)}`); button.addEventListener("click", () => { if (state.busy) return; state.revoked = grant; attempts.delete("revoke"); $("revoke-form").reset(); $("revoke-box").hidden = false; $("revoke-label").textContent = `${userName(grant.user_id)} · ${roleName(grant.role_id)}`; message("revoke-message"); $("revoke-reason").focus(); }); action.append(button); }
      row.append(person, scope, validity, action); return row;
    }));
    $("grants-empty").hidden = grants.length > 0;
  }
  function renderAudit() {
    $("audit-body").replaceChildren(...[...state.audit].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).map((entry) => {
      const tr = node("tr"); const action = node("td"); action.append(node("span", actions[entry.action] || entry.action, "cell-main"));
      if (entry.reason_code) action.append(node("span", entry.reason_code, "cell-sub"));
      const outcome = node("td"); outcome.append(node("span", entry.outcome === "ALLOWED" ? "Được phép" : entry.outcome === "DENIED" ? "Bị từ chối" : entry.outcome, `status-badge${entry.outcome === "ALLOWED" ? "" : " off"}`));
      tr.append(node("td", time(entry.created_at)), node("td", entry.created_by ? userName(entry.created_by) : "Hệ thống"), action, outcome); return tr;
    }));
    $("audit-empty").hidden = state.audit.length > 0; $("audit-more").hidden = !state.auditCursor;
  }
  async function auditPage(reset = false) {
    const page = await api(API + "audit-events?limit=50" + (!reset && state.auditCursor ? "&cursor=" + encodeURIComponent(state.auditCursor) : ""));
    state.audit = reset ? page.items : [...state.audit, ...page.items]; state.auditCursor = page.next_cursor; renderAudit();
  }
  async function reloadData() {
    const [organization, branches, users, roles, permissions, grants, assessments] = await Promise.all([api(API + "organization"), collection("branches"), collection("users"), collection("roles"), collection("permissions"), collection("role-assignments"), collection("admin/assessments")]);
    Object.assign(state, { organization, branches, users, roles, permissions, grants, assessments });
    const assessmentChoice = $("grant-assessment").value;
    $("grant-assessment").replaceChildren(node("option", "Chọn đợt đang mở"), ...assessments.filter((a) => a.state === "OPEN").map((a) => { const option = node("option", `${a.code} · ${a.name}`); option.value = a.id; return option; }));
    $("grant-assessment").firstElementChild.value = ""; $("grant-assessment").value = assessmentChoice;
    $("organization-label").textContent = `${organization.name} · ${state.session.display_name}`;
    renderUsers(); renderRoles(); renderGrants(); await auditPage(true);
  }
  async function writeFailure(error, messageId, form) {
    if (error.status === 403) state.csrf = "";
    if ([409, 412, 428].includes(error.status)) {
      attempts.delete(form);
      try { await reloadData(); }
      catch (_) { message("page-message", "Chưa tải lại được dữ liệu mới. Hãy kiểm tra kết nối và bấm Làm mới.", "notice"); }
      if (form === "user" || form === "credential") { state.stale = true; $("reload-user-button").hidden = false; }
      if (form === "revoke") { state.revoked = null; $("revoke-box").hidden = true; messageId = "page-message"; }
    }
    message(messageId, errorText(error), "error", true);
  }
  async function afterWrite(text) {
    try { await reloadData(); message("page-message", text, "success"); }
    catch (_) { message("page-message", text + " Chưa tải được danh sách mới; bấm Làm mới trước thao tác tiếp theo.", "notice", true); }
  }

  $("user-form").addEventListener("submit", async (event) => {
    event.preventDefault(); if (state.busy || state.stale || !event.currentTarget.reportValidity()) return;
    const selected = state.selected, body = { username: $("user-username").value.trim(), display_name: $("user-display").value.trim(), active: $("user-active").checked, branch_ids: selectedBranches("user-branches"), write_context: context($("user-reason").value) };
    busy(true); message("user-message");
    try {
      const result = await mutate("user", API + "users" + (selected ? "/" + selected.id : ""), selected ? "PATCH" : "POST", body, selected?.version);
      await afterWrite(selected ? "Đã lưu thông tin tài khoản." : "Đã tạo tài khoản. Tiếp theo, đặt mật khẩu tạm và cấp vai trò.");
      if (!state.users.some((u) => u.id === result.id)) state.users.push(result);
      selectUser(result, false); message("user-message", selected ? "Đã lưu thay đổi." : "Tài khoản đã được tạo. Đặt mật khẩu tạm ở bên dưới để người dùng đăng nhập.", "success", true);
    } catch (error) { await writeFailure(error, "user-message", "user"); }
    finally { busy(false); }
  });
  $("credential-form").addEventListener("submit", async (event) => {
    event.preventDefault(); if (state.busy || state.stale || !state.selected || state.selected.id === state.session.user_id || !event.currentTarget.reportValidity()) return;
    if ($("temporary-password").value !== $("temporary-confirm").value) { clearPasswords(); message("credential-message", "Hai lần nhập mật khẩu tạm chưa khớp. Vui lòng nhập lại.", "error", true); return; }
    busy(true); message("credential-message"); const id = state.selected.id;
    try {
      await mutate("credential", API + "users/" + id + "/credential-resets", "POST", { temporary_password: $("temporary-password").value, force_change: true, write_context: context($("credential-reason").value) }, state.selected.version);
      clearPasswords(); await afterWrite("Đã đặt mật khẩu tạm và thu hồi các phiên cũ của người dùng.");
      const fresh = state.users.find((u) => u.id === id); if (fresh) selectUser(fresh, false);
      message("credential-message", "Đã đặt mật khẩu tạm. Người dùng cần đổi mật khẩu sau lần đăng nhập tiếp theo.", "success", true);
    } catch (error) { await writeFailure(error, "credential-message", "credential"); }
    finally { clearPasswords(); busy(false); }
  });
  $("grant-form").addEventListener("submit", async (event) => {
    event.preventDefault(); if (state.busy || !event.currentTarget.reportValidity()) return;
    const user = state.users.find((u) => u.id === $("grant-user").value), role = state.roles.find((r) => r.id === $("grant-role").value);
    if (!user || !role) { message("grant-message", "Chọn người dùng và vai trò hợp lệ.", "error", true); return; }
    const assessment = role.code === "VDT_REVIEWER" ? state.assessments.find((a) => a.id === $("grant-assessment").value && a.state === "OPEN") : null;
    if (role.code === "VDT_REVIEWER" && !assessment) { message("grant-message", "Chọn một đợt đánh giá đang mở.", "error", true); return; }
    const branches = role.code === "VDT_ADMIN" ? [] : role.code === "VDT_REVIEWER" ? assessment.scope.branch_ids : selectedBranches("grant-branches");
    if (role.code !== "VDT_ADMIN" && !branches.length) { message("grant-message", "Chọn ít nhất một chi nhánh cho vai trò này.", "error", true); return; }
    const start = new Date($("grant-start").value), end = $("grant-end").value ? new Date($("grant-end").value) : null;
    if (Number.isNaN(start.getTime()) || (end && (Number.isNaN(end.getTime()) || end <= start || end <= new Date())) || (role.code === "VDT_REVIEWER" && !end)) { message("grant-message", "Ngày hết hạn phải sau ngày bắt đầu và sau thời điểm hiện tại.", "error", true); return; }
    const assigned = assessment ? [assessment.id] : [];
    const writeContext = context($("grant-reason").value, user);
    if (assessment) writeContext.dependencies.push({ resource_type: "assessment", id: assessment.id, version: assessment.version });
    const body = { user_id: user.id, role_id: role.id, scope: { organization_id: state.organization.id, branch_ids: branches, system_ids: [], asset_ids: [], data_asset_ids: [], scenario_ids: [], assessment_ids: assigned }, assigned_assessment_ids: assigned, effective_at: start.toISOString(), access_expires_at: end?.toISOString() || null, write_context: writeContext };
    busy(true); message("grant-message");
    try { await mutate("grant", API + "role-assignments", "POST", body); await afterWrite("Đã cấp vai trò trong phạm vi và thời hạn đã chọn."); $("grant-reason").value = ""; message("grant-message", "Đã cấp quyền. Kiểm tra lượt cấp mới trong danh sách.", "success", true); }
    catch (error) { await writeFailure(error, "grant-message", "grant"); }
    finally { busy(false); }
  });
  $("revoke-form").addEventListener("submit", async (event) => {
    event.preventDefault(); if (state.busy || !state.revoked || !event.currentTarget.reportValidity()) return;
    const grant = state.revoked, user = state.users.find((u) => u.id === grant.user_id);
    if (!user) { message("revoke-message", "Hãy làm mới danh sách trước khi thu hồi.", "error", true); return; }
    busy(true); message("revoke-message");
    try { await mutate("revoke", API + "role-assignments/" + grant.id + "/revocations", "POST", { write_context: context($("revoke-reason").value, user) }, grant.version); state.revoked = null; $("revoke-box").hidden = true; await afterWrite("Đã thu hồi lượt cấp quyền."); }
    catch (error) { await writeFailure(error, "revoke-message", "revoke"); }
    finally { busy(false); }
  });
  $("refresh-button").addEventListener("click", async () => {
    if (state.busy) return; busy(true); clearPasswords();
    try { await reloadData(); selectUser(state.users.find((u) => u.id === state.selected?.id) || null, false); branchChecks("grant-branches"); state.revoked = null; $("revoke-box").hidden = true; message("page-message", "Đã tải lại dữ liệu mới. Kiểm tra nội dung trước khi lưu.", "notice"); }
    catch (error) { message("page-message", errorText(error), "error", true); }
    finally { busy(false); }
  });
  $("reload-user-button").addEventListener("click", () => { if (!state.busy) selectUser(state.users.find((u) => u.id === state.selected?.id) || null); });
  $("new-user-button").addEventListener("click", () => { if (!state.busy) selectUser(null); });
  $("user-search").addEventListener("input", renderUsers);
  $("grant-role").addEventListener("change", grantScope);
  $("revoke-cancel").addEventListener("click", () => { state.revoked = null; $("revoke-box").hidden = true; attempts.delete("revoke"); });
  $("audit-more").addEventListener("click", async () => { if (state.busy || !state.auditCursor) return; busy(true); try { await auditPage(); } catch (error) { message("page-message", errorText(error), "error", true); } finally { busy(false); } });
  document.querySelectorAll("[data-panel]").forEach((button) => button.addEventListener("click", () => {
    if (state.busy) return; clearPasswords(); document.querySelectorAll("[data-panel]").forEach((tab) => { if (tab === button) tab.setAttribute("aria-current", "page"); else tab.removeAttribute("aria-current"); $("panel-" + tab.dataset.panel).hidden = tab !== button; });
  }));
  window.addEventListener("pagehide", () => { clearPasswords(); attempts.clear(); });
  window.addEventListener("pageshow", (event) => { if (event.persisted) window.location.reload(); });
  async function start() {
    busy(true);
    try {
      state.session = await api(API + "auth/session");
      if (state.session.password_change_required) { window.location.replace("/"); return; }
      if (!["organization.manage", "users.manage", "roles.assign"].every((permission) => state.session.permissions.includes(permission))) { message("page-message", "Tài khoản hiện tại chưa có đủ quyền quản trị. Trở về Tài khoản của tôi để xem quyền được cấp.", "notice"); return; }
      await csrf(); await reloadData(); branchChecks("grant-branches"); selectUser(null, false); $("grant-start").value = localTime(new Date());
      $("admin-content").hidden = false; message("page-message");
    } catch (error) { message("page-message", errorText(error), "error", true); }
    finally { busy(false); }
  }
  void start();
})();
