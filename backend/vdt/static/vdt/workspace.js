"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const labels = {systems:"Hệ thống", assets:"Tài sản", "data-assets":"Dữ liệu"};
  const knownFields = {systems:{purpose:"Mục đích",hosting:"Nơi vận hành",exposure:"Phạm vi truy cập",criticality:"Mức độ quan trọng"},assets:{business_value:"Giá trị đối với hoạt động"},"data-assets":{sensitivity:"Mức độ nhạy cảm",record_scope:"Phạm vi dữ liệu"}};
  let setup, branch, catalog = {}, busy = false, inventoryEdit = null, scenarioEdit = null, contextSaved = null, preview = null;
  const retries = new Map();
  const el = (tag,text,cls) => { const n=document.createElement(tag); if(text!==undefined)n.textContent=text; if(cls)n.className=cls; return n; };
  const notice = (text,error=false) => { $("message").textContent=text; $("message").hidden=!text; $("message").className="message "+(error?"error":"notice"); };
  async function api(path,options={}) {
    const response=await fetch(path,{credentials:"same-origin",cache:"no-store",...options,headers:{Accept:"application/json",...options.headers}});
    const data=await response.json().catch(()=>null);
    if(!response.ok){ if(response.status===401||data?.code==="PASSWORD_CHANGE_REQUIRED")location.replace("/"); throw new Error(data?.detail||data?.title||"Không tải hoặc lưu được hồ sơ. Hãy thử lại."); }
    return data;
  }
  async function write(path,body,version,method="POST") {
    const signature=JSON.stringify({path,body,version,method});
    if(!retries.has(signature))retries.set(signature,crypto.randomUUID());
    const csrf=(await api("/api/v1/auth/csrf")).csrf_token;
    const data=await api(path,{method,headers:{"Content-Type":"application/json","X-CSRFToken":csrf,"Idempotency-Key":retries.get(signature),...(version?{"If-Match":`"${version}"`}:{})},body:JSON.stringify(body)});
    retries.delete(signature);return data;
  }
  async function task(work) {
    if(busy)return; busy=true;
    $("workspace-branch").disabled=true;$("inventory-kind").disabled=true;
    document.querySelectorAll("main button").forEach(b=>b.disabled=true);
    document.querySelectorAll(".editor-card").forEach(n=>n.inert=true);
    try {await work();}catch(error){notice(error.message,true);}
    finally {busy=false;$("workspace-branch").disabled=false;$("inventory-kind").disabled=false;document.querySelectorAll("main button").forEach(b=>b.disabled=false);document.querySelectorAll(".editor-card").forEach(n=>n.inert=false);}
  }
  async function pages(kind) {
    const rows=[],seen=new Set();let cursor=null;
    do {const page=await api(`/api/v1/${kind}?limit=200${cursor?"&cursor="+encodeURIComponent(cursor):""}`);rows.push(...page.items);cursor=page.next_cursor;if(cursor&&seen.has(cursor))throw new Error("Không tải được đầy đủ danh sách.");if(cursor)seen.add(cursor);}while(cursor);
    return rows;
  }
  async function load() {
    const previous=branch?.id;
    const results=await Promise.all([api("/api/v1/workspace/setup"),...Object.keys(labels).map(pages),pages("scenarios")]);
    setup=results[0];catalog={systems:results[1],assets:results[2],"data-assets":results[3],scenarios:results[4]};
    $("workspace-branch").replaceChildren(...setup.branches.map(b=>{const option=el("option",`${b.name} (${b.code})`);option.value=b.id;return option;}));
    branch=setup.branches.find(b=>b.id===previous)||setup.branches[0];
    if(!branch)throw new Error("Chưa có chi nhánh đủ quyền chuẩn bị hồ sơ. Quản trị viên cần kiểm tra phạm vi đã cấp.");
    $("workspace-branch").value=branch.id;
    renderRows();
  }
  const inBranch = (kind,active=false) => (catalog[kind]||[]).filter(r=>r.scope.branch_ids.includes(branch?.id)&&(!active||r.state==="ACTIVE"));
  const scope = () => ({organization_id:setup.organization.id,branch_ids:[branch.id],system_ids:[],asset_ids:[],data_asset_ids:[],scenario_ids:[],assessment_ids:[]});
  const dependency = (kind,data) => ({resource_type:kind,id:data.id,version:data.version});
  function dependencies(reason,objects=[],ownerId=null) {
    const rows=[dependency("organization",setup.organization),dependency("branch",branch),...objects.map(([kind,row])=>dependency(kind,row))];
    if(ownerId){const person=branch.owners.find(p=>p.id===ownerId);if(!person)throw new Error("Cần chọn lại người phụ trách đang hoạt động.");rows.push(dependency("user",person));}
    return {dependencies:[...new Map(rows.map(r=>[r.resource_type+":"+r.id,r])).values()],reason};
  }
  function source(prefix) {return {kind:$(prefix+"-source-kind").value,reference:$(prefix+"-source").value.trim(),reason:$(prefix+"-reason").value.trim(),evidence_revision_id:null,verification_decision_id:null};}
  function sourceFill(prefix,sources,reason="") {const s=sources?.[0];$(prefix+"-source-kind").value=s?.kind||"DOCUMENT";$(prefix+"-source").value=s?.reference||"";$(prefix+"-reason").value=reason;}
  function ownerOptions(id,selected="") {$(id).replaceChildren(el("option","Chưa chọn người phụ trách"),...branch.owners.map(p=>{const o=el("option",p.name);o.value=p.id;return o;}));$(id).options[0].value="";$(id).value=selected;}
  function knownInputs(container,prefix,fields,values={}) {
    $(container).replaceChildren(...Object.entries(fields).map(([key,label])=>{
      const row=el("div",undefined,"known-row"), stateField=el("div",undefined,"field"), labelNode=el("label",label), select=el("select");
      const id=`${prefix}-${key}`;labelNode.htmlFor=id+"-state";select.id=id+"-state";
      for(const [value,text] of [["UNKNOWN","Chưa xác định"],["KNOWN","Đã biết — có nguồn ghi nhận"]]){const o=el("option",text);o.value=value;select.append(o);}
      select.value=values[key]?.state||"UNKNOWN";stateField.append(labelNode,select);
      const valueField=el("div",undefined,"field"), valueLabel=el("label","Nội dung"),input=el("textarea");valueLabel.htmlFor=id+"-value";input.id=id+"-value";input.rows=2;input.maxLength=4000;input.value=values[key]?.value||"";valueField.append(valueLabel,input);
      const reasonField=el("div",undefined,"field"),reasonLabel=el("label","Lý do chưa xác định"),reason=el("input");reasonLabel.htmlFor=id+"-reason";reason.id=id+"-reason";reason.maxLength=4000;reason.value=values[key]?.state==="UNKNOWN"?values[key].reason:"";reasonField.append(reasonLabel,reason);
      const toggle=()=>{const known=select.value==="KNOWN";valueField.hidden=!known;input.required=known;input.disabled=!known;reasonField.hidden=known;reason.required=!known;reason.disabled=known;};
      select.addEventListener("change",toggle);toggle();row.append(stateField,valueField,reasonField);return row;
    }));
  }
  function knownValue(prefix,key,s) {const id=`${prefix}-${key}`,known=$(id+"-state").value==="KNOWN";return {state:known?"KNOWN":"UNKNOWN",value:known?$(id+"-value").value.trim():null,reason:known?s.reason:$(id+"-reason").value.trim(),sources:known?[s]:[]};}
  function choices(container,rows,name,selected=[],fixed=[]) {
    container.replaceChildren(...rows.map(row=>{const label=el("label",undefined,"choice"),input=el("input");input.type="checkbox";input.name=name;input.value=row.id;input.checked=selected.includes(row.id);input.disabled=fixed.includes(row.id);label.append(input,el("span",`${row.name} (${row.code})`));return label;}));
    if(!rows.length)container.append(el("p","Chưa có đối tượng phù hợp.","field-help"));
  }
  const checked = (name) => [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(n=>n.value).sort();
  const stateLabel = (value) => ({ACTIVE:"Đang sử dụng",DRAFT:"Nháp",RETIRED:"Ngừng sử dụng"}[value]||value);
  function rowTitle(row) {const td=el("td");td.append(el("span",row.code,"cell-main"),el("span",row.name,"cell-sub"));return td;}
  function button(text,handler){const b=el("button",text,"row-button");b.type="button";b.addEventListener("click",()=>void task(handler));return b;}
  function renderRows() {
    const kind=$("inventory-kind").value, rows=inBranch(kind);
    $("inventory-rows").replaceChildren(...rows.map(row=>{const tr=el("tr"),actions=el("td");actions.append(button("Xem / sửa",async()=>{const fresh=await api(`/api/v1/${kind}/${row.id}`);editInventory(fresh);notice("");}));tr.append(rowTitle(row),el("td",stateLabel(row.state)),actions);return tr;}));$("inventory-empty").hidden=!!rows.length;
    const scenarios=inBranch("scenarios");$("scenario-rows").replaceChildren(...scenarios.map(row=>{const tr=el("tr"),actions=el("td");actions.append(button("Mở",()=>openScenario(row.id)));tr.append(rowTitle(row),el("td",stateLabel(row.state)),actions);return tr;}));$("scenario-empty").hidden=!!scenarios.length;
  }
  function editInventory(data=null) {
    inventoryEdit=data;const kind=$("inventory-kind").value;
    $("inventory-form").reset();$("inventory-title").textContent=labels[kind]+(data?" · cập nhật":" mới");
    $("inventory-code").value=data?.code||"";$("inventory-name").value=data?.name||"";$("inventory-state").value=data?.state||"ACTIVE";
    ownerOptions("inventory-owner",data?.owner_id||"");$("asset-type-field").hidden=kind!=="assets";$("asset-type").value=data?.asset_type||"APPLICATION";
    const relatedKind=kind==="systems"?"assets":"systems",key=kind==="systems"?"asset_ids":"system_ids";
    $("inventory-links-title").textContent=kind==="systems"?"Tài sản liên quan":"Thuộc hệ thống";
    choices($("inventory-link-options"),inBranch(relatedKind),"inventory-links",data?.[key]||[],data?.[key]||[]);
    knownInputs("inventory-known","inventory",knownFields[kind],data||{});sourceFill("inventory",data?.sources);
  }
  $("inventory-form").addEventListener("submit",event=>{event.preventDefault();if(!event.currentTarget.reportValidity())return;void task(async()=>{
    const kind=$("inventory-kind").value,s=source("inventory"),ownerId=$("inventory-owner").value||null;
    const body={code:$("inventory-code").value.trim(),name:$("inventory-name").value.trim(),owner_id:ownerId,scope:scope(),state:$("inventory-state").value,sources:[s]};
    for(const key of Object.keys(knownFields[kind]))body[key]=knownValue("inventory",key,s);
    const ids=checked("inventory-links"),relatedKind=kind==="systems"?"assets":"systems",resource=kind==="systems"?"asset":"system";
    const objects=ids.map(id=>[resource,catalog[relatedKind].find(r=>r.id===id)]);
    if(kind==="systems"){body.asset_ids=ids;body.vendor_ids=[];}else{body.system_ids=ids;if(kind==="assets")body.asset_type=$("asset-type").value;}
    body.write_context=dependencies(s.reason,objects,ownerId);
    await write(`/api/v1/${kind}${inventoryEdit?"/"+inventoryEdit.id:""}`,body,inventoryEdit?.version,inventoryEdit?"PATCH":"POST");
    await load();editInventory();resetScenario();notice("Đã lưu hồ sơ và lịch sử thay đổi.");
  });});
  function contextChoices() {
    $("context-selections").replaceChildren(...Object.keys(labels).map(kind=>{const group=el("fieldset"),legend=el("legend",labels[kind]),list=el("div",undefined,"choice-list");group.append(legend,list);choices(list,inBranch(kind,true),"context-"+kind);return group;}));
  }
  function resetScenario() {
    scenarioEdit=null;contextSaved=null;preview=null;$("scenario-form").reset();$("context-form").reset();$("scenario-preview").hidden=true;$("scenario-title").textContent="Kịch bản mới";$("scenario-save").textContent="Lưu bản nháp";$("context-inputs").disabled=false;$("context-save").hidden=false;$("context-form").hidden=false;$("context-saved").hidden=true;$("scenario-inputs").disabled=true;ownerOptions("scenario-owner");contextChoices();
    knownInputs("context-known","context",{environment:"Môi trường đánh giá",preconditions:"Điều kiện tiên quyết",adversary_capability:"Khả năng của tác nhân gây rủi ro"});
  }
  function showContext(context) {
    contextSaved=context;$("context-inputs").disabled=true;$("context-save").hidden=true;$("scenario-inputs").disabled=false;$("context-saved").hidden=false;
    const value=k=>context[k].state==="KNOWN"?context[k].value:"Chưa xác định: "+context[k].reason;
    $("context-saved").textContent=`Bối cảnh đã lưu lúc ${new Date(context.created_at).toLocaleString("vi-VN")}.\nMôi trường: ${value("environment")}\nThông tin này được giữ nguyên trong hồ sơ. Bạn có thể tiếp tục mô tả kịch bản.`;
  }
  $("context-form").addEventListener("submit",event=>{event.preventDefault();if(!event.currentTarget.reportValidity())return;void task(async()=>{
    const s=source("context"),systems=checked("context-systems"),assets=checked("context-assets"),dataAssets=checked("context-data-assets");
    if(!systems.length&&!assets.length)throw new Error("Chọn ít nhất một hệ thống hoặc tài sản.");
    const body={scope:{...scope(),system_ids:systems,asset_ids:assets,data_asset_ids:dataAssets},system_ids:systems,asset_ids:assets,data_asset_ids:dataAssets,vendor_ids:[],data_flow_ids:[],sources:[s],preconditions:[knownValue("context","preconditions",s)],environment:knownValue("context","environment",s),adversary_capability:knownValue("context","adversary_capability",s)};
    const objects=[["systems",systems,"system"],["assets",assets,"asset"],["data-assets",dataAssets,"data_asset"]].flatMap(([kind,ids,type])=>ids.map(id=>[type,catalog[kind].find(r=>r.id===id)]));
    body.write_context=dependencies(s.reason,objects);showContext(await write("/api/v1/context-snapshots",body));notice("Đã lưu bối cảnh. Điền mô tả để tạo kịch bản.");
  });});
  function scenarioObjects(context) {return [["systems","system_ids","system"],["assets","asset_ids","asset"],["data-assets","data_asset_ids","data_asset"]].flatMap(([kind,key,type])=>context.scope[key].map(id=>{const data=catalog[kind].find(r=>r.id===id);if(!data)throw new Error("Không còn quyền đọc đủ đối tượng của kịch bản.");return [type,data];}));}
  $("scenario-form").addEventListener("submit",event=>{event.preventDefault();if(!event.currentTarget.reportValidity()||!contextSaved)return;void task(async()=>{
    const s=source("scenario"),ownerId=$("scenario-owner").value||null;
    const body={code:$("scenario-code").value.trim(),name:$("scenario-name").value.trim(),event:$("scenario-event").value.trim(),consequences:$("scenario-consequences").value.trim(),owner_id:ownerId,context_snapshot_id:contextSaved.id,scope:contextSaved.scope,attack_metadata:[],sources:[s],write_context:dependencies(s.reason,scenarioObjects(contextSaved),ownerId)};
    const result=await write("/api/v1/scenarios"+(scenarioEdit?"/"+scenarioEdit.id:""),body,scenarioEdit?.version,scenarioEdit?"PATCH":"POST");
    await load();resetScenario();await openScenario(result.id);notice("Đã lưu kịch bản. Kiểm tra nội dung rồi chuyển sang Đang sử dụng để thêm vào đợt.");
  });});
  async function openScenario(id) {
    const item=await api("/api/v1/scenarios/"+id),snapshot=await api("/api/v1/scenario-snapshots/"+item.current_scenario_snapshot_id),ctx=await api("/api/v1/context-snapshots/"+item.context_snapshot_id);
    scenarioEdit=item;preview=item;showContext(ctx);$("context-form").hidden=true;$("scenario-title").textContent="Cập nhật kịch bản";$("scenario-save").textContent="Lưu cập nhật";
    for(const key of ["code","name","event","consequences"])$("scenario-"+key).value=item[key];ownerOptions("scenario-owner",item.owner_id||"");sourceFill("scenario",snapshot.sources);
    $("scenario-inputs").disabled=item.state==="RETIRED";$("scenario-preview").hidden=false;$("preview-title").textContent=item.name;
    const fields=[["Trạng thái",stateLabel(item.state)],["Sự kiện",item.event],["Hậu quả",item.consequences],["Môi trường",ctx.environment.value||"Chưa xác định — "+ctx.environment.reason],["Điều kiện",ctx.preconditions.map(p=>p.value||"Chưa xác định — "+p.reason).join("; ")]];
    const box=el("div",undefined,"preview-facts");for(const [label,value] of fields){const p=el("p");p.append(el("strong",label),el("span",value));box.append(p);}$("preview-content").replaceChildren(box);
    $("transition-form").hidden=item.state==="RETIRED";$("transition-state").value=item.state==="DRAFT"?"ACTIVE":"RETIRED";$("transition-reason").value="";
  }
  $("transition-form").addEventListener("submit",event=>{event.preventDefault();if(!event.currentTarget.reportValidity()||!preview)return;void task(async()=>{
    const body={state:$("transition-state").value,write_context:dependencies($("transition-reason").value.trim(),scenarioObjects(contextSaved),preview.owner_id)};
    const result=await write(`/api/v1/scenarios/${preview.id}/transitions`,body,preview.version);await load();await openScenario(result.id);notice("Đã cập nhật trạng thái. Kịch bản đang sử dụng có thể được thêm từ hồ sơ đợt đánh giá.");
  });});
  function tab(name) {$("inventory-section").hidden=name!=="inventory";$("scenarios-section").hidden=name!=="scenarios";for(const value of ["inventory","scenarios"]){$("tab-"+value).className="button button-"+(value===name?"primary":"secondary");$("tab-"+value).setAttribute("aria-pressed",String(value===name));}}
  $("tab-inventory").addEventListener("click",()=>tab("inventory"));$("tab-scenarios").addEventListener("click",()=>tab("scenarios"));
  $("inventory-kind").addEventListener("change",()=>{renderRows();editInventory();});
  $("workspace-branch").addEventListener("change",()=>{branch=setup.branches.find(b=>b.id===$("workspace-branch").value);editInventory();resetScenario();renderRows();notice("");});
  $("inventory-reset").addEventListener("click",()=>editInventory());$("scenario-reset").addEventListener("click",resetScenario);
  $("reload").addEventListener("click",()=>void task(async()=>{await load();editInventory();resetScenario();notice("Đã tải lại danh mục. Các form đã trở về hồ sơ mới.");}));
  window.addEventListener("pageshow",event=>{if(event.persisted)location.reload();});
  void task(async()=>{await load();editInventory();resetScenario();notice("");});
})();
