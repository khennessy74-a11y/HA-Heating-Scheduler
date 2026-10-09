/* Heating Scheduler workflow preview. Strictly read-only: no write service calls. */
class HeatingSchedulerWorkflowPreview extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = null;
    this._rows = [];
    this._view = "control";
    this._selected = null;
    this._busy = false;
    this._error = "";
    this._request = 0;
  }
  setConfig(config) {
    if (!config || typeof config.entry_id !== "string" || !config.entry_id.trim())
      throw new Error("Provide a disposable Heating Scheduler entry_id");
    this._config = { entry_id: config.entry_id.trim() };
    this._rows = [];
    this._view = "control";
    this._selected = null;
    this._request++;
    this._draw();
    this._load();
  }
  set hass(hass) {
    this._hass = hass;
    if (!this._loaded && this._config) this._load();
  }
  getCardSize() { return Math.max(3, this._rows.length + 2); }
  async _load() {
    if (!this._hass || !this._config || this._busy) return;
    const id = this._config.entry_id, request = ++this._request;
    this._busy = true;
    this._error = "";
    this._draw();
    try {
      const result = await this._hass.callWS({
        type: "call_service", domain: "heating_scheduler",
        service: "list_schedules", service_data: { entry_id: id },
        return_response: true
      });
      if (request !== this._request || id !== this._config?.entry_id) return;
      const response = result?.response ?? result;
      if (response?.read_only !== true || !Array.isArray(response.items))
        throw new Error("Read-only schedule response unavailable");
      this._rows = response.items;
      this._loaded = true;
    } catch (err) {
      if (request === this._request) this._error = String(err?.message || err);
    } finally {
      if (request === this._request) {
        this._busy = false;
        this._draw();
      }
    }
  }
  _node(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value != null) node.textContent = String(value);
    return node;
  }
  _button(label, action, disabled = false) {
    const button = this._node("button", "", label);
    button.type = "button";
    button.disabled = disabled;
    if (!disabled) button.addEventListener("click", action);
    return button;
  }
  _draw() {
    if (!this._config) return;
    const root = this.shadowRoot;
    root.replaceChildren();
    const css = this._node("style");
    css.textContent = `
      ha-card { padding:16px; }
      .bar,.row { display:flex; align-items:center; justify-content:space-between; gap:12px; }
      .bar { margin-bottom:12px; flex-wrap:wrap; }
      .row { padding:13px 0; border-top:1px solid var(--divider-color); }
      .details { flex:1; min-width:0; text-align:left; }
      .name { font-weight:600; overflow-wrap:anywhere; }
      .sub,.muted { color:var(--secondary-text-color); font-size:13px; }
      .status { padding:5px 8px; border-radius:10px; background:var(--secondary-background-color); font-size:12px; }
      .enabled { color:var(--success-color, green); }
      button { padding:8px; border:1px solid var(--divider-color); border-radius:10px; background:transparent; color:var(--primary-text-color); }
      button:disabled { opacity:.45; cursor:not-allowed; }
      .form { display:grid; gap:12px; padding-top:12px; }
      fieldset { border:1px solid var(--divider-color); border-radius:10px; display:grid; grid-template-columns:repeat(auto-fit,minmax(65px,1fr)); gap:8px; }
      legend { font-weight:600; }
      label.day, label.enabledToggle { display:flex; align-items:center; gap:6px; }
      label.day input, label.enabledToggle input { width:auto; }
      label { display:grid; gap:4px; font-size:14px; }
      input,select { padding:8px; border-radius:8px; border:1px solid var(--divider-color); background:var(--card-background-color); color:var(--primary-text-color); width:100%; box-sizing:border-box; }
      .actions { display:flex; gap:8px; flex-wrap:wrap; }
      .notice { padding:8px 0; color:var(--secondary-text-color); font-size:13px; }
    `;
    const card = this._node("ha-card");
    const bar = this._node("div", "bar");
    const back = this._view !== "control"
      ? this._button("← Heating Control", () => { this._view = "control"; this._selected = null; this._draw(); })
      : this._node("strong", "", "Heating Control");
    bar.append(back);
    bar.append(this._button("Refresh", () => { this._loaded = false; this._load(); }, this._busy));
    card.append(bar);
    if (this._error) card.append(this._node("div", "notice", this._error));
    card.append(this._node("div", "notice", "Development preview · All schedule changes disabled"));
    if (this._view === "edit" || this._view === "add") this._drawForm(card);
    else if (this._view === "delete_preview") this._drawDeletePreview(card);
    else this._drawList(card);
    root.append(css, card);
  }
  _drawList(card) {
    if (this._view === "control") {
      const actions = this._node("div", "actions");
      actions.append(
        this._button("Manage Schedules", () => { this._view = "manage"; this._draw(); }),
        this._button("Add Schedule (preview)", () => { this._view = "add"; this._selected = null; this._draw(); })
      );
      card.append(actions);
    } else card.append(this._node("h3", "", "Manage Schedules"));
    if (this._busy && !this._rows.length) card.append(this._node("p", "muted", "Loading…"));
    if (!this._busy && !this._rows.length) card.append(this._node("p", "muted", "No schedules available"));
    for (const item of this._rows) {
      const row = this._node("div", "row");
      const details = this._button(item.title || "Unnamed", () => {
        this._selected = item;
        this._view = "edit";
        this._draw();
      });
      details.className = "details";
      const sub = this._node("div", "sub", item.subtitle || "Details unavailable");
      details.append(sub);
      row.append(details);
      if (this._view === "manage") {
        row.append(this._button("✎ Edit", () => {
          this._selected = item;
          this._view = "edit";
          this._draw();
        }));
        if (item.status === "Disabled" && item.can_delete_after_confirmation === true) {
          row.append(this._button("🗑 Review", () => {
            this._selected = item;
            this._view = "delete_preview";
            this._draw();
          }));
        }
      } else {
        row.append(this._node("span", "status " + (item.status === "Enabled" ? "enabled" : ""),
          ["Enabled", "Disabled", "Unknown"].includes(item.status) ? item.status : "Unknown"));
      }
      card.append(row);
    }
  }
  _drawDeletePreview(card) {
    card.append(this._node("h3", "", "Delete Schedule — confirmation preview"));
    const item = this._selected;
    // This screen intentionally has NO service call or confirm/delete handler.
    card.append(this._node("p", "", "Delete " + String(item?.title || "this schedule") + "?"));
    card.append(this._node("p", "notice",
      "Deletion is locked in this development build, even for disabled schedules."));
    const actions = this._node("div", "actions");
    actions.append(
      this._button("Cancel", () => {
        this._view = "manage";
        this._selected = null;
        this._draw();
      }),
      this._button("Confirm deletion — unavailable", () => {}, true)
    );
    card.append(actions);
  }
  _drawForm(card) {
    card.append(this._node("h3", "",
      this._view === "add" ? "Add Schedule — preview" : "Edit Schedule — preview"));
    const form = this._node("div", "form");
    const selected = this._selected;

    const field = (labelText, input) => {
      const label = this._node("label", "", labelText);
      input.disabled = true;
      input.setAttribute("aria-label", labelText);
      label.append(input);
      form.append(label);
    };
    const name = this._node("input");
    name.type = "text";
    name.value = selected?.title || "";
    field("Schedule name", name);

    const time = this._node("input");
    time.type = "time";
    // Unknown timing stays blank: never invent editable source data.
    time.value = selected?.start || "";
    field("Start time", time);

    const duration = this._node("select");
    const choice = selected?.minutes;
    const durations = [15, 30, 45, 60, 90, 120, 180, 240];
    const placeholder = this._node("option", "", "Select duration");
    placeholder.value = "";
    duration.append(placeholder);
    for (const minutes of durations) {
      const option = this._node("option", "", minutes + " minutes");
      option.value = String(minutes);
      duration.append(option);
    }
    duration.value = durations.includes(choice) ? String(choice) : "";
    field("Duration", duration);

    const weekdaySection = this._node("fieldset");
    weekdaySection.disabled = true;
    const legend = this._node("legend", "", "Weekdays");
    weekdaySection.append(legend);
    for (const [code, label] of [
      ["mon", "Mon"], ["tue", "Tue"], ["wed", "Wed"], ["thu", "Thu"],
      ["fri", "Fri"], ["sat", "Sat"], ["sun", "Sun"]
    ]) {
      const wrapper = this._node("label", "day");
      const checkbox = this._node("input");
      checkbox.type = "checkbox";
      checkbox.checked = Array.isArray(selected?.weekdays) && selected.weekdays.includes(code);
      checkbox.disabled = true;
      wrapper.append(checkbox, this._node("span", "", label));
      weekdaySection.append(wrapper);
    }
    form.append(weekdaySection);

    const enabledLabel = this._node("label", "enabledToggle");
    const toggle = this._node("input");
    toggle.type = "checkbox";
    toggle.disabled = true;
    toggle.checked = selected ? selected.enabled === true : true;
    enabledLabel.append(toggle, this._node("span", "", "Enabled"));
    form.append(enabledLabel);
    if (selected && selected.enabled == null)
      form.append(this._node("p", "notice", "Enabled state unknown"));

    form.append(this._node("p", "notice",
      "Preview only · All fields and Save are disabled. Unknown schedule values remain blank."));
    form.append(this._button("Save — unavailable", () => {}, true));
    card.append(form);
  }
}
if (!customElements.get("heating-scheduler-workflow-preview"))
  customElements.define("heating-scheduler-workflow-preview", HeatingSchedulerWorkflowPreview);
