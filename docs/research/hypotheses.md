# Hypotheses Register

## 1. Purpose

Tài liệu này quản lý các claim chưa được coi là fact. Mỗi hypothesis phải được kiểm chứng bằng evidence phù hợp trước khi dùng để mở rộng scope, đưa ra market claim hoặc bảo vệ kết luận nghiên cứu.

### Status vocabulary

- **Strong hypothesis:** Có rationale ban đầu nhưng chưa đủ evidence để coi là validated.
- **Needs validation:** Cần nghiên cứu thêm trước khi dựa vào claim.
- **Key product hypothesis:** Nếu sai, target user hoặc delivery model có thể cần pivot.
- **Future validation:** Không cần giải quyết trước prototype v0.1.
- **Validated / Rejected / Revised:** Chỉ cập nhật khi có evidence và ghi rõ nguồn.

## H1 — Vietnam regulatory mapping gap

**Hypothesis:** Organizations may require an additional mapping layer between international cybersecurity frameworks and Vietnam-specific regulatory requirements.

**Current status:** Strong hypothesis; not validated.

**Why it matters:** Đây là cơ sở cho Requirement → Control → Evidence traceability.

**Validation approach:**

- Chọn một tập requirement đã được legal review.
- Thử mapping sang selected controls trong ISO/NIST/CIS.
- Ghi nhận trường hợp one-to-many, many-to-one hoặc không có direct mapping.
- Nhờ reviewer có chuyên môn đánh giá completeness và reasoning.

**Evidence required:** Reviewed mapping set, mapping rationale, reviewer feedback và unresolved cases.

**Decision if unsupported:** Thu hẹp claim thành một curated mapping cho selected requirements thay vì một general Vietnam regulatory layer.

## H2 — Global GRC localization gap

**Hypothesis:** Global GRC platforms may require custom configuration, custom controls, local expertise or manual mapping to represent selected Vietnamese cybersecurity/data requirements.

**Current status:** Needs validation.

**Why it matters:** Ảnh hưởng tới differentiation và build-versus-configure argument.

**Validation approach:**

- Chọn tiêu chí so sánh trước khi review platform.
- Kiểm tra documentation và, nếu khả thi, product demonstration/trial.
- Đánh giá platform-by-platform; không khái quát từ một ví dụ.

**Evidence required:** Comparison matrix, source links, version/date và limitations.

**Decision if unsupported:** Định vị prototype như research/education implementation hoặc SME workflow specialization, không claim localization gap của toàn thị trường.

## H3 — Data mapping pain point

**Hypothesis:** Data inventory and data-flow discovery may be among the most resource-intensive readiness activities because data is distributed across departments, SaaS, cloud, vendors and applications.

**Current status:** Needs interview/testing validation.

**Why it matters:** Ảnh hưởng tới onboarding workflow và effort của assessment.

**Validation approach:**

- Phỏng vấn SME/consultant theo cùng interview guide.
- Quan sát hoặc mô phỏng data-mapping task.
- Ghi nhận time, handoffs, missing information và rework.

**Evidence required:** Interview notes, coded themes, task observations và limitations.

**Decision if unsupported:** Giảm độ sâu data mapping trong MVP và tập trung vào requirement/control/evidence traceability.

## H4 — SME guided self-assessment need

**Hypothesis:** Vietnamese SMEs may benefit from a lower-cost guided self-assessment platform instead of immediately deploying enterprise GRC solutions.

**Current status:** Key product hypothesis requiring validation.

**Why it matters:** Đây là giả thuyết quan trọng nhất về primary user và delivery model.

**Validation approach:**

- Phỏng vấn SME về current workflow, willingness, skills và trust barriers.
- Test prototype tasks với representative users.
- So sánh self-service và consultant-assisted completion.

**Evidence required:** User interviews, task completion observations, error/help patterns và willingness-to-use signals. Không suy ra willingness-to-pay nếu chưa nghiên cứu riêng.

**Decision if unsupported:** Pivot từ SME self-service sang consultant-assisted SME assessment mà vẫn giữ core domain model.

## H5 — Continuous readiness value

**Hypothesis:** Organizations may receive more value from continuous evidence tracking than from one-time compliance assessment reports.

**Current status:** Future validation required.

**Why it matters:** Ảnh hưởng tới lifecycle, reminders, evidence freshness và product positioning.

**Validation approach:**

- Xác định evidence nào thay đổi theo thời gian.
- Mô phỏng expiry/update events trong synthetic scenario.
- Phỏng vấn users về recurring review và pain points.

**Evidence required:** Evidence lifecycle cases, user feedback và comparison with one-time reporting.

**Decision if unsupported:** Giữ prototype như point-in-time readiness assessment; không đầu tư continuous monitoring trong v0.1.

## H6 — Product differentiator

> **Đề xuất cấu trúc mới:** H6 tách claim đã có trong phần “Key Product Differentiator Hypothesis” thành một hypothesis có thể kiểm chứng; không phải fact mới.

**Hypothesis:** The combination of Vietnamese requirement mapping, security controls, evidence and continuous readiness provides meaningful differentiation for the selected users.

**Current status:** Needs validation after H1, H2, H4 and H5.

**Validation approach:** Market comparison plus user testing of the integrated workflow.

**Decision rule:** Không sử dụng claim “unique” hoặc “no existing solution” nếu comparison không chứng minh được.

## Validation priority

1. **H4** — quyết định self-service hay consultant-assisted.
2. **H1** — quyết định feasibility/value của regulatory mapping.
3. **H3** — định hình onboarding và data-discovery scope.
4. **H2** — kiểm tra differentiation against existing platforms.
5. **H5** — quyết định point-in-time hay continuous workflow.
6. **H6** — chỉ đánh giá sau khi có kết quả từ các hypothesis phụ thuộc.

## Update template

```markdown
### Validation update — YYYY-MM-DD

- Evidence collected:
- Source / participant / experiment:
- Finding:
- Limitations:
- Status change:
- Product or scope decision:
```

