"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let session, csrf = "", organization, items = [], busy = false, retry = null, detailEpoch = 0;
  let presentation = new Map();
  let detailData = null, candidates = [], linkRetry = null;
  const element = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const api = async (url, options = {}) => {
    const response = await fetch(url, { credentials: "same-origin", cache: "no-store", ...options, headers: { Accept: "application/json", ...options.headers } });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      if (response.status === 401 || data?.code === "PASSWORD_CHANGE_REQUIRED") location.replace("/");
      throw { status: response.status, detail: data?.detail || data?.title, code: data?.code };
    }
    if (url === "/api/v1/auth/session") data.password_change_required = response.headers.get("X-VDT-Password-Change-Required") === "true";
    return data;
  };
  const notice = (value, error = false) => {
    $("message").textContent = value;
    $("message").className = "message " + (error ? "error" : "notice");
    $("message").hidden = !value;
  };
  const errorText = (error) => error?.detail || "Không tải hoặc lưu được dữ liệu. Hãy thử lại.";
  const setBusy = (value) => {
    busy = value;
    document.querySelectorAll("main button").forEach((button) => { button.disabled = value; });
    $("create").setAttribute("aria-busy", String(value));
  };
  const clearDetail = () => {
    detailEpoch += 1;
    $("assessment-detail").hidden = true;
    detailData = null; candidates = [];
    $("dossier-items").replaceChildren(); $("scenario-link-card").hidden = true;
    $("scenario-link-form").reset();
    for (const id of ["detail-title","detail-access","detail-code","detail-branches","detail-state","detail-updated","detail-scenarios","detail-expiry","detail-preparation"]) $(id).textContent = "";
  };
  const page = async (name) => {
    const rows = [], seen = new Set(); let cursor = null;
    do {
      const result = await api("/api/v1/" + name + "?limit=200" + (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""));
      if (!Array.isArray(result?.items)) throw { detail: "Danh sách trả về không hợp lệ." };
      rows.push(...result.items); cursor = result.next_cursor;
      if (cursor && seen.has(cursor)) throw { detail: "Không tải được đầy đủ danh sách." };
      if (cursor) seen.add(cursor);
    } while (cursor);
    return rows;
  };
  const branchName = (branch) => `${branch.name} (${branch.code})${branch.active ? "" : " · không hoạt động"}`;
  const readableTime = (value) => {
    const date = new Date(value);
    return value && !Number.isNaN(date.getTime()) ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium", timeStyle: "short" }).format(date) : "Chưa xác định";
  };
  async function openDetail(id) {
    if (busy) return;
    clearDetail(); const epoch = detailEpoch;
    notice("Đang mở hồ sơ…");
    try {
      const [data, display, dossier] = await Promise.all([api("/api/v1/assessments/" + id), api("/api/v1/assessments/" + id + "/display-context"), api("/api/v1/assessments/" + id + "/dossier")]);
      if (epoch !== detailEpoch) return;
      const permissions = display.access_permissions;
      detailData = dossier.assessment;
      const roles = [];
      if (permissions.includes("assessment.run")) roles.push("Người đánh giá");
      if (permissions.includes("assessment.review")) roles.push("Consultant / Người thẩm định");
      if (!roles.length) roles.push("Người xem đánh giá");
      $("detail-title").textContent = data.name;
      $("detail-access").textContent = "Quyền của bạn trong đợt này: " + roles.join(" · ");
      $("detail-code").textContent = data.code;
      $("detail-branches").textContent = display.branches.map(branchName).join(", ") || "Chưa gắn chi nhánh";
      $("detail-state").textContent = data.state === "OPEN" ? "Đang mở" : "Đã lưu trữ";
      $("detail-updated").textContent = readableTime(data.updated_at);
      $("detail-scenarios").textContent = data.scenario_ids.length ? String(data.scenario_ids.length) : "Chưa gắn kịch bản";
      $("detail-expiry-row").hidden = !permissions.includes("assessment.review");
      $("detail-expiry").textContent = readableTime(display.review_access_expires_at);
      $("detail-preparation").textContent = data.scenario_ids.length
        ? "Đợt đã có kịch bản. Công việc thẩm định tiếp theo cần hồ sơ bằng chứng và bản kết quả đánh giá cụ thể."
        : "Đợt này mới có thông tin phạm vi. Người phụ trách cần bổ sung kịch bản, bằng chứng và bản kết quả đánh giá trước khi gửi thẩm định.";
      renderDossier(dossier);
      if (permissions.includes("assessment.run") && data.state === "OPEN") {
        const available = await page("scenarios");
        if (epoch !== detailEpoch) return;
        candidates = available.filter(s => s.state === "ACTIVE" && !detailData.scenario_ids.includes(s.id) && s.scope.branch_ids.every(branch => data.scope.branch_ids.includes(branch)));
        $("scenario-link-choice").replaceChildren(...candidates.map(s => { const option=element("option",s.name+" ("+s.code+")");option.value=s.id;return option; }));
        $("scenario-link-card").hidden=false;$("scenario-link-form").hidden=!candidates.length;$("scenario-link-empty").hidden=!!candidates.length;
      }
      $("assessment-detail").hidden = false;
      $("detail-title").focus({ preventScroll: true });
      $("assessment-detail").scrollIntoView({ block: "start", behavior: "smooth" });
      notice("");
    } catch (error) {
      if (epoch !== detailEpoch) return;
      clearDetail(); notice(errorText(error), true);
    }
  }
  const render = () => {
    $("items").replaceChildren(...items.map((item) => {
      const tr = element("tr"), title = element("td");
      title.append(element("span",item.code,"cell-main"),element("span",item.name,"cell-sub"));
      const branches = element("td");
      presentation.get(item.id).branches.forEach((branch) => branches.append(element("span",branchName(branch),"branch-label")));
      const state = element("td"); state.append(element("span",item.state === "OPEN" ? "Đang mở" : "Đã lưu trữ","status-badge"));
      const action = element("td"), open = element("button","Mở hồ sơ","row-button");
      open.type = "button"; open.disabled = busy; open.setAttribute("aria-label","Mở hồ sơ " + item.code);
      open.addEventListener("click",() => void openDetail(item.id)); action.append(open);
      tr.append(title,branches,state,action); return tr;
    }));
    $("empty").hidden = items.length > 0;
  };
  const load = async () => {
    clearDetail(); items = []; presentation.clear(); $("items").replaceChildren(); $("empty").hidden = true;
    session = await api("/api/v1/auth/session");
    if (session.password_change_required || !session.permissions.some((p) => ["assessment.run","assessment.review","report.read"].includes(p))) {
      location.replace("/"); return;
    }
    const canCreate = session.permissions.includes("assessment.run");
    $("workspace-link").hidden = !canCreate;
    $("create-card").hidden = !canCreate;
    $("assessment-workspace").classList.toggle("read-only", !canCreate);
    const [rows, labels, setup] = await Promise.all([
      page("assessments"), page("assessments/display-context"), canCreate ? api("/api/v1/assessments/setup") : Promise.resolve(null)
    ]);
    presentation = new Map(labels.map((item) => [item.id,item]));
    // Requests each recheck authority; intersect their results if access changed.
    items = rows.filter((item) => presentation.has(item.id));
    if (setup) {
      organization = setup.organization; const selected = $("branch").value;
      $("branch").replaceChildren(...setup.branches.map((branch) => { const option = element("option",branch.name); option.value = branch.id; return option; }));
      if (setup.branches.some((branch) => branch.id === selected)) $("branch").value = selected;
    }
    render();
  };
  $("create").addEventListener("submit", async (event) => {
    event.preventDefault(); if (busy || !organization || !event.currentTarget.reportValidity()) return;
    const form = event.currentTarget;
    const scope = { organization_id: organization.id, branch_ids: [$("branch").value], system_ids: [], asset_ids: [], data_asset_ids: [], scenario_ids: [], assessment_ids: [] };
    const body = { code: $("code").value.trim(), name: $("name").value.trim(), scenario_ids: [], scope,
      write_context: { dependencies: [{ resource_type: "organization", id: organization.id, version: organization.version }], reason: $("reason").value.trim() } };
    const signature = JSON.stringify(body);
    if (!retry || retry.signature !== signature) retry = { signature, key: crypto.randomUUID() };
    setBusy(true);
    try {
      if (!csrf) csrf = (await api("/api/v1/auth/csrf")).csrf_token;
      await api("/api/v1/assessments", { method: "POST", headers: { "Content-Type": "application/json", "X-CSRFToken": csrf, "Idempotency-Key": retry.key }, body: signature });
      retry = null; form.reset(); await load(); notice("Đã tạo đợt đánh giá. Bấm Mở hồ sơ để xem thông tin và phạm vi.");
    } catch (error) { notice(errorText(error), true); }
    finally { setBusy(false); }
  });
  async function refresh(initial = false) {
    if (busy) return; setBusy(true); notice("Đang tải dữ liệu…");
    try { await load(); notice(initial ? "" : "Đã làm mới danh sách."); }
    catch (error) { notice(errorText(error), true); }
    finally { setBusy(false); }
  }
  $("refresh").addEventListener("click",() => void refresh());
  $("close-detail").addEventListener("click",() => { clearDetail(); $("refresh").focus(); });
  const knownText = value => value.state === "KNOWN" ? value.value : "Chưa xác định — " + value.reason;
  function renderDossier(dossier) {
    $("dossier-empty").hidden = !!dossier.items.length; $("dossier-restricted").hidden = !dossier.restricted;
    $("dossier-items").replaceChildren(...dossier.items.map(item => {
      const card=element("article",undefined,"dossier-entry"), s=item.scenario, ctx=item.context;
      card.append(element("h4",s.code+" · "+s.name));
      const dl=element("dl");
      const fields=[["Người phụ trách khi lưu",item.owner_name||"Chưa chọn"],["Sự kiện",s.event],["Hậu quả",s.consequences],
        ["Môi trường",knownText(ctx.environment)],["Điều kiện tiên quyết",ctx.preconditions.map(knownText).join("\n")],
        ["Khả năng tác nhân",knownText(ctx.adversary_capability)],["Phiên bản được lưu trong đợt","Lần lưu "+s.revision_number+" · "+readableTime(s.created_at)],
        ["Nguồn kịch bản",s.sources.map(x=>x.reference+" — "+x.reason+(x.kind==="ASSUMPTION"?" (giả định)":x.kind==="TEMPLATE"?" (mẫu tham khảo)":"")).join("\n")||"Chưa ghi nguồn"]];
      for (const [label,value] of fields) dl.append(element("dt",label),element("dd",value));card.append(dl);
      const details=element("details");details.append(element("summary","Hệ thống, tài sản và dữ liệu tại lúc lưu bối cảnh"));
      const names={purpose:"Mục đích",hosting:"Nơi vận hành",exposure:"Phạm vi truy cập",criticality:"Mức độ quan trọng",business_value:"Giá trị hoạt động",sensitivity:"Mức độ nhạy cảm",record_scope:"Phạm vi dữ liệu"};
      for(const kind of ["systems","assets","data-assets"])for(const row of item.inventory[kind]){
        const block=element("div",undefined,"inventory-record");block.append(element("strong",row.name+" ("+row.code+")"));
        for(const [key,label] of Object.entries(names))if(row[key])block.append(element("p",label+": "+knownText(row[key])));
        details.append(block);
      }
      card.append(details);return card;
    }));
  }
  $("scenario-link-form").addEventListener("submit",async event => {
    event.preventDefault();if(busy||!detailData||!event.currentTarget.reportValidity())return;
    const selected=candidates.find(s=>s.id===$("scenario-link-choice").value);if(!selected)return;
    const id=detailData.id,version=detailData.version;
    const body={scenario_id:selected.id,write_context:{reason:$("scenario-link-reason").value.trim(),dependencies:[{resource_type:"organization",id:organization.id,version:organization.version},{resource_type:"scenario",id:selected.id,version:selected.version}]}};
    const signature=JSON.stringify({id,version,body});if(!linkRetry||linkRetry.signature!==signature)linkRetry={signature,key:crypto.randomUUID()};
    setBusy(true);
    try {
      if(!csrf)csrf=(await api("/api/v1/auth/csrf")).csrf_token;
      await api(`/api/v1/assessments/${id}/scenario-links`,{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":csrf,"Idempotency-Key":linkRetry.key,"If-Match":`"${version}"`},body:JSON.stringify(body)});
      linkRetry=null;await load();setBusy(false);await openDetail(id);notice("Đã thêm kịch bản và giữ phiên bản vào hồ sơ đợt.");
    }catch(error){notice(errorText(error),true);}finally{setBusy(false);}
  });
  window.addEventListener("pageshow",(event) => { if (event.persisted) location.reload(); });
  void refresh(true);
})();
